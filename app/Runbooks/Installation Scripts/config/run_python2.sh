#!/bin/bash

chmod -R 777 .

# Get all Python files where the first 3 characters are numbers
python_files=$(ls | grep -E '^[0-9]{2}.*\.py$')

# Check if we found any Python files to execute
if [ -z "$python_files" ]; then
  echo "No Python files found with the required naming convention."
  exit 1
fi

# Sort the Python files based on the first 3 characters (numeric order)
sorted_files=$(echo "$python_files" | sort -n)

# Execute each file in sequence using python
for file in $sorted_files; do
  echo "Executing $file..."
  python "$file"
done

echo "Execution complete."
