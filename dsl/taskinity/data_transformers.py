"""
Data Transformers for Taskinity.

This module provides classes for transforming data in various ways,
such as filtering, mapping, and reducing.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable, Iterator, TypeVar, Generic

# Type variables for generic typing
T = TypeVar('T')
U = TypeVar('U')


class DataTransformer(Generic[T, U], ABC):
    """Base class for data transformers."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the data transformer.
        
        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(__name__)
    
    @abstractmethod
    def transform(self, data: T) -> U:
        """
        Transform data.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        pass
    
    def __call__(self, data: T) -> U:
        """
        Call the transformer as a function.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        return self.transform(data)


class FilterTransformer(DataTransformer[List[T], List[T]]):
    """Transformer for filtering data."""
    
    def __init__(self, predicate: Callable[[T], bool], logger: Optional[logging.Logger] = None):
        """
        Initialize the filter transformer.
        
        Args:
            predicate: Function that returns True for items to keep
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.predicate = predicate
    
    def transform(self, data: List[T]) -> List[T]:
        """
        Filter data based on the predicate.
        
        Args:
            data: List of items to filter
            
        Returns:
            Filtered list
        """
        self.logger.info(f"Filtering {len(data)} items")
        result = [item for item in data if self.predicate(item)]
        self.logger.info(f"Filtered to {len(result)} items")
        return result


class MapTransformer(DataTransformer[List[T], List[U]]):
    """Transformer for mapping data."""
    
    def __init__(self, mapper: Callable[[T], U], logger: Optional[logging.Logger] = None):
        """
        Initialize the map transformer.
        
        Args:
            mapper: Function to apply to each item
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.mapper = mapper
    
    def transform(self, data: List[T]) -> List[U]:
        """
        Map data using the mapper function.
        
        Args:
            data: List of items to map
            
        Returns:
            Mapped list
        """
        self.logger.info(f"Mapping {len(data)} items")
        result = [self.mapper(item) for item in data]
        return result


class ReduceTransformer(DataTransformer[List[T], U]):
    """Transformer for reducing data to a single value."""
    
    def __init__(self, reducer: Callable[[U, T], U], initial_value: U, logger: Optional[logging.Logger] = None):
        """
        Initialize the reduce transformer.
        
        Args:
            reducer: Function to apply to each item and accumulator
            initial_value: Initial value for the accumulator
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.reducer = reducer
        self.initial_value = initial_value
    
    def transform(self, data: List[T]) -> U:
        """
        Reduce data to a single value.
        
        Args:
            data: List of items to reduce
            
        Returns:
            Reduced value
        """
        self.logger.info(f"Reducing {len(data)} items")
        result = self.initial_value
        for item in data:
            result = self.reducer(result, item)
        return result


class ChainTransformer(DataTransformer[T, Any]):
    """Transformer that chains multiple transformers together."""
    
    def __init__(self, transformers: List[DataTransformer], logger: Optional[logging.Logger] = None):
        """
        Initialize the chain transformer.
        
        Args:
            transformers: List of transformers to apply in sequence
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.transformers = transformers
    
    def transform(self, data: T) -> Any:
        """
        Apply multiple transformers in sequence.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        self.logger.info(f"Applying chain of {len(self.transformers)} transformers")
        result = data
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result


class GroupByTransformer(DataTransformer[List[Dict[str, Any]], Dict[Any, List[Dict[str, Any]]]]):
    """Transformer for grouping data by a key."""
    
    def __init__(self, key: Union[str, Callable[[Dict[str, Any]], Any]], logger: Optional[logging.Logger] = None):
        """
        Initialize the group by transformer.
        
        Args:
            key: Key to group by (string or function)
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.key = key
    
    def transform(self, data: List[Dict[str, Any]]) -> Dict[Any, List[Dict[str, Any]]]:
        """
        Group data by a key.
        
        Args:
            data: List of dictionaries to group
            
        Returns:
            Dictionary mapping keys to lists of items
        """
        self.logger.info(f"Grouping {len(data)} items")
        result = {}
        
        # Determine how to get the key
        if isinstance(self.key, str):
            key_func = lambda item: item.get(self.key)
        else:
            key_func = self.key
        
        # Group items
        for item in data:
            key = key_func(item)
            if key not in result:
                result[key] = []
            result[key].append(item)
        
        self.logger.info(f"Grouped into {len(result)} groups")
        return result


class AggregateTransformer(DataTransformer[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Transformer for aggregating data."""
    
    def __init__(
        self,
        group_by: Union[str, Callable[[Dict[str, Any]], Any]],
        aggregations: Dict[str, Dict[str, Callable[[List[Any]], Any]]],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the aggregate transformer.
        
        Args:
            group_by: Key to group by (string or function)
            aggregations: Dictionary mapping output keys to dictionaries mapping input keys to aggregation functions
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.group_by = group_by
        self.aggregations = aggregations
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate data.
        
        Args:
            data: List of dictionaries to aggregate
            
        Returns:
            List of aggregated dictionaries
        """
        self.logger.info(f"Aggregating {len(data)} items")
        
        # Group data
        grouper = GroupByTransformer(self.group_by, self.logger)
        grouped = grouper.transform(data)
        
        # Aggregate each group
        result = []
        for key, group in grouped.items():
            aggregated = {"group_key": key}
            
            for output_key, aggregation in self.aggregations.items():
                for input_key, agg_func in aggregation.items():
                    # Extract values for the input key
                    values = [item.get(input_key) for item in group if input_key in item]
                    
                    # Apply aggregation function
                    aggregated[output_key] = agg_func(values)
            
            result.append(aggregated)
        
        self.logger.info(f"Aggregated into {len(result)} items")
        return result


class SortTransformer(DataTransformer[List[T], List[T]]):
    """Transformer for sorting data."""
    
    def __init__(
        self,
        key: Optional[Callable[[T], Any]] = None,
        reverse: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the sort transformer.
        
        Args:
            key: Function to extract the sort key (optional)
            reverse: Whether to sort in reverse order (default: False)
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.key = key
        self.reverse = reverse
    
    def transform(self, data: List[T]) -> List[T]:
        """
        Sort data.
        
        Args:
            data: List of items to sort
            
        Returns:
            Sorted list
        """
        self.logger.info(f"Sorting {len(data)} items")
        return sorted(data, key=self.key, reverse=self.reverse)


class LimitTransformer(DataTransformer[List[T], List[T]]):
    """Transformer for limiting the number of items."""
    
    def __init__(self, limit: int, offset: int = 0, logger: Optional[logging.Logger] = None):
        """
        Initialize the limit transformer.
        
        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip (default: 0)
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.limit = limit
        self.offset = offset
    
    def transform(self, data: List[T]) -> List[T]:
        """
        Limit the number of items.
        
        Args:
            data: List of items to limit
            
        Returns:
            Limited list
        """
        self.logger.info(f"Limiting {len(data)} items (offset={self.offset}, limit={self.limit})")
        return data[self.offset:self.offset + self.limit]
