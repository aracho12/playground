#!/bin/bash

# Configuration
REMOTE_USER="x3246a09"
REMOTE_HOST="nurion.ksc.re.kr"
REMOTE_DIR="/home01/x3246a09"
REMOTE_SCRATCH_DIR="/scratch/x3246a09"
LOCAL_BACKUP_DIR="/Users/aracho/Dropbox/BACKUP/nurion_x3246a09/home"
LOCAL_SCRATCH_BACKUP_DIR="/Users/aracho/Dropbox/BACKUP/nurion_x3246a09/scratch"

# Files and directories to exclude (add patterns as needed)
EXCLUDE_PATTERNS=(
    ".cache"
    ".local"
    "*.tmp"
    ".git"
    "__pycache__"
    "node_modules"
    ".DS_Store"
    "_TRASH"
    "miniconda3"
    "transfer"
    "00_START"
    "AECCAR*"
    "WAVECAR"
    "CHG*"
    "*.cube"
    "solute"
    "solute.temp"
)

# Create local backup directories if they don't exist
mkdir -p "$LOCAL_BACKUP_DIR"
mkdir -p "$LOCAL_SCRATCH_BACKUP_DIR"

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

# Check if home backup was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Home backup completed successfully!"
    echo "Backup location: $LOCAL_BACKUP_DIR"
else
    echo ""
    echo "Home backup failed with errors."
    exit 1
fi

# Run rsync backup for scratch
echo ""
echo "Starting backup of scratch directory..."
echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_SCRATCH_DIR"
echo "Destination: $LOCAL_SCRATCH_BACKUP_DIR"
echo ""

rsync -avzP \
    --delete \
    $EXCLUDE_OPTS \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_SCRATCH_DIR/" \
    "$LOCAL_SCRATCH_BACKUP_DIR/"

# Check if scratch backup was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Scratch backup completed successfully!"
    echo "Backup location: $LOCAL_SCRATCH_BACKUP_DIR"
else
    echo ""
    echo "Scratch backup failed with errors."
    exit 1
fi
