import os
import re
import time
from datetime import datetime
from collections import defaultdict
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# ==============================
# CONFIG
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDERS_TO_CLEAN = [
    os.path.join(BASE_DIR, "exports"),
    os.path.join(BASE_DIR, "auto"),
]

# Set to False to simulate (no delete)
DELETE_FILES = True

# ==============================
# CLEANER LOGIC
# ==============================

pattern = re.compile(
    r"^(?P<prefix>.+)_(?P<date>\d{4}-\d{2}-\d{2})_(?P<time>\d{2}:\d{2}:\d{2})\.csv$"
)


def clean_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"[!] Folder not found: {folder_path}")
        return

    print(f"\nCleaning folder: {folder_path}")

    files_grouped = defaultdict(list)

    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match:
            prefix = match.group("prefix")
            date = match.group("date")
            time_part = match.group("time")

            dt = datetime.strptime(
                f"{date} {time_part}", "%Y-%m-%d %H:%M:%S"
            )

            key = (prefix, date)
            files_grouped[key].append((dt, filename))

    deleted_count = 0

    for key, file_list in files_grouped.items():
        file_list.sort(reverse=True)  # newest first
        latest = file_list[0]

        for _, old_file in file_list[1:]:
            file_path = os.path.join(folder_path, old_file)

            if DELETE_FILES:
                os.remove(file_path)
                print(f"Deleted: {old_file}")
            else:
                print(f"Would delete: {old_file}")

            deleted_count += 1

    print(f"Finished {folder_path} → Deleted {deleted_count} files")


def run_cleaner():
    print(f"\n===== Running Cleaner at {datetime.now()} =====")
    for folder in FOLDERS_TO_CLEAN:
        clean_folder(folder)
    print("===== Cleaner Finished =====\n")


# ==============================
# DAILY SCHEDULER
# ==============================

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Run daily at 02:00 AM
    scheduler.add_job(
        run_cleaner,
        CronTrigger(hour=2, minute=0),
        id="daily_csv_cleaner",
        replace_existing=True,
    )

    print("Daily CSV cleaner started (runs at 02:00 AM)")
    run_cleaner()  # Optional: run once immediately
    scheduler.start()