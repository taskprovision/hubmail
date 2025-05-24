#!/bin/bash
# Script to add DSL Flow Visualizer JavaScript to all Markdown files in the project

# Directory containing the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Root directory of the project
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
# Path to the DSL Flow Visualizer JavaScript
JS_PATH="/hubmail/dsl/static/js/dsl-flow-visualizer.js"

# HTML to add at the end of each Markdown file
read -r -d '' HTML_CONTENT << EOM
<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '${JS_PATH}';
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
  style.textContent = \`
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
  \`;
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
EOM

# Function to add HTML content to a Markdown file if it doesn't already have it
add_html_to_markdown() {
  local file="$1"
  
  # Check if the file already has the DSL Flow Visualizer script
  if grep -q "DSL Flow Visualizer" "$file"; then
    echo "Skipping $file (already has DSL Flow Visualizer)"
    return
  fi
  
  # Add the HTML content at the end of the file
  echo -e "\n$HTML_CONTENT" >> "$file"
  echo "Added DSL Flow Visualizer to $file"
}

# Find all Markdown files in the project
find "$PROJECT_DIR" -name "*.md" | while read -r file; do
  add_html_to_markdown "$file"
done

echo "Completed adding DSL Flow Visualizer to Markdown files"
