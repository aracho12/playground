#!/bin/bash

# Configuration
REMOTE_USER="aracho"
REMOTE_HOST="tars.kaist.ac.kr"
REMOTE_DIR="/home/aracho"
LOCAL_BACKUP_DIR="/Users/aracho/Dropbox/BACKUP/tars"

# Files and directories to exclude (add patterns as needed)
EXCLUDE_PATTERNS=(
    ".cache"
    ".local"
    "*.tmp"
    ".git"
    "__pycache__"
    "node_modules"
    ".DS_Store"
    "AECCAR*"
)

# Create local backup directory if it doesn't exist
mkdir -p "$LOCAL_BACKUP_DIR"

# Build exclude options for rsync
EXCLUDE_OPTS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTS="$EXCLUDE_OPTS --exclude=$pattern"
done

# Run rsync backup
echo "Starting backup from tars to Dropbox..."
echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
echo "Destination: $LOCAL_BACKUP_DIR"
echo ""

rsync -avzP \
    --delete \
    $EXCLUDE_OPTS \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/" \
    "$LOCAL_BACKUP_DIR/"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Backup completed successfully!"
    echo "Backup location: $LOCAL_BACKUP_DIR"
else
    echo ""
    echo "Backup failed with errors."
    exit 1
fi
