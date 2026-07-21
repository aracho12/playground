#!/bin/bash
#
# pushmac.sh — send file(s) from tars to the Mac over a reverse SSH tunnel.
#
# Prerequisite: the Mac must have an active SSH session to tars that sets up a
# RemoteForward back to the Mac's SSH server, e.g. in the Mac's ~/.ssh/config:
#
#     Host tars
#         HostName tars.kaist.ac.kr
#         User aracho
#         RemoteForward 2222 localhost:22
#
# While that Mac->tars session is alive, tars can reach the Mac at
# localhost:2222. Run this ON tars.
#
# Usage:
#   pushmac.sh                                    Send ~/conversations/ to the Mac
#   pushmac.sh <file/dir> [<file/dir> ...]        Send file(s) into the default dest dir
#   MAC_DEST=/Users/aracho/Desktop pushmac.sh f   Override destination dir
#   MAC_PORT=2222 pushmac.sh f                     Override tunnel port

# Configuration (override via environment)
MAC_PORT="${MAC_PORT:-2222}"
MAC_USER="${MAC_USER:-aracho}"
MAC_HOST="${MAC_HOST:-localhost}"
MAC_DEST="${MAC_DEST:-/Users/aracho/bin/tars_transfer/}"

# No-argument default: sync the conversations folder to the Mac.
CONV_SRC="${CONV_SRC:-$HOME/conversations/}"
CONV_DEST="${CONV_DEST:-/Users/aracho/Dropbox/BACKUP/claude_conversations/tars_aracho/}"

usage() {
    cat <<EOF
Usage:
  $(basename "$0")                              Send $CONV_SRC to the Mac ($CONV_DEST)
  $(basename "$0") <file/dir> [<file/dir> ...]  Send file(s) to the Mac ($MAC_DEST)

Requires an active Mac->tars SSH session with:
    RemoteForward $MAC_PORT localhost:22
in the Mac's ~/.ssh/config.
Override via env vars: MAC_DEST / MAC_PORT / MAC_USER / MAC_HOST / CONV_SRC / CONV_DEST.
EOF
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# Pick source(s) and destination: no args -> conversations, else the given paths.
if [ "$#" -eq 0 ]; then
    SRCS=("$CONV_SRC")
    DEST="$CONV_DEST"
else
    SRCS=("$@")
    DEST="$MAC_DEST"
fi

# Verify the reverse tunnel is up before attempting the transfer.
if ! ssh -p "$MAC_PORT" -o ConnectTimeout=5 -o BatchMode=yes \
        "$MAC_USER@$MAC_HOST" true 2>/dev/null; then
    echo "Cannot reach the Mac at $MAC_HOST:$MAC_PORT." >&2
    echo "Open an 'ssh tars' session from the Mac (with RemoteForward $MAC_PORT localhost:22) first." >&2
    exit 1
fi

echo "Sending to Mac ($MAC_USER@$MAC_HOST:$MAC_PORT) -> $DEST"
echo "Source: ${SRCS[*]}"
echo ""

rsync -avzP \
    -e "ssh -p $MAC_PORT" \
    "${SRCS[@]}" \
    "$MAC_USER@$MAC_HOST:$DEST"

if [ $? -eq 0 ]; then
    echo ""
    echo "Push completed successfully!"
    echo "Destination: $MAC_USER@$MAC_HOST:$DEST"
else
    echo ""
    echo "Push failed with errors."
    exit 1
fi
