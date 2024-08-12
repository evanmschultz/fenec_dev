#!/bin/bash

# Set the output file name
output_file="aggregated_contents.txt"

# Remove the output file if it already exists
rm -f "$output_file"

# Function to process each file
process_file() {
    local file="$1"
    local rel_path="${file#./}"
    # Append file path and contents to the output file
    echo "File: $rel_path" >> "$output_file"
    echo "----------------------------------------" >> "$output_file"
    cat "$file" >> "$output_file"
    echo -e "\n\n" >> "$output_file"
}

# Variable to keep track of the last printed directory
last_dir=""

# Function to print directory name
print_directory() {
    local dir=$(dirname "$1")
    if [ "$dir" != "$last_dir" ]; then
        echo "Entering directory: $dir"
        last_dir="$dir"
    fi
}

# Find all files, excluding specific directories and files
find . -type f \
    ! -path "*/.git/*" \
    ! -path "*/.pytest_cache/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.venv/*" \
    ! -path "*/node_modules/*" \
    ! -path "*/chroma/*" \
    ! -path "*/output_json/*" \
    ! -name ".gitignore" \
    ! -name "LICENSE" \
    ! -name "$output_file" \
    ! -name "*.pyc" \
    ! -name ".DS_Store" \
    ! -name "*.log" \
    ! -name "*.sqlite3" \
    ! -name "*.db" \
    ! -name "poetry.lock" \
    ! -name "Pipfile.lock" \
    ! -name "package-lock.json" \
    ! -name "yarn.lock" \
    ! -name "Gemfile.lock" \
    ! -name "composer.lock" \
    ! -name "*.env" \
    ! -name ".env.*" \
    ! -name "*.cfg" \
    ! -name "*.ini" \
    ! -name "*.toml" \
    ! -name "*.yaml" \
    ! -name "*.yml" \
    -print0 | while IFS= read -r -d '' file; do
    print_directory "$file"
    process_file "$file"
done

echo "File aggregation complete. Output saved to $output_file"