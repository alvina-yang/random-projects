#!/bin/bash

# Start date
start_date="2025-03-21"
end_date="2025-04-05"

# Convert dates to timestamps
start_ts=$(date -j -f "%Y-%m-%d" "$start_date" "+%s")
end_ts=$(date -j -f "%Y-%m-%d" "$end_date" "+%s")

current_ts=$start_ts

while [ $current_ts -le $end_ts ]; do
    current_date=$(date -j -f "%s" $current_ts "+%Y-%m-%d")
    
    # Generate random number of commits for this day (4-11)
    num_commits=$((RANDOM % 8 + 4))
    
    echo "Creating $num_commits commits for $current_date"
    
    for i in $(seq 1 $num_commits); do
        echo "Commit $i for $current_date" >> commit_history.txt
        git add commit_history.txt
        GIT_AUTHOR_DATE="$current_date 12:00:00" GIT_COMMITTER_DATE="$current_date 12:00:00" git commit -m "Commit $i for $current_date"
    done
    
    # Move to next day
    current_ts=$((current_ts + 86400))
done

echo "All commits created. Now modifying commit dates..." 