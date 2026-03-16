import os
import time
from datetime import datetime, timedelta

# ================= CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FOLDERS_TO_CLEAN = [
    os.path.join(BASE_DIR, "exports"),
    os.path.join(BASE_DIR, "auto"),
]

FILE_EXTENSIONS = (".csv", ".log")
KEEP_DAYS = 1

RUN_HOUR = 2      # 02:00 AM
RUN_MINUTE = 0
# ==========================================


def clean_old_files():
    now = datetime.now()
    cutoff = now - timedelta(days=KEEP_DAYS)

   
    for folder in FOLDERS_TO_CLEAN:
        if not os.path.exists(folder):
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)

            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                )

                if file_mtime < cutoff:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(
                            f"[ERROR] Could not delete {file_path}: {e}\n"
                        )


if __name__ == "__main__":

    print("Cleaner scheduler started...")
    print(f"Runs daily at {RUN_HOUR:02d}:{RUN_MINUTE:02d}")
    print(f"Keeping files for {KEEP_DAYS} days")
    print("Press Ctrl+C to exit")

    while True:
        clean_old_files()
        time.sleep(60*60*5)