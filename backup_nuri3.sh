#!/bin/bash

# Configuration
REMOTE_USER="x3379a03"
REMOTE_HOST="nurion.ksc.re.kr"
REMOTE_HOME="/home01/x3379a03"
REMOTE_DIR="$REMOTE_HOME"
REMOTE_SCRATCH_DIR="/scratch/x3379a03"
REMOTE_CONVERSATIONS_DIR="$REMOTE_HOME/conversations"
LOCAL_BACKUP_DIR="/Users/aracho/Dropbox/BACKUP/nurion_x3379a03/home"
LOCAL_SCRATCH_BACKUP_DIR="/Users/aracho/Dropbox/BACKUP/nurion_x3379a03/scratch"
LOCAL_CONVERSATIONS_BACKUP_DIR="/Users/aracho/Dropbox/BACKUP/claude_conversations/nurion_x3379a03"

# SSH ControlMaster socket
SOCKET_PATH="$HOME/.ssh/sockets/${REMOTE_USER}@${REMOTE_HOST}:22"

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
    "ces2.emd.lammpstrj"
)

usage() {
    cat <<EOF
Usage:
  $(basename "$0")                 Back up remote home and scratch to Dropbox
  $(basename "$0") --conversation  Back up remote conversations folder to Dropbox
  $(basename "$0") <path>          Fetch a remote file/folder into the current directory
                                   (path is relative to $REMOTE_HOME, or absolute if it
                                   starts with /)
EOF
}

# Ensure a live SSH ControlMaster connection (OTP + Password prompted once).
ensure_ssh() {
    mkdir -p "$HOME/.ssh/sockets"

    if [ -S "$SOCKET_PATH" ]; then
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
}

# Build exclude options for rsync from EXCLUDE_PATTERNS.
build_exclude_opts() {
    EXCLUDE_OPTS=""
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        EXCLUDE_OPTS="$EXCLUDE_OPTS --exclude=$pattern"
    done
}

# Fetch a remote file/folder into the current working directory.
# $1: path relative to REMOTE_HOME, or absolute if it starts with /
fetch_path() {
    local arg="$1"
    local remote_path

    if [[ "$arg" == /* ]]; then
        remote_path="$arg"
    else
        remote_path="$REMOTE_HOME/$arg"
    fi

    ensure_ssh

    echo ""
    echo "Fetching from remote..."
    echo "Source: $REMOTE_USER@$REMOTE_HOST:$remote_path"
    echo "Destination: $(pwd)/"
    echo ""

    # No trailing slash on the source so the file/folder itself is copied here.
    rsync -avzP \
        -e "ssh -o ControlPath=$SOCKET_PATH" \
        "$REMOTE_USER@$REMOTE_HOST:$remote_path" \
        "./"

    if [ $? -eq 0 ]; then
        echo ""
        echo "Fetch completed successfully!"
        echo "Saved into: $(pwd)"
    else
        echo ""
        echo "Fetch failed with errors."
        exit 1
    fi
}

# Back up the remote conversations folder to Dropbox (accumulating, no --delete).
backup_conversations() {
    mkdir -p "$LOCAL_CONVERSATIONS_BACKUP_DIR"

    ensure_ssh
    build_exclude_opts

    echo ""
    echo "Starting accumulating backup of conversations..."
    echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_CONVERSATIONS_DIR"
    echo "Destination: $LOCAL_CONVERSATIONS_BACKUP_DIR"
    echo ""

    rsync -avzP \
        -e "ssh -o ControlPath=$SOCKET_PATH" \
        $EXCLUDE_OPTS \
        "$REMOTE_USER@$REMOTE_HOST:$REMOTE_CONVERSATIONS_DIR/" \
        "$LOCAL_CONVERSATIONS_BACKUP_DIR/"

    if [ $? -eq 0 ]; then
        echo ""
        echo "Conversations backup completed successfully!"
        echo "Backup location: $LOCAL_CONVERSATIONS_BACKUP_DIR"
    else
        echo ""
        echo "Conversations backup failed with errors."
        exit 1
    fi
}

# Default backup: home and scratch to Dropbox.
backup_default() {
    mkdir -p "$LOCAL_BACKUP_DIR"
    mkdir -p "$LOCAL_SCRATCH_BACKUP_DIR"

    ensure_ssh
    build_exclude_opts

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

    if [ $? -eq 0 ]; then
        echo ""
        echo "Scratch backup completed successfully!"
        echo "Backup location: $LOCAL_SCRATCH_BACKUP_DIR"
    else
        echo ""
        echo "Scratch backup failed with errors."
        exit 1
    fi
}

# Dispatch
case "$1" in
    -h|--help)
        usage
        ;;
    --conversation|--conversations)
        backup_conversations
        ;;
    "")
        backup_default
        ;;
    -*)
        echo "Unknown option: $1" >&2
        echo ""
        usage
        exit 1
        ;;
    *)
        fetch_path "$1"
        ;;
esac
