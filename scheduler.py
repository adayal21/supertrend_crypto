import schedule
import time
import os
import sys

from engine import run_portfolio
from logger import logger


def job():

    logger.info(
        "\n"
        "##################################################\n"
        "SCHEDULER EXECUTION STARTED\n"
        "##################################################"
    )

    try:

        run_portfolio()

    except Exception as e:

        logger.error(
            f"Scheduler error: {e}"
        )


# ==========================================================
# RUN IMMEDIATELY ON STARTUP
# ==========================================================

LOCK_FILE = "scheduler.lock"

if os.path.exists(LOCK_FILE):

    print("Scheduler already running.")

    sys.exit()

with open(LOCK_FILE, "w") as f:

    f.write("running")

job()

# ==========================================================
# RUN EVERY HOUR AT :01
# ==========================================================

schedule.every().hour.at(":01").do(job)

logger.info("Scheduler started")

try:

    while True:

        schedule.run_pending()

        time.sleep(1)

except KeyboardInterrupt:

    if os.path.exists(LOCK_FILE):

        os.remove(LOCK_FILE)

    print("Scheduler stopped.")