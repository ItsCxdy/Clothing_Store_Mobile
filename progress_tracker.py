import json
import os
from datetime import date, datetime

DATA_FILE = 'targets.json'

def today_str():
    """Get today's date as ISO string."""
    return date.today().isoformat()

def load_targets():
    """Load targets from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_targets(targets):
    """Save targets to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(targets, f, indent=4)

def add_target(name, deadline_str):
    """Add a new target with deadline."""
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        target = {
            'name': name,
            'deadline': deadline_str,
            'progress_logs': []
        }
        targets = load_targets()
        targets.append(target)
        save_targets(targets)
        print(f"Added target '{name}' with deadline {deadline_str}")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD")

def log_daily_progress(target_name, progress_pct):
    """Log daily progress for a target. Prevents duplicate logs for the same day."""
    try:
        pct = float(progress_pct)
        if not 0 <= pct <= 100:
            raise ValueError("Progress must be 0-100")
    except ValueError as e:
        print(f"Invalid progress: {e}")
        return
    
    today = today_str()
    targets = load_targets()
    for target in targets:
        if target['name'] == target_name:
            # Check if already logged today
            if any(log['date'] == today for log in target['progress_logs']):
                print(f"Progress already logged for '{target_name}' today.")
                return
            
            target['progress_logs'].append({
                'date': today,
                'progress': pct
            })
            save_targets(targets)
            print(f"Logged {pct}% progress for '{target_name}' on {today}")
            return
    print(f"Target '{target_name}' not found.")

def show_summary():
    """Show summary of completed vs pending tasks."""
    targets = load_targets()
    today = date.today()
    completed = 0
    pending = 0
    
    print("\n=== Progress Summary ===")
    for target in targets:
        logs = target['progress_logs']
        deadline_str = target['deadline']
        deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        
        if logs:
            latest_progress = logs[-1]['progress']
            if latest_progress >= 100 or deadline_date < today:
                status = "Completed/Overdue"
                completed += 1
            else:
                status = f"Pending ({latest_progress}%)"
                pending += 1
            print(f"'{target['name']}': {status} (Deadline: {deadline_str})")
        else:
            if deadline_date < today:
                status = "Overdue (no progress)"
                completed += 1
            else:
                status = "Pending (no progress)"
                pending += 1
            print(f"'{target['name']}': {status} (Deadline: {deadline_str})")
    
    total = len(targets)
    print(f"\nCompleted/Overdue: {completed}, Pending: {pending} (Total: {total})")
    print("======================\n")

def main():
    """Simple CLI menu."""
    while True:
        print("\nOptions:")
        print("1. Add target")
        print("2. Log daily progress")
        print("3. Show summary")
        print("4. Quit")
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == '1':
            name = input("Target name: ").strip()
            deadline = input("Deadline (YYYY-MM-DD): ").strip()
            add_target(name, deadline)
        elif choice == '2':
            name = input("Target name: ").strip()
            progress = input("Progress percentage (0-100): ").strip()
            log_daily_progress(name, progress)
        elif choice == '3':
            show_summary()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
