# backend/lottery_scheduler.py
"""
Scheduler to run lottery scraper daily at 4:45pm Vietnam time
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from backend.lottery_scraper import scrape_and_save
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def start_scheduler():
    """
    Start the background scheduler
    Runs daily at 4:45pm Vietnam time (ICT/Asia/Ho_Chi_Minh)
    """
    scheduler = BackgroundScheduler()
    vietnam_tz = timezone('Asia/Ho_Chi_Minh')
    
    # Schedule for 4:45pm Vietnam time
    scheduler.add_job(
        scrape_and_save,
        trigger=CronTrigger(hour=16, minute=45, timezone=vietnam_tz),
        id='lottery_scraper',
        name='Daily Lottery Scraper',
        replace_existing=True
    )
    
    scheduler.start()
    logging.info("Lottery scheduler started - will run daily at 4:45pm Vietnam time")
    
    return scheduler

# For testing only
if __name__ == "__main__":
    scheduler = start_scheduler()
    
    # Keep the script running
    try:
        import time
        
        logging.info("\nScheduler is running. Press Ctrl+C to stop.\n")
        
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logging.error("\nScheduler stopped")