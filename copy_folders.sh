#!/bin/bash
#
# copy_folders.sh
# 지정한 source 경로에서 qm_*, mm_* 폴더(+추가 지정 폴더)를
# 현재 디렉토리로 복사하고, 복사 용량을 표시합니다.
#
# 사용법:
#   ./copy_folders.sh <SOURCE_PATH> [추가폴더1] [추가폴더2] ...
#
# 예시:
#   ./copy_folders.sh /scratch/x3379a03/.../export
#   ./copy_folders.sh /scratch/x3379a03/.../export solute
#

set -euo pipefail

# --- 인자 확인 ---
if [ "$#" -lt 1 ]; then
    echo "사용법: $0 <SOURCE_PATH> [추가폴더 ...]"
    echo "예시:   $0 /scratch/x3379a03/.../export solute"
    exit 1
fi

SRC="$1"
shift  # 나머지 인자는 추가로 복사할 폴더 이름
EXTRA=("$@")

DEST="$(pwd)"

# --- source 경로 존재 확인 ---
if [ ! -d "$SRC" ]; then
    echo "오류: source 경로가 존재하지 않습니다 -> $SRC"
    exit 1
fi

echo "Source: $SRC"
echo "Dest:   $DEST"
echo "----------------------------------------"

shopt -s nullglob   # 매칭되는 폴더가 없으면 패턴을 빈 값으로 처리

# --- 복사 대상 목록 구성: qm_*, mm_* + 추가 폴더 ---
# (${EXTRA[@]+...} 형태는 빈 배열에서도 set -u 에러가 나지 않음)
targets=("$SRC"/qm_* "$SRC"/mm_*)
for name in ${EXTRA[@]+"${EXTRA[@]}"}; do
    targets+=("$SRC/$name")
done

# --- 복사 실행 ---
count=0
for src_path in "${targets[@]}"; do
    base="$(basename "$src_path")"
    if [ -d "$src_path" ]; then
        cp -r "$src_path" "$DEST/"
        size="$(du -sh "$DEST/$base" | cut -f1)"
        printf "  [OK]   %-12s %s\n" "$base" "$size"
        count=$((count + 1))
    else
        printf "  [SKIP] %-12s (source에 폴더 없음)\n" "$base"
    fi
done

echo "----------------------------------------"
if [ "$count" -eq 0 ]; then
    echo "복사할 폴더를 찾지 못했습니다."
else
    echo "완료: $count 개 폴더 복사."
    { du -ch "$DEST"/qm_* "$DEST"/mm_* ${EXTRA[@]+"${EXTRA[@]/#/$DEST/}"} 2>/dev/null || true; } \
        | tail -1 | awk '{print "총 용량: "$1}'
fi
