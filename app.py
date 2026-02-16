from flask import Flask, render_template, request, redirect, url_for, flash, session
import subprocess
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- Timezone ---------------- #
TZ = ZoneInfo("Australia/Perth")

# ---------------- Paths ---------------- #
SPIDERS_FOLDER = os.path.abspath("core/spiders")
SCRAPY_PROJECT_PATH = os.path.abspath(".")

SPIDERS = [
    f.replace(".py", "")
    for f in os.listdir(SPIDERS_FOLDER)
    if f.endswith(".py") and "init" not in f
]

running_spiders = {}

# ---------------- Scheduler ---------------- #
scheduler = BackgroundScheduler(timezone=TZ)
scheduler.start()

# ---------------- Theme ---------------- #
@app.before_request
def set_default_theme():
    if "theme" not in session:
        session["theme"] = "light"

@app.route("/toggle-theme", methods=["POST"])
def toggle_theme():
    session["theme"] = "dark" if session.get("theme") == "light" else "light"
    return redirect(url_for("index"))

# ---------------- Spider utils ---------------- #
def is_running(spider_name):
    if spider_name in running_spiders:
        proc = running_spiders[spider_name]
        if proc.poll() is None:
            return True
        else:
            del running_spiders[spider_name]
    return False

def run_spider_job(spider_name, start_t=None, end_t=None):
    """Run spider only inside allowed time window"""
    now = datetime.now(TZ).time()
    if start_t and end_t and not (start_t <= now <= end_t):
        return  # outside allowed window
    if not is_running(spider_name):
        proc = subprocess.Popen(
            ["scrapy", "crawl", spider_name, "--logfile", f"auto/%(name)s_%(time)s.log", "-o", "-o exports/%(name)s_%(time)s.csv"],
            cwd=SCRAPY_PROJECT_PATH,
        )
        running_spiders[spider_name] = proc

# ---------------- Routes ---------------- #
@app.route("/")
def index():
    spider_status = {sp: is_running(sp) for sp in SPIDERS}

    # Build schedule info
    jobs_info = {}
    for spider in SPIDERS:
        job = scheduler.get_job(f"{spider}_job")
        if job:
            jobs_info[spider] = {
                "next_run": job.next_run_time.astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None,
                "schedule_type": job.name,
            }
        else:
            jobs_info[spider] = None

    theme = session.get("theme", "light")

    return render_template(
        "index.html",
        spiders=SPIDERS,
        status=spider_status,
        jobs_info=jobs_info,
        theme=theme,
    )

@app.route("/run/<spider_name>", methods=["POST"])
def run_spider(spider_name):
    run_spider_job(spider_name)
    flash(f"{spider_name} started!", "success")
    return redirect(url_for("index"))

@app.route("/stop/<spider_name>", methods=["POST"])
def stop_spider(spider_name):
    if is_running(spider_name):
        proc = running_spiders[spider_name]
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
        del running_spiders[spider_name]
        flash(f"{spider_name} stopped!", "success")
    else:
        flash("Not running", "warning")
    return redirect(url_for("index"))

@app.route("/schedule/<spider_name>", methods=["POST"])
def schedule_spider(spider_name):
    schedule_type = request.form.get("schedule")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    job_id = f"{spider_name}_job"

    # Remove existing job
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    start_t = datetime.strptime(start_time, "%H:%M").time() if start_time else None
    end_t = datetime.strptime(end_time, "%H:%M").time() if end_time else None

    # Interval triggers
    if schedule_type == "10min":
        trigger = IntervalTrigger(minutes=10)
    elif schedule_type == "15min":
        trigger = IntervalTrigger(minutes=15)
    elif schedule_type == "30min":
        trigger = IntervalTrigger(minutes=30)
    # Cron triggers
    elif schedule_type == "daily":
        trigger = CronTrigger(hour=start_t.hour, minute=start_t.minute)
    elif schedule_type == "weekly":
        trigger = CronTrigger(day_of_week="mon", hour=start_t.hour, minute=start_t.minute)
    elif schedule_type == "monthly":
        trigger = CronTrigger(day=1, hour=start_t.hour, minute=start_t.minute)
    else:
        flash("Invalid schedule", "error")
        return redirect(url_for("index"))

    scheduler.add_job(
        run_spider_job,
        trigger,
        args=[spider_name, start_t, end_t],
        id=job_id,
        name=schedule_type,
        replace_existing=True,
        max_instances=1,
    )

    flash(f"{spider_name} scheduled ({schedule_type})", "success")
    return redirect(url_for("index"))

@app.route("/unschedule/<spider_name>", methods=["POST"])
def unschedule_spider(spider_name):
    job_id = f"{spider_name}_job"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        flash("Schedule removed", "success")
    else:
        flash("No schedule found", "warning")
    return redirect(url_for("index"))

# ---------------- Run ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0",port="80",use_reloader=False)
