#!/bin/bash

# Configuration
REMOTE_USER="x3379a03"
REMOTE_HOST="nurion.ksc.re.kr"
REMOTE_DIR="/home01/x3379a03/conversations"
LOCAL_BACKUP_DIR="/Users/aracho/Dropbox/BACKUP/claude_conversations/nurion_x3379a03"

# Files and directories to exclude (add patterns as needed)
EXCLUDE_PATTERNS=(
    ".DS_Store"
    "*.tmp"
)

# Create local backup directory if it doesn't exist
mkdir -p "$LOCAL_BACKUP_DIR"

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

# Run rsync backup (accumulating — no --delete so Dropbox keeps files
# even if they are removed from the remote)
echo ""
echo "Starting accumulating backup of conversations..."
echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
echo "Destination: $LOCAL_BACKUP_DIR"
echo ""

rsync -avzP \
    -e "ssh -o ControlPath=$SOCKET_PATH" \
    $EXCLUDE_OPTS \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/" \
    "$LOCAL_BACKUP_DIR/"

if [ $? -eq 0 ]; then
    echo ""
    echo "Conversations backup completed successfully!"
    echo "Backup location: $LOCAL_BACKUP_DIR"
else
    echo ""
    echo "Conversations backup failed with errors."
    exit 1
fi
