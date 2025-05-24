"""
Code Converter Extension for Taskinity.

This extension provides functionality to analyze existing Python code
and convert it to Taskinity flows, making it easier to migrate existing
projects to use Taskinity.
"""
import os
import ast
import inspect
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple

# Check if optional dependencies are installed
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


def convert_code_to_taskinity(
    source_code: Union[str, Callable, Path], 
    output_file: Optional[str] = None,
    include_docstrings: bool = True,
    include_imports: bool = True
) -> str:
    """
    Convert Python code to Taskinity flow DSL.
    
    Args:
        source_code: Python source code as string, function object, or file path
        output_file: Path to save the generated DSL (optional)
        include_docstrings: Whether to include docstrings in the generated DSL
        include_imports: Whether to include import statements in the generated DSL
        
    Returns:
        Generated Taskinity DSL as a string
    """
    # Handle different input types
    if isinstance(source_code, Callable):
        # Extract source code from function object
        source_code = inspect.getsource(source_code)
    elif isinstance(source_code, (str, Path)) and os.path.isfile(str(source_code)):
        # Read source code from file
        with open(source_code, 'r') as f:
            source_code = f.read()
    
    # Parse the source code
    code_structure = analyze_code_structure(source_code)
    
    # Generate Taskinity DSL
    dsl_text = _generate_dsl_from_structure(code_structure, include_docstrings, include_imports)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(dsl_text)
    
    return dsl_text


def analyze_code_structure(source_code: str) -> Dict[str, Any]:
    """
    Analyze Python source code and extract its structure.
    
    Args:
        source_code: Python source code as string
        
    Returns:
        Dictionary containing the code structure
    """
    # Parse the source code into an AST
    tree = ast.parse(source_code)
    
    # Extract functions
    functions = {}
    imports = []
    main_code = []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # Extract function definition
            func_name = node.name
            func_args = [arg.arg for arg in node.args.args]
            func_docstring = ast.get_docstring(node)
            func_body = source_code.split('\n')[node.lineno-1:node.end_lineno]
            
            # Extract function dependencies (function calls within the function)
            func_calls = _extract_function_calls(node)
            
            functions[func_name] = {
                'name': func_name,
                'args': func_args,
                'docstring': func_docstring,
                'body': '\n'.join(func_body),
                'calls': func_calls
            }
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            # Extract import statements
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(f"import {name.name}")
            else:  # ImportFrom
                names = ', '.join(name.name for name in node.names)
                imports.append(f"from {node.module} import {names}")
        else:
            # Extract other code (e.g., main block)
            main_code.append(ast.unparse(node))
    
    # Build the dependency graph
    dependencies = []
    for func_name, func_info in functions.items():
        for called_func in func_info['calls']:
            if called_func in functions:
                dependencies.append((func_name, called_func))
    
    return {
        'functions': functions,
        'imports': imports,
        'main_code': main_code,
        'dependencies': dependencies
    }


def _extract_function_calls(node: ast.AST) -> Set[str]:
    """
    Extract function calls from an AST node.
    
    Args:
        node: AST node to analyze
        
    Returns:
        Set of function names that are called within the node
    """
    function_calls = set()
    
    class FunctionCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                function_calls.add(node.func.id)
            self.generic_visit(node)
    
    visitor = FunctionCallVisitor()
    visitor.visit(node)
    
    return function_calls


def _generate_dsl_from_structure(
    code_structure: Dict[str, Any],
    include_docstrings: bool = True,
    include_imports: bool = True
) -> str:
    """
    Generate Taskinity DSL from code structure.
    
    Args:
        code_structure: Code structure dictionary from analyze_code_structure
        include_docstrings: Whether to include docstrings
        include_imports: Whether to include import statements
        
    Returns:
        Generated Taskinity DSL as a string
    """
    functions = code_structure['functions']
    imports = code_structure['imports']
    dependencies = code_structure['dependencies']
    
    # Determine flow name based on the first function or a default
    flow_name = next(iter(functions.keys()), "ConvertedFlow") if functions else "ConvertedFlow"
    
    # Start building the DSL
    dsl_lines = []
    
    # Add imports if requested
    if include_imports and imports:
        for import_stmt in imports:
            dsl_lines.append(import_stmt)
        dsl_lines.append("")  # Empty line after imports
    
    # Start flow definition
    dsl_lines.append(f"flow {flow_name}:")
    dsl_lines.append(f"    description: \"Converted from Python code\"")
    dsl_lines.append("")
    
    # Add tasks (functions)
    for func_name, func_info in functions.items():
        dsl_lines.append(f"    task {func_name}:")
        
        # Add docstring if available and requested
        if include_docstrings and func_info['docstring']:
            dsl_lines.append(f"        description: \"{func_info['docstring'].replace('\"', '\\\"')}\"")
        
        # Add code block
        dsl_lines.append(f"        code: |")
        for line in func_info['body'].split('\n'):
            dsl_lines.append(f"            {line}")
        
        dsl_lines.append("")  # Empty line after task
    
    # Add connections (dependencies)
    if dependencies:
        dsl_lines.append("    # Task connections")
        for source, target in dependencies:
            dsl_lines.append(f"    {source} -> {target}")
    
    return '\n'.join(dsl_lines)


def visualize_code_structure(code_structure: Dict[str, Any], output_file: str) -> None:
    """
    Visualize the code structure as a graph.
    
    Args:
        code_structure: Code structure dictionary from analyze_code_structure
        output_file: Path to save the visualization
    """
    if not NETWORKX_AVAILABLE:
        raise ImportError("NetworkX and matplotlib are required for visualization. "
                         "Install with: pip install networkx matplotlib")
    
    import matplotlib.pyplot as plt
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes (functions)
    for func_name in code_structure['functions']:
        G.add_node(func_name)
    
    # Add edges (dependencies)
    for source, target in code_structure['dependencies']:
        G.add_edge(source, target)
    
    # Create the visualization
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, arrowsize=20, font_size=12, font_weight='bold')
    
    # Save the visualization
    plt.savefig(output_file)
    plt.close()
    
    print(f"Visualization saved to {output_file}")


def import_module_from_file(file_path: Union[str, Path]) -> Any:
    """
    Import a Python module from a file path.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Imported module object
    """
    file_path = Path(file_path)
    module_name = file_path.stem
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module
