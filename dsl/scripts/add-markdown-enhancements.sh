#!/bin/bash
# Script to add markdown enhancements to all markdown files in the project
# This script adds syntax highlighting and DSL flow visualization to markdown files

# Base directory
BASE_DIR="/home/tom/github/taskprovision/hubmail/dsl"

# Path to the enhancement template
TEMPLATE_PATH="$BASE_DIR/static/templates/markdown-enhancements.html"

# Check if template exists
if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "Error: Template file not found at $TEMPLATE_PATH"
    exit 1
fi

# Find all markdown files
echo "Finding all markdown files in $BASE_DIR..."
MARKDOWN_FILES=$(find "$BASE_DIR" -type f -name "*.md" -o -name "*.markdown")

# Count files
FILE_COUNT=$(echo "$MARKDOWN_FILES" | wc -l)
echo "Found $FILE_COUNT markdown files to process"

# Process each file
PROCESSED=0
SKIPPED=0

for FILE in $MARKDOWN_FILES; do
    echo "Processing: $FILE"
    
    # Check if file already has the enhancements
    if grep -q "Taskinity Markdown Enhancements" "$FILE"; then
        echo "  - Already has enhancements, skipping"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi
    
    # Calculate relative path from the markdown file to the static directory
    REL_PATH=$(realpath --relative-to="$(dirname "$FILE")" "$BASE_DIR/static")
    
    # Create a temporary file with the correct relative paths
    TMP_FILE=$(mktemp)
    sed "s|../static|$REL_PATH|g" "$TEMPLATE_PATH" > "$TMP_FILE"
    
    # Add a separator and then the enhancements
    echo -e "\n\n<!-- Markdown Enhancements -->\n" >> "$FILE"
    cat "$TMP_FILE" >> "$FILE"
    
    # Clean up
    rm "$TMP_FILE"
    
    echo "  - Successfully added enhancements"
    PROCESSED=$((PROCESSED + 1))
done

echo "Completed processing markdown files"
echo "  - $PROCESSED files enhanced"
echo "  - $SKIPPED files already had enhancements"
echo "Done!"
