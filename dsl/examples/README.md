# Taskinity Examples

This directory contains various examples demonstrating how to use Taskinity in different scenarios. Each example is self-contained and includes all necessary files to run it, including Dockerfiles and docker-compose configurations where appropriate.

## Taskinity Project Structure

The Taskinity project has been reorganized into a more modular structure:

1. **Core Module** (`taskinity/core/`): Contains essential functionality including task and flow decorators, DSL parser and executor, and flow management utilities.

2. **Extensions Module** (`taskinity/extensions/`): Contains additional features like visualization tools, code converters, data processors, and API clients.

3. **Utils Module** (`taskinity/utils/`): Provides supporting functionality like environment variable management, benchmarking tools, and logging utilities.

All examples in this directory have been updated to use the new module structure. The old `flow_dsl` module references have been replaced with the new `taskinity_core` module.

## Examples Overview

### 1. Email Processing

A complete example of using Taskinity to process emails. This example demonstrates how to:
- Connect to email servers (SMTP/IMAP)
- Process incoming emails based on rules
- Send notifications based on email content
- Schedule email processing tasks

**Directory**: [email_processing](./email_processing/)

### 2. Data Processing

Examples of data processing pipelines using Taskinity. These examples show how to:
- Load data from various sources (CSV, JSON, databases)
- Transform and clean data
- Analyze data and generate reports
- Visualize results

**Directory**: [data_processing](./data_processing/)

### 3. API Integration

Examples of integrating external APIs with Taskinity. These examples demonstrate:
- Making API requests
- Processing API responses
- Error handling and retries
- Authentication with various services

**Directory**: [api_integration](./api_integration/)

### 4. Visualization

Examples of visualizing Taskinity flows. These examples show how to:
- Generate Mermaid diagrams from flows
- Create interactive visualizations
- Export flow diagrams to various formats

**Directory**: [visualization](./visualization/)

### 5. Parallel Tasks

Examples of running tasks in parallel with Taskinity. These examples demonstrate:
- Defining parallel task execution
- Managing dependencies between parallel tasks
- Optimizing performance with parallel execution

**Directory**: [parallel_tasks](./parallel_tasks/)

## Running the Examples

### Using the Makefile

This directory includes a centralized Makefile that allows you to run all examples and tests from one place. The Makefile is compatible with the new modular Taskinity structure (core, extensions, utils).

#### View Available Commands

```bash
# Show all available commands
make help
```

#### Running Examples

```bash
# Run all examples
make run-all

# Run a specific example
make email-run     # Run email processing example
make data-run      # Run data processing example
make api-run       # Run API integration example
make parallel-run  # Run parallel tasks example
make viz-run       # Run visualization example
make perf-run      # Run performance benchmarks
```

#### Running Tests

```bash
# Run all tests
make test-all

# Run tests for a specific example
make email-test    # Run email processing tests
make data-test     # Run data processing tests
make api-test      # Run API integration tests
make parallel-test # Run parallel tasks tests
make viz-test      # Run visualization tests
make perf-test     # Run performance benchmark tests
```

#### Docker Environment Management

```bash
# Start Docker environments
make email-docker-basic    # Start basic email Docker environment
make email-docker-mock     # Start mock email Docker environment with MailHog
make email-docker-full     # Start full email Docker environment

# Stop Docker environments
make email-docker-down     # Stop all email Docker environments

# Start all Docker environments
make docker-up-all

# Stop all Docker environments
make docker-down-all
```

### Manual Execution

Each example directory also contains a README.md file with specific instructions for running that example manually. In general, you can follow these steps:

1. Navigate to the example directory:
   ```bash
   cd examples/[example_name]
   ```

2. Copy the .env.example file to .env and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

3. If the example includes a docker-compose.yml file, start the required services:
   ```bash
   docker-compose up -d
   ```
   
   Or use the provided shell scripts for Docker environments (in email_processing):
   ```bash
   ./docker-up.sh [basic|mock|full]    # Start a specific Docker environment
   ./docker-down.sh [basic|mock|full]   # Stop a specific Docker environment
   ```

4. Run the example:
   ```bash
   python main.py
   ```

## Performance Comparisons

Where applicable, examples include performance comparisons with other solutions to demonstrate Taskinity's efficiency. These comparisons typically measure:

- Lines of code required
- Execution time
- Memory usage
- Ease of implementation

## Contributing

Feel free to contribute your own examples by creating a pull request. Please follow these guidelines:
- Create a new directory for your example
- Include a README.md file with clear instructions
- Include all necessary files to run the example
- Add an .env.example file if environment variables are needed
- Add Docker configurations if external services are required

<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '/hubmail/dsl/static/js/dsl-flow-visualizer.js';
  script.async = true;
  script.onload = function() {
    // Initialize the visualizer when script is loaded
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  };
  document.head.appendChild(script);
  
  // Add CSS styles
  var style = document.createElement('style');
  style.textContent = `
    .dsl-flow-diagram {
      margin: 20px 0;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 5px;
      background-color: #f9f9f9;
      overflow-x: auto;
    }
    
    .dsl-download-btn {
      background-color: #4682b4;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 5px 10px;
      font-size: 14px;
      cursor: pointer;
    }
    
    .dsl-download-btn:hover {
      background-color: #36648b;
    }
  `;
  document.head.appendChild(style);
  
  // Add language class to DSL code blocks if not already present
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
      var content = codeBlock.textContent.trim();
      if (content.startsWith('flow ') && !codeBlock.classList.contains('language-dsl')) {
        codeBlock.classList.add('language-dsl');
      }
    });
    
    // Initialize the visualizer
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  });
})();
</script>


<!-- Markdown Enhancements -->

<!-- Taskinity Markdown Enhancements -->
<!-- Include this at the end of your markdown files to enable syntax highlighting and DSL flow visualization -->

<!-- Prism.js for syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>

<!-- Load common language components -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>

<!-- Taskinity custom scripts -->
<script src="../static/js/dsl-flow-visualizer.js"></script>
<script src="../static/js/markdown-syntax-highlighter.js"></script>

<script>
  // Initialize both scripts when the page loads
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize syntax highlighter
    window.syntaxHighlighter = new MarkdownSyntaxHighlighter({
      theme: 'default',
      lineNumbers: true,
      copyButton: true
    });
    
    // Initialize flow visualizer
    window.flowVisualizer = new DSLFlowVisualizer({
      codeBlockSelector: 'pre code.language-dsl, pre code.language-flow'
    });
  });
</script>

<!-- Custom styles for better markdown rendering -->
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }
  
  pre {
    border-radius: 5px;
    background-color: #f5f5f5;
    padding: 15px;
    overflow: auto;
  }
  
  code {
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: #2c3e50;
  }
  
  a {
    color: #3498db;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
  }
  
  table, th, td {
    border: 1px solid #ddd;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
  }
  
  th {
    background-color: #f2f2f2;
  }
  
  blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    color: #666;
    margin: 20px 0;
  }
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  .dsl-flow-diagram {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
</style>
