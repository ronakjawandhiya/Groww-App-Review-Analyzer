"""
Scheduler module for automating the Groww Reviews Analyzer
"""
import schedule
import time
import logging
from datetime import datetime
import argparse

from main import main

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_weekly_analysis():
    """
    Run the weekly analysis process
    """
    logger.info("Starting scheduled weekly analysis...")
    try:
        # Run analysis for the previous week
        main(weeks_back=1, max_reviews=100)
        logger.info("Scheduled weekly analysis completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled weekly analysis: {e}")


def setup_schedule(run_time="monday", run_hour=9, run_minute=0):
    """
    Set up the weekly schedule
    
    Args:
        run_time (str): Day of week to run (e.g., "monday", "tuesday")
        run_hour (int): Hour to run (0-23)
        run_minute (int): Minute to run (0-59)
    """
    # Schedule the job
    if run_time.lower() == "monday":
        schedule.every().monday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    elif run_time.lower() == "tuesday":
        schedule.every().tuesday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    elif run_time.lower() == "wednesday":
        schedule.every().wednesday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    elif run_time.lower() == "thursday":
        schedule.every().thursday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    elif run_time.lower() == "friday":
        schedule.every().friday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    elif run_time.lower() == "saturday":
        schedule.every().saturday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    elif run_time.lower() == "sunday":
        schedule.every().sunday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    else:
        # Default to Monday
        schedule.every().monday.at(f"{run_hour:02d}:{run_minute:02d}").do(run_weekly_analysis)
    
    logger.info(f"Scheduled weekly analysis for {run_time.capitalize()} at {run_hour:02d}:{run_minute:02d}")


def run_scheduler(run_time="monday", run_hour=9, run_minute=0):
    """
    Run the scheduler indefinitely
    
    Args:
        run_time (str): Day of week to run (e.g., "monday", "tuesday")
        run_hour (int): Hour to run (0-23)
        run_minute (int): Minute to run (0-59)
    """
    logger.info("Starting Groww Reviews Analyzer Scheduler...")
    
    # Set up the schedule
    setup_schedule(run_time, run_hour, run_minute)
    
    # Run the scheduler
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduler: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schedule Groww Reviews Analyzer")
    parser.add_argument("--day", type=str, default="monday", 
                        help="Day of week to run (default: monday)")
    parser.add_argument("--hour", type=int, default=9,
                        help="Hour to run (0-23, default: 9)")
    parser.add_argument("--minute", type=int, default=0,
                        help="Minute to run (0-59, default: 0)")
    
    args = parser.parse_args()
    
    run_scheduler(args.day, args.hour, args.minute)