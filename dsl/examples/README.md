# Taskinity Examples

This directory contains various examples demonstrating how to use Taskinity in different scenarios. Each example is self-contained and includes all necessary files to run it, including Dockerfiles and docker-compose configurations where appropriate.

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

Each example directory contains a README.md file with specific instructions for running that example. In general, you can follow these steps:

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
  script.src = '/static/js/dsl-flow-visualizer.js';
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
