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
    ".conda"
    "transfer"
    "00_START"
    "AECCAR*"
    "WAVECAR"
    "CHG*"
    "*.cube"
    "solute"
    "solute.temp"
    #"ces2.emd.lammpstrj"
)

# Create local backup directories if they don't exist
mkdir -p "$LOCAL_BACKUP_DIR"
mkdir -p "$LOCAL_SCRATCH_BACKUP_DIR"

# Check and refresh SSH ControlMaster socket
SOCKET_PATH="$HOME/.ssh/sockets/${REMOTE_USER}@${REMOTE_HOST}:22"
mkdir -p "$HOME/.ssh/sockets"

if [ -S "$SOCKET_PATH" ]; then
    # Socket exists — check if it's alive
    if ! ssh -O check -o ControlPath="$SOCKET_PATH" "$REMOTE_USER@$REMOTE_HOST" 2>/dev/null; then
        echo "Stale SSH socket found. Removing and reconnecting..."
        rm -f "$SOCKET_PATH"
        ssh -MNf \
            -o ControlPath="$SOCKET_PATH" \
            -o ControlPersist=10m \
            "$REMOTE_USER@$REMOTE_HOST"
    else
        echo "Reusing existing SSH connection."
    fi
else
    echo "No SSH socket found. Connecting to $REMOTE_HOST (OTP + Password required)..."
    ssh -MNf \
        -o ControlPath="$SOCKET_PATH" \
        -o ControlPersist=10m \
        "$REMOTE_USER@$REMOTE_HOST"
fi

# Build exclude options for rsync
EXCLUDE_OPTS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTS="$EXCLUDE_OPTS --exclude=$pattern"
done

# Run rsync backup
# echo "Starting backup from tars to Dropbox..."
# echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
# echo "Destination: $LOCAL_BACKUP_DIR"
# echo ""

# rsync -avzP \
#     --delete \
#     -e "ssh -o ControlPath=$SOCKET_PATH" \
#     $EXCLUDE_OPTS \
#     "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/" \
#     "$LOCAL_BACKUP_DIR/"

# # Check if home backup was successful
# if [ $? -eq 0 ]; then
#     echo ""
#     echo "Home backup completed successfully!"
#     echo "Backup location: $LOCAL_BACKUP_DIR"
# else
#     echo ""
#     echo "Home backup failed with errors."
#     exit 1
# fi

# Run rsync backup for scratch
echo ""
echo "Starting backup of scratch directory..."
echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_SCRATCH_DIR"
echo "Destination: $LOCAL_SCRATCH_BACKUP_DIR"
echo ""

rsync -avzP \
    --delete \
    -e "ssh -o ControlPath=$SOCKET_PATH" \
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
