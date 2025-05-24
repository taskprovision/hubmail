"""
Data Processors for Taskinity.

This module provides classes for processing data from various sources
such as CSV files, JSON files, and databases.
"""
import os
import csv
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Iterator, Callable

# Check if optional dependencies are installed
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import sqlalchemy
    from sqlalchemy import create_engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class DataProcessor(ABC):
    """Base class for data processors."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the data processor.
        
        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(__name__)
    
    @abstractmethod
    def read(self, source: Any, **kwargs) -> Any:
        """
        Read data from a source.
        
        Args:
            source: Data source
            **kwargs: Additional arguments
            
        Returns:
            Loaded data
        """
        pass
    
    @abstractmethod
    def write(self, data: Any, destination: Any, **kwargs) -> None:
        """
        Write data to a destination.
        
        Args:
            data: Data to write
            destination: Destination to write to
            **kwargs: Additional arguments
        """
        pass
    
    def transform(self, data: Any, transformer: Callable[[Any], Any]) -> Any:
        """
        Transform data using a transformer function.
        
        Args:
            data: Data to transform
            transformer: Transformer function
            
        Returns:
            Transformed data
        """
        self.logger.info("Transforming data")
        return transformer(data)
    
    def process(self, source: Any, destination: Any, transformer: Optional[Callable[[Any], Any]] = None, **kwargs) -> Any:
        """
        Process data from source to destination with optional transformation.
        
        Args:
            source: Data source
            destination: Data destination
            transformer: Transformer function (optional)
            **kwargs: Additional arguments
            
        Returns:
            Processed data
        """
        self.logger.info(f"Processing data from {source} to {destination}")
        
        # Read data
        data = self.read(source, **kwargs)
        
        # Transform data if transformer is provided
        if transformer:
            data = self.transform(data, transformer)
        
        # Write data
        self.write(data, destination, **kwargs)
        
        return data


class CSVProcessor(DataProcessor):
    """Processor for CSV files."""
    
    def read(self, source: Union[str, Path], **kwargs) -> List[Dict[str, Any]]:
        """
        Read data from a CSV file.
        
        Args:
            source: Path to CSV file
            **kwargs: Additional arguments for csv.DictReader
            
        Returns:
            List of dictionaries representing CSV rows
        """
        self.logger.info(f"Reading CSV from {source}")
        
        # Use pandas if available for better performance and features
        if PANDAS_AVAILABLE and kwargs.pop("use_pandas", True):
            df = pd.read_csv(source, **kwargs)
            return df.to_dict("records")
        
        # Fall back to standard library
        with open(source, 'r', newline='') as f:
            reader = csv.DictReader(f, **kwargs)
            return list(reader)
    
    def write(self, data: List[Dict[str, Any]], destination: Union[str, Path], **kwargs) -> None:
        """
        Write data to a CSV file.
        
        Args:
            data: List of dictionaries to write
            destination: Path to CSV file
            **kwargs: Additional arguments for csv.DictWriter
        """
        self.logger.info(f"Writing CSV to {destination}")
        
        # Use pandas if available for better performance and features
        if PANDAS_AVAILABLE and kwargs.pop("use_pandas", True):
            df = pd.DataFrame(data)
            df.to_csv(destination, index=kwargs.pop("include_index", False), **kwargs)
            return
        
        # Fall back to standard library
        if not data:
            self.logger.warning("No data to write")
            return
        
        fieldnames = kwargs.pop("fieldnames", list(data[0].keys()))
        
        with open(destination, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, **kwargs)
            writer.writeheader()
            writer.writerows(data)


class JSONProcessor(DataProcessor):
    """Processor for JSON files."""
    
    def read(self, source: Union[str, Path], **kwargs) -> Any:
        """
        Read data from a JSON file.
        
        Args:
            source: Path to JSON file or JSON string
            **kwargs: Additional arguments for json.load
            
        Returns:
            Loaded JSON data
        """
        self.logger.info(f"Reading JSON from {source}")
        
        # Check if source is a file path or a JSON string
        if isinstance(source, (str, Path)) and os.path.isfile(str(source)):
            with open(source, 'r') as f:
                return json.load(f, **kwargs)
        elif isinstance(source, str):
            try:
                return json.loads(source, **kwargs)
            except json.JSONDecodeError:
                self.logger.error("Invalid JSON string")
                raise
        else:
            self.logger.error("Invalid JSON source")
            raise ValueError("Source must be a file path or a JSON string")
    
    def write(self, data: Any, destination: Union[str, Path], **kwargs) -> None:
        """
        Write data to a JSON file.
        
        Args:
            data: Data to write
            destination: Path to JSON file
            **kwargs: Additional arguments for json.dump
        """
        self.logger.info(f"Writing JSON to {destination}")
        
        # Set default indent for better readability
        indent = kwargs.pop("indent", 2)
        
        with open(destination, 'w') as f:
            json.dump(data, f, indent=indent, **kwargs)


class DatabaseProcessor(DataProcessor):
    """Processor for database operations."""
    
    def __init__(self, connection_string: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the database processor.
        
        Args:
            connection_string: Database connection string (optional)
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.connection_string = connection_string
        self.engine = None
        
        if connection_string:
            self._create_engine()
    
    def _create_engine(self) -> None:
        """Create SQLAlchemy engine from connection string."""
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for database operations. "
                             "Install with: pip install sqlalchemy")
        
        self.engine = create_engine(self.connection_string)
    
    def read(self, source: str, **kwargs) -> Any:
        """
        Read data from a database.
        
        Args:
            source: SQL query or table name
            **kwargs: Additional arguments
                - connection_string: Database connection string (optional if set in __init__)
                - params: Parameters for the SQL query
                - as_dataframe: Return as pandas DataFrame (default: True if pandas is available)
            
        Returns:
            Query results as list of dictionaries or pandas DataFrame
        """
        self.logger.info(f"Reading from database: {source}")
        
        # Get connection string
        connection_string = kwargs.pop("connection_string", self.connection_string)
        if not connection_string and not self.engine:
            raise ValueError("Connection string must be provided")
        
        # Create engine if not already created
        if not self.engine or connection_string != self.connection_string:
            self.connection_string = connection_string
            self._create_engine()
        
        # Get query parameters
        params = kwargs.pop("params", {})
        
        # Determine if source is a table name or SQL query
        if source.strip().lower().startswith("select") or source.strip().lower().startswith("with"):
            # Source is an SQL query
            query = source
        else:
            # Source is a table name
            query = f"SELECT * FROM {source}"
        
        # Execute query
        with self.engine.connect() as connection:
            result = connection.execute(sqlalchemy.text(query), params)
            
            # Return as pandas DataFrame if requested and available
            as_dataframe = kwargs.pop("as_dataframe", PANDAS_AVAILABLE)
            if as_dataframe and PANDAS_AVAILABLE:
                return pd.DataFrame(result.fetchall(), columns=result.keys())
            
            # Return as list of dictionaries
            return [dict(row) for row in result]
    
    def write(self, data: Any, destination: str, **kwargs) -> None:
        """
        Write data to a database.
        
        Args:
            data: Data to write (list of dictionaries or pandas DataFrame)
            destination: Table name
            **kwargs: Additional arguments
                - connection_string: Database connection string (optional if set in __init__)
                - if_exists: What to do if the table exists (default: 'fail', options: 'fail', 'replace', 'append')
                - schema: Database schema
                - index: Include index in the table (default: False)
        """
        self.logger.info(f"Writing to database table: {destination}")
        
        # Get connection string
        connection_string = kwargs.pop("connection_string", self.connection_string)
        if not connection_string and not self.engine:
            raise ValueError("Connection string must be provided")
        
        # Create engine if not already created
        if not self.engine or connection_string != self.connection_string:
            self.connection_string = connection_string
            self._create_engine()
        
        # Get additional arguments
        if_exists = kwargs.pop("if_exists", "fail")
        schema = kwargs.pop("schema", None)
        index = kwargs.pop("index", False)
        
        # Convert to pandas DataFrame if not already
        if PANDAS_AVAILABLE:
            if not isinstance(data, pd.DataFrame):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Write to database
            df.to_sql(
                destination,
                self.engine,
                schema=schema,
                if_exists=if_exists,
                index=index,
                **kwargs
            )
        else:
            # Fall back to SQLAlchemy Core for simple cases
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                raise ValueError("Data must be a list of dictionaries when pandas is not available")
            
            # Create table metadata
            metadata = sqlalchemy.MetaData()
            
            # Determine column types (simple implementation)
            columns = []
            if data:
                for key, value in data[0].items():
                    if isinstance(value, int):
                        columns.append(sqlalchemy.Column(key, sqlalchemy.Integer))
                    elif isinstance(value, float):
                        columns.append(sqlalchemy.Column(key, sqlalchemy.Float))
                    elif isinstance(value, bool):
                        columns.append(sqlalchemy.Column(key, sqlalchemy.Boolean))
                    else:
                        columns.append(sqlalchemy.Column(key, sqlalchemy.String))
            
            # Create table
            table = sqlalchemy.Table(destination, metadata, *columns, schema=schema)
            
            # Create table in database if it doesn't exist
            if if_exists == "replace":
                table.drop(self.engine, checkfirst=True)
            
            table.create(self.engine, checkfirst=True)
            
            # Insert data
            with self.engine.connect() as connection:
                if if_exists == "append" or if_exists == "replace":
                    connection.execute(table.insert(), data)
                elif if_exists == "fail":
                    try:
                        connection.execute(table.insert(), data)
                    except sqlalchemy.exc.IntegrityError:
                        raise ValueError(f"Table {destination} already exists")
