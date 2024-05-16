#!/bin/bash

input_dir_json="./scraped_specs/*.json"

# Use a glob expansion directly in the loop to handle multiple files
for file in $input_dir_json; do
    if [ -f "$file" ]; then
        base_name_input_file=$(basename "$file" .json)
        echo "Processing file: $base_name_input_file"

        # Make sure to use 'node' (check the case sensitivity)
        # Also ensure your script path is correctly specified relative to where you're running this script
        result=$(node step1_generate_api_calls.js "${base_name_input_file}" "json")
        echo "Result: $result"
    else
        echo "No JSON files found in $input_dir_json"
    fi
done

input_dir_yaml="./scraped_specs/*.yaml"

# Use a glob expansion directly in the loop to handle multiple files
for file in $input_dir_yaml; do
    if [ -f "$file" ]; then
        base_name_input_file=$(basename "$file" .yaml)
        echo "Processing file: $base_name_input_file"

        # Make sure to use 'node' (check the case sensitivity)
        # Also ensure your script path is correctly specified relative to where you're running this script
        result=$(node step1_generate_api_calls.js "${base_name_input_file}" "yaml")
        echo "Result: $result"
    else
        echo "No JSON files found in $input_dir_yaml"
    fi
done