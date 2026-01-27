#!/usr/bin/env bash

# Cancel running job in current folder using Slurm job id from out.o<jobid>

set -u

# Get job id: from argument or from out.o* file in current directory
get_jobid() {
  if [[ $# -ge 1 ]]; then
    echo "$1"
    return 0
  fi

  shopt -s nullglob
  local candidates=(out.o*)
  shopt -u nullglob

  if [[ ${#candidates[@]} -eq 0 ]]; then
    echo "No out.o* file found in current directory." >&2
    return 1
  elif [[ ${#candidates[@]} -gt 1 ]]; then
    echo "Multiple out.o* files found. Please specify job id explicitly." >&2
    printf '  %s\n' "${candidates[@]}" >&2
    return 1
  fi

  local f="${candidates[0]}"
  # Expect filename like out.o666975
  local jobid="${f#out.o}"

  if [[ -z "$jobid" || "$jobid" == "$f" ]]; then
    echo "Failed to parse job id from $f" >&2
    return 1
  fi

  echo "$jobid"
}

main() {
  local jobid
  if ! jobid="$(get_jobid "$@")"; then
    exit 1
  fi

  echo "Job ID: $jobid"
  echo

  # Show current job status from squeue
  if ! command -v squeue >/dev/null 2>&1; then
    echo "squeue command not found. Cannot show job status." >&2
  else
    echo "=== squeue output ==="
    squeue -j "$jobid"
    echo "====================="
  fi

  # Confirm cancellation
  printf "이 job 을 삭제할까요? (y/N): "
  read -r answer

  case "$answer" in
    y|Y|yes|YES)
      ;;
    *)
      echo "취소하지 않았습니다."
      exit 0
      ;;
  esac

  # Ask for reason/comment
  printf "취소 이유 또는 코멘트를 입력하세요 (한 줄): "
  read -r reason

  # Create CANCELLED file with the reason
  {
    printf "%s\n" "$reason"
  } > CANCELLED

  echo "Created file 'CANCELLED' with the provided reason."

  # Actually cancel the job (Slurm)
  if command -v scancel >/dev/null 2>&1; then
    if scancel "$jobid"; then
      echo "Job $jobid has been cancelled."
    else
      echo "Failed to cancel job $jobid with scancel." >&2
      exit 1
    fi
  else
    echo "scancel command not found. Job was NOT cancelled on scheduler." >&2
    exit 1
  fi
}

main "$@"

