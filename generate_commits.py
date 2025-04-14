import os
import random
from datetime import datetime, timedelta
import subprocess

def run_command(command):
    subprocess.run(command, shell=True, check=True)

# Set the date range
start_date = datetime(2025, 4, 7)
end_date = datetime(2025, 4, 13)

# Generate commits for each day
current_date = start_date
while current_date <= end_date:
    # Generate 5-12 commits for this day
    num_commits = random.randint(5, 12)
    
    # Generate commits throughout the day
    for i in range(num_commits):
        # Create a random time during the day (between 9 AM and 5 PM)
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        commit_time = current_date.replace(hour=hour, minute=minute, second=second)
        
        # Create a dummy file with the commit message
        with open('commit.txt', 'w') as f:
            f.write(f'Commit from {commit_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Stage the file
        run_command('git add commit.txt')
        
        # Create the commit with the specific date
        env = os.environ.copy()
        env['GIT_AUTHOR_DATE'] = commit_time.strftime('%Y-%m-%d %H:%M:%S')
        env['GIT_COMMITTER_DATE'] = commit_time.strftime('%Y-%m-%d %H:%M:%S')
        
        subprocess.run(
            'git commit -m "Update commit.txt"',
            shell=True,
            env=env,
            check=True
        )
    
    # Move to next day
    current_date += timedelta(days=1)

# Clean up
if os.path.exists('commit.txt'):
    os.remove('commit.txt') 