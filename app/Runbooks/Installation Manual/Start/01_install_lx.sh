#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python is not installed. Please install Python and try again."
    exit 1
fi

# Run the Python script
python 01_start.py