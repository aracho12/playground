#!/bin/bash

# Configuration
LOCAL_DIR="/Users/aracho/bin/tars_transfer"
REMOTE_USER="aracho"
REMOTE_HOST="tars.kaist.ac.kr"
REMOTE_DIR="/home/aracho/transfer"

# Create local directory if it doesn't exist
mkdir -p "$LOCAL_DIR"

# Check if remote directory is empty
REMOTE_FILES=$(ssh "$REMOTE_USER@$REMOTE_HOST" "ls -A $REMOTE_DIR 2>/dev/null")

if [ -z "$REMOTE_FILES" ]; then
    echo "No files to transfer."
    exit 0
fi

# Transfer files
echo "Transferring files..."
rsync -avzP "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/" "$LOCAL_DIR/"

# Check if transfer was successful
if [ $? -eq 0 ]; then
    echo "Transfer complete! Deleting remote files..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "rm -rf $REMOTE_DIR/*"
    echo "Done!"
else
    echo "Transfer failed. Remote files were not deleted."
    exit 1
fi

