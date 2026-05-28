#!/usr/bin/env bash
# qs - pretty qstat formatter
# Usage: qs [qstat options]

GREEN='\033[32m'; YELLOW='\033[33m'; RESET='\033[0m'; BOLD='\033[1m'

parse_sec() {
    local t="$1"
    [[ -z "$t" ]] && echo 0 && return
    IFS=: read -r h m s <<< "$t"
    printf '%d' $(( 10#${h:-0} * 3600 + 10#${m:-0} * 60 + 10#${s:-0} ))
}

fmt_dur() {
    local sec=$1
    local d=$(( sec / 86400 ))
    local h=$(( (sec % 86400) / 3600 ))
    local m=$(( (sec % 3600) / 60 ))
    (( d > 0 )) && printf "%dd %02dh %02dm" $d $h $m && return
    (( h > 0 )) && printf "%dh %02dm" $h $m && return
    printf "%dm" $m
}

print_job() {
    [[ -z "$job_id" ]] && return
    local used_sec=$(parse_sec "$used")
    local lim_sec=$(parse_sec "$limit")
    local used_fmt; used_fmt=$(fmt_dur "$used_sec")
    local lim_fmt; (( lim_sec > 0 )) && lim_fmt=$(fmt_dur "$lim_sec") || lim_fmt="-"
    local pct="-"
    (( lim_sec > 0 )) && pct="$(( used_sec * 100 / lim_sec ))%"

    local color=$RESET
    [[ "$state" == "R" ]] && color=$GREEN
    [[ "$state" == "Q" ]] && color=$YELLOW

    printf "%-12s %-20s ${color}%-3s${RESET} %11s %11s %5s  %s\n" \
        "${job_id%%.*}" "${name:0:20}" "$state" \
        "$used_fmt" "$lim_fmt" "$pct" "$queue"
}

printf "${BOLD}%-12s %-20s %-3s %11s %11s %5s  %s${RESET}\n" \
    "Job ID" "Name" "S" "Used" "Limit" "%" "Queue"
printf '%0.s─' {1..75}; echo

job_id="" name="" state="" queue="" used="" limit=""

while IFS= read -r line; do
    line="${line#"${line%%[![:space:]]*}"}"   # ltrim
    case "$line" in
        Job\ Id:*)       print_job
                         job_id="${line#Job Id: }"
                         name="" state="" queue="" used="" limit="" ;;
        Job_Name\ =\ *)  name="${line#Job_Name = }" ;;
        job_state\ =\ *) state="${line#job_state = }" ;;
        queue\ =\ *)     queue="${line#queue = }" ;;
        resources_used.walltime\ =\ *) used="${line#resources_used.walltime = }" ;;
        Resource_List.walltime\ =\ *)  limit="${line#Resource_List.walltime = }" ;;
    esac
done < <(qstat -f "$@")

print_job

printf '%0.s─' {1..75}; echo
total=0; r_count=0; q_count=0
while IFS= read -r line; do
    line="${line#"${line%%[![:space:]]*}"}"
    case "$line" in
        job_state\ =\ R) (( r_count++ )); (( total++ )) ;;
        job_state\ =\ Q) (( q_count++ )); (( total++ )) ;;
        job_state\ =\ *) (( total++ )) ;;
    esac
done < <(qstat -f "$@")
printf "${BOLD}Total: %d  |  ${GREEN}R: %d${RESET}${BOLD}  |  ${YELLOW}Q: %d${RESET}${BOLD}  |  %s${RESET}\n" \
    "$total" "$r_count" "$q_count" "$(date '+%Y-%m-%d %H:%M:%S')"