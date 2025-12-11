"""
Main entry point for the Groww Reviews Analyzer Application
"""
import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
import pandas as pd
import traceback

from config import CONFIG
from review_scraper import scrape_reviews
from theme_classifier import classify_reviews
from pulse_generator import generate_weekly_pulse
from email_sender import send_email_draft

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(CONFIG["OUTPUT_DIR"], "app.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main(weeks_back=1, max_reviews=100):
    """
    Main function to run the Groww Reviews Analyzer
    
    Args:
        weeks_back (int): Number of weeks back to analyze (default: 1 for previous week)
        max_reviews (int): Maximum number of reviews to process
    """
    try:
        logger.info("Starting Groww Reviews Analyzer...")
        
        # Create output directory if it doesn't exist
        os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)
        
        # Step 1: Scrape reviews
        logger.info("Step 1: Scraping reviews...")
        try:
            reviews_df = scrape_reviews(weeks_back, max_reviews)
        except Exception as e:
            logger.error(f"Failed to scrape reviews: {e}")
            logger.error("A compatible browser is required for scraping. Please install Chrome, Edge, or Firefox.")
            return
        
        if reviews_df.empty:
            logger.warning("No reviews found for the specified period.")
            return
        
        logger.info(f"Found {len(reviews_df)} reviews")
        
        # Save raw reviews to CSV
        csv_path = os.path.join(CONFIG["OUTPUT_DIR"], "raw_reviews.csv")
        try:
            reviews_df.to_csv(csv_path, index=False)
            logger.info(f"Raw reviews saved to {csv_path}")
        except Exception as e:
            logger.error(f"Error saving raw reviews CSV: {e}")
        
        # Step 2: Classify reviews into themes
        logger.info("Step 2: Classifying reviews into themes...")
        try:
            classified_reviews = classify_reviews(reviews_df)
        except Exception as e:
            logger.error(f"Error classifying reviews: {e}")
            logger.error(traceback.format_exc())
            return
        
        # Save classified reviews
        classified_path = os.path.join(CONFIG["OUTPUT_DIR"], "classified_reviews.csv")
        try:
            classified_reviews.to_csv(classified_path, index=False)
            logger.info(f"Classified reviews saved to {classified_path}")
        except Exception as e:
            logger.error(f"Error saving classified reviews CSV: {e}")
        
        # Step 3: Generate weekly pulse report
        logger.info("Step 3: Generating weekly pulse report...")
        try:
            pulse_report = generate_weekly_pulse(classified_reviews)
        except Exception as e:
            logger.error(f"Error generating pulse report: {e}")
            logger.error(traceback.format_exc())
            return
        
        # Save pulse report
        pulse_path = os.path.join(CONFIG["OUTPUT_DIR"], f"weekly_pulse_{datetime.now().strftime('%Y%m%d')}.md")
        try:
            with open(pulse_path, 'w', encoding='utf-8') as f:
                f.write(pulse_report)
            logger.info(f"Weekly pulse report saved to {pulse_path}")
        except Exception as e:
            logger.error(f"Error saving pulse report: {e}")
        
        # Step 4: Send email draft
        logger.info("Step 4: Preparing email draft...")
        email_content = f"""Subject: Weekly Groww Product Pulse Report - {datetime.now().strftime('%Y-%m-%d')}

Hello Team,

Please find attached the weekly pulse report for Groww product reviews.

This report summarizes:
- Top 3 themes from customer reviews
- Key customer quotes
- Actionable insights

Best regards,
Groww Product Analytics
"""
        
        try:
            success = send_email_draft(
                recipient=CONFIG["EMAIL_RECIPIENT"],
                subject=f"Weekly Groww Product Pulse Report - {datetime.now().strftime('%Y-%m-%d')}",
                body=email_content,
                attachment_path=pulse_path
            )
            
            if success:
                logger.info("Email draft prepared successfully")
            else:
                logger.error("Failed to prepare email draft")
        except Exception as e:
            logger.error(f"Error preparing email draft: {e}")
            logger.error(traceback.format_exc())
        
        logger.info("\nProcess completed successfully!")
        logger.info(f"Outputs saved in: {os.path.abspath(CONFIG['OUTPUT_DIR'])}")
        
    except Exception as e:
        logger.error(f"Unexpected error in main process: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Groww product reviews and generate weekly pulse report")
    parser.add_argument("--weeks", type=int, default=1, 
                        help="Number of weeks back to analyze (default: 1)")
    parser.add_argument("--max-reviews", type=int, default=100,
                        help="Maximum number of reviews to process (default: 100)")
    
    args = parser.parse_args()
    main(args.weeks, args.max_reviews)