import os
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# ================= CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FOLDERS_TO_CLEAN = [
    os.path.join(BASE_DIR, "exports"),
    os.path.join(BASE_DIR, "auto"),
]

FILE_EXTENSIONS = (".csv", ".log")
KEEP_DAYS = 2
LOG_FILE = os.path.join(BASE_DIR, "cleaner.log")

RUN_HOUR = 2      # 02:00 AM
RUN_MINUTE = 0
# ==========================================


def clean_old_files():
    now = datetime.now()
    cutoff = now - timedelta(days=KEEP_DAYS)

    with open(LOG_FILE, "a") as log:
        log.write(f"\n===== Cleaning started at {now} =====\n")

        for folder in FOLDERS_TO_CLEAN:
            if not os.path.exists(folder):
                log.write(f"[WARNING] Folder not found: {folder}\n")
                continue

            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)

                if os.path.isfile(file_path):
                    file_mtime = datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    )

                    if file_mtime < cutoff:
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            log.write(
                                f"[DELETED] {file_path} "
                                f"(Size: {round(file_size/1024,2)} KB)\n"
                            )
                        except Exception as e:
                            log.write(
                                f"[ERROR] Could not delete {file_path}: {e}\n"
                            )

        log.write(f"===== Cleaning finished at {datetime.now()} =====\n")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        clean_old_files,
        CronTrigger(hour=RUN_HOUR, minute=RUN_MINUTE),
        id="daily_file_cleaner",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()

    print("Cleaner scheduler started...")
    print(f"Runs daily at {RUN_HOUR:02d}:{RUN_MINUTE:02d}")
    print(f"Keeping files for {KEEP_DAYS} days")
    print("Press Ctrl+C to exit")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")