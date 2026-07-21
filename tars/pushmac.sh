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
#   pushmac.sh <file/dir> [<file/dir> ...]        Send into the default dest dir
#   MAC_DEST=/Users/aracho/Desktop pushmac.sh f   Override destination dir
#   MAC_PORT=2222 pushmac.sh f                     Override tunnel port

# Configuration (override via environment)
MAC_PORT="${MAC_PORT:-2222}"
MAC_USER="${MAC_USER:-aracho}"
MAC_HOST="${MAC_HOST:-localhost}"
MAC_DEST="${MAC_DEST:-/Users/aracho/bin/tars_transfer/}"

usage() {
    cat <<EOF
Usage:
  $(basename "$0") <file/dir> [<file/dir> ...]   Send to the Mac over the reverse tunnel

Requires an active Mac->tars SSH session with:
    RemoteForward $MAC_PORT localhost:22
in the Mac's ~/.ssh/config. Destination on the Mac: $MAC_DEST
(override with MAC_DEST / MAC_PORT / MAC_USER / MAC_HOST env vars).
EOF
}

case "$1" in
    -h|--help|"")
        usage
        [ -z "$1" ] && exit 1 || exit 0
        ;;
esac

# Verify the reverse tunnel is up before attempting the transfer.
if ! ssh -p "$MAC_PORT" -o ConnectTimeout=5 -o BatchMode=yes \
        "$MAC_USER@$MAC_HOST" true 2>/dev/null; then
    echo "Cannot reach the Mac at $MAC_HOST:$MAC_PORT." >&2
    echo "Open an 'ssh tars' session from the Mac (with RemoteForward $MAC_PORT localhost:22) first." >&2
    exit 1
fi

echo "Sending to Mac ($MAC_USER@$MAC_HOST:$MAC_PORT) -> $MAC_DEST"
echo ""

rsync -avzP \
    -e "ssh -p $MAC_PORT" \
    "$@" \
    "$MAC_USER@$MAC_HOST:$MAC_DEST"

if [ $? -eq 0 ]; then
    echo ""
    echo "Push completed successfully!"
    echo "Destination: $MAC_USER@$MAC_HOST:$MAC_DEST"
else
    echo ""
    echo "Push failed with errors."
    exit 1
fi
