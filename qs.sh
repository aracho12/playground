#!/usr/bin/env bash
# qs - pretty qstat formatter
# Usage: qs [-path] [-t] [-all] [qstat options]

GREEN='\033[32m'; YELLOW='\033[33m'; CYAN='\033[36m'; RESET='\033[0m'; BOLD='\033[1m'

show_path=0; show_time=0
qstat_args=()
for arg in "$@"; do
    case "$arg" in
        -path) show_path=1 ;;
        -t)    show_time=1 ;;
        -all)  show_path=1; show_time=1 ;;
        *)     qstat_args+=("$arg") ;;
    esac
done

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

epoch_to_date() {
    local ep=$1
    date -d "@$ep" '+%m/%d %H:%M' 2>/dev/null || date -r "$ep" '+%m/%d %H:%M'
}

# Print header based on mode
print_header() {
    if (( show_path && show_time )); then
        printf "${BOLD}%-12s %-20s %-3s %11s %5s  %-14s  %-14s  %s${RESET}\n" \
            "Job ID" "Name" "S" "Used" "%" "Queue" "Ends" "Path"
        printf '%0.s─' {1..100}; echo
    elif (( show_path )); then
        printf "${BOLD}%-12s %-20s %-3s %11s %5s  %-14s  %s${RESET}\n" \
            "Job ID" "Name" "S" "Used" "%" "Queue" "Path"
        printf '%0.s─' {1..90}; echo
    elif (( show_time )); then
        printf "${BOLD}%-12s %-20s %-3s %11s %5s  %-14s  %s${RESET}\n" \
            "Job ID" "Name" "S" "Used" "%" "Queue" "Ends"
        printf '%0.s─' {1..75}; echo
    else
        printf "${BOLD}%-12s %-20s %-3s %11s %11s %5s  %s${RESET}\n" \
            "Job ID" "Name" "S" "Used" "Limit" "%" "Queue"
        printf '%0.s─' {1..75}; echo
    fi
}

print_job() {
    [[ -z "$job_id" ]] && return
    local used_sec; used_sec=$(parse_sec "$used")
    local lim_sec;  lim_sec=$(parse_sec "$limit")
    local used_fmt; used_fmt=$(fmt_dur "$used_sec")
    local pct="-"
    (( lim_sec > 0 )) && pct="$(( used_sec * 100 / lim_sec ))%"

    local color=$RESET
    [[ "$state" == "R" ]] && color=$GREEN
    [[ "$state" == "Q" ]] && color=$YELLOW

    # End time for R jobs
    local end_str="-"
    if [[ "$state" == "R" && $lim_sec -gt 0 ]]; then
        local now_sec; now_sec=$(date +%s)
        local remaining=$(( lim_sec - used_sec ))
        local end_epoch=$(( now_sec + remaining ))
        end_str=$(epoch_to_date "$end_epoch")
    fi

    if (( show_path && show_time )); then
        printf "%-12s %-20s ${color}%-3s${RESET} %11s %5s  %-14s  ${CYAN}%-14s${RESET}  %s\n" \
            "${job_id%%.*}" "${name:0:20}" "$state" \
            "$used_fmt" "$pct" "$queue" "$end_str" "$workdir"
    elif (( show_path )); then
        printf "%-12s %-20s ${color}%-3s${RESET} %11s %5s  %-14s  %s\n" \
            "${job_id%%.*}" "${name:0:20}" "$state" \
            "$used_fmt" "$pct" "$queue" "$workdir"
    elif (( show_time )); then
        printf "%-12s %-20s ${color}%-3s${RESET} %11s %5s  %-14s  ${CYAN}%s${RESET}\n" \
            "${job_id%%.*}" "${name:0:20}" "$state" \
            "$used_fmt" "$pct" "$queue" "$end_str"
    else
        local lim_fmt; (( lim_sec > 0 )) && lim_fmt=$(fmt_dur "$lim_sec") || lim_fmt="-"
        printf "%-12s %-20s ${color}%-3s${RESET} %11s %11s %5s  %s\n" \
            "${job_id%%.*}" "${name:0:20}" "$state" \
            "$used_fmt" "$lim_fmt" "$pct" "$queue"
    fi
}

print_header

job_id="" name="" state="" queue="" used="" limit="" workdir=""
total=0; r_count=0; q_count=0

while IFS= read -r line; do
    line="${line#"${line%%[![:space:]]*}"}"   # ltrim
    case "$line" in
        Job\ Id:*)
            print_job
            job_id="${line#Job Id: }"
            name="" state="" queue="" used="" limit="" workdir="" ;;
        Job_Name\ =\ *)    name="${line#Job_Name = }" ;;
        job_state\ =\ *)
            state="${line#job_state = }"
            case "$state" in
                R) (( r_count++ )); (( total++ )) ;;
                Q) (( q_count++ )); (( total++ )) ;;
                *) (( total++ )) ;;
            esac ;;
        queue\ =\ *)       queue="${line#queue = }" ;;
        resources_used.walltime\ =\ *) used="${line#resources_used.walltime = }" ;;
        Resource_List.walltime\ =\ *)  limit="${line#Resource_List.walltime = }" ;;
        Variable_List\ =\ *)
            varlist="${line#Variable_List = }"
            # PBS_O_WORKDIR may be split across continuation lines; grab what's here
            workdir=$(echo "$varlist" | tr ',' '\n' | grep '^PBS_O_WORKDIR=' | cut -d= -f2-)
            ;;
        # continuation: Variable_List can wrap; detect PBS_O_WORKDIR on wrapped lines
        PBS_O_WORKDIR=*)
            [[ -z "$workdir" ]] && workdir="${line#PBS_O_WORKDIR=}" ;;
    esac
done < <(qstat -f "${qstat_args[@]}")

print_job

# Footer
if (( show_path && show_time )); then
    printf '%0.s─' {1..100}; echo
elif (( show_path || show_time )); then
    printf '%0.s─' {1..90}; echo
else
    printf '%0.s─' {1..75}; echo
fi

printf "${BOLD}Total: %d  |  ${GREEN}R: %d${RESET}${BOLD}  |  ${YELLOW}Q: %d${RESET}${BOLD}  |  %s${RESET}\n" \
    "$total" "$r_count" "$q_count" "$(date '+%Y-%m-%d %H:%M:%S')"
