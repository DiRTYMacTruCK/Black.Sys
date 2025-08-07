#!/bin/bash

# Set terminal title
echo -ne "\033]0;Steam API File Replacer\007"

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Hardcoded target directory
TARGET_DIR="./games"

echo "================================================================================"
echo "                          Steam API File Replacer"
echo "================================================================================"
echo
echo "Target directory: $TARGET_DIR"
echo

# Ask user for confirmation
echo "This will search for and replace Steam API files in:"
echo "$TARGET_DIR"
echo
echo "Do you want to:"
echo "  1. Run in DRY-RUN mode (preview changes only)"
echo "  2. REPLACE files (creates backups)"
echo "  3. Cancel"
echo
read -p "Select an option (1-3): " choice

case $choice in
    1)
        echo
        echo "Running in DRY-RUN mode..."
        echo "--------------------------------------------------------------------------------"
        python3 "./data/steam_api_replacer.py" "$TARGET_DIR" --dry-run
        ;;
    2)
        echo
        echo "REPLACING files (backups will be created)..."
        echo "--------------------------------------------------------------------------------"
        python3 "./data/steam_api_replacer.py" "$TARGET_DIR"
        ;;
    3)
        echo
        echo "Operation cancelled."
        ;;
    *)
        echo
        echo "Invalid option selected."
        ;;
esac

echo
echo "--------------------------------------------------------------------------------"
read -p "Press Enter to close this window..."
