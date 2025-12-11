"""
Module for generating weekly pulse reports from classified reviews
"""
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import re

from config import CONFIG


def get_top_themes(classified_reviews, top_n=3):
    """
    Get the top N themes by review count
    
    Args:
        classified_reviews (pandas.DataFrame): DataFrame with classified reviews
        top_n (int): Number of top themes to return
        
    Returns:
        list: List of top themes
    """
    if classified_reviews.empty:
        return []
    
    theme_counts = Counter(classified_reviews['theme'])
    top_themes = [theme for theme, _ in theme_counts.most_common(top_n)]
    
    return top_themes


def extract_key_quotes(classified_reviews, theme, max_quotes=3):
    """
    Extract key quotes for a specific theme
    
    Args:
        classified_reviews (pandas.DataFrame): DataFrame with classified reviews
        theme (str): Theme to extract quotes for
        max_quotes (int): Maximum number of quotes to return
        
    Returns:
        list: List of key quotes
    """
    # Filter reviews for the specific theme
    theme_reviews = classified_reviews[classified_reviews['theme'] == theme]
    
    if theme_reviews.empty:
        return []
    
    # Sort by confidence and date (newest first)
    theme_reviews = theme_reviews.sort_values(['confidence', 'date'], ascending=[False, False])
    
    # Extract quotes (title + text)
    quotes = []
    for _, review in theme_reviews.head(max_quotes).iterrows():
        quote = f"{review.get('cleaned_title', '')}. {review.get('cleaned_text', '')}"
        # Truncate if too long
        if len(quote) > 150:
            quote = quote[:147] + "..."
        quotes.append(quote)
    
    return quotes


def generate_action_ideas(theme, review_count):
    """
    Generate action ideas for a theme
    
    Args:
        theme (str): Theme to generate actions for
        review_count (int): Number of reviews for this theme
        
    Returns:
        list: List of action ideas
    """
    action_templates = {
        "Investment Experience": [
            "Improve portfolio loading speed and accuracy",
            "Enhance SIP setup flow with clearer guidance",
            "Add more educational content for new investors"
        ],
        "Payment, Banking and Money Flow": [
            "Optimize UPI payment flow to reduce failures",
            "Streamline KYC process with better error handling",
            "Improve bank linking success rate"
        ],
        "Loans and Insurance Experience": [
            "Reduce loan approval turnaround time",
            "Simplify insurance claim process with status tracking",
            "Improve document verification experience"
        ],
        "Customer Support, Service and Trust": [
            "Reduce first response time for support tickets",
            "Implement proactive communication during outages",
            "Add self-service options for common issues"
        ],
        "App performance, Usability & Reliability": [
            "Fix critical app crashes reported in reviews",
            "Optimize app performance on low-end devices",
            "Improve navigation flow based on user feedback"
        ]
    }
    
    # Get template actions for the theme
    actions = action_templates.get(theme, [
        f"Conduct detailed analysis of {review_count} {theme.lower()} issues",
        f"Prioritize {theme.lower()} improvements in next sprint",
        f"Gather more user feedback on {theme.lower()} pain points"
    ])
    
    return actions[:3]


def generate_weekly_pulse(classified_reviews):
    """
    Generate a weekly pulse report from classified reviews
    
    Args:
        classified_reviews (pandas.DataFrame): DataFrame with classified reviews
        
    Returns:
        str: Formatted pulse report
    """
    if classified_reviews.empty:
        return "# Weekly Product Pulse Report\n\nNo reviews found for this period."
    
    # Get date range
    date_range = f"{classified_reviews['date'].min()} to {classified_reviews['date'].max()}"
    
    # Get top 3 themes
    top_themes = get_top_themes(classified_reviews, 3)
    
    # Generate report title
    report_title = f"Weekly Product Pulse: {date_range}"
    
    # Generate overview
    total_reviews = len(classified_reviews)
    overview = f"This week, we analyzed {total_reviews} customer reviews. The top themes highlight key areas for improvement and celebration."
    
    # Generate theme summaries
    theme_summaries = []
    all_quotes = []
    all_actions = []
    
    for i, theme in enumerate(top_themes, 1):
        # Get reviews for this theme
        theme_reviews = classified_reviews[classified_reviews['theme'] == theme]
        review_count = len(theme_reviews)
        
        # Generate sentiment summary
        avg_rating = theme_reviews['rating'].mean() if 'rating' in theme_reviews.columns else 3.5
        if avg_rating >= 4:
            sentiment = "positive"
        elif avg_rating >= 3:
            sentiment = "mixed"
        else:
            sentiment = "negative"
        
        summary = f"{sentiment.capitalize()} feedback on {theme.lower()}. Key issues identified."
        theme_summaries.append({
            "name": theme,
            "summary": summary
        })
        
        # Extract key quotes
        quotes = extract_key_quotes(classified_reviews, theme, 1)  # One quote per theme
        for quote in quotes:
            all_quotes.append(f"- [{theme}] {quote}")
        
        # Generate action ideas
        actions = generate_action_ideas(theme, review_count)
        for action in actions:
            all_actions.append(f"- {action}")
    
    # Create the report
    report_lines = [
        f"# {report_title}",
        "",
        f"**Overview:** {overview}",
        "",
        "**Top Themes:**"
    ]
    
    for summary in theme_summaries:
        report_lines.append(f"- {summary['name']}: {summary['summary']}")
    
    report_lines.extend([
        "",
        "**Key Quotes:**"
    ])
    
    report_lines.extend(all_quotes[:3])  # Limit to 3 quotes total
    
    report_lines.extend([
        "",
        "**Action Ideas:**"
    ])
    
    report_lines.extend(all_actions[:3])  # Limit to 3 actions total
    
    report_lines.extend([
        "",
        "---",
        "*Report generated automatically from customer reviews*",
        f"*Period: {date_range}*"
    ])
    
    return "\n".join(report_lines)


# For testing purposes
if __name__ == "__main__":
    # Sample data for testing
    sample_data = {
        "review_id": ["1", "2", "3", "4", "5"],
        "title": [
            "Great investment platform", 
            "Payment failed", 
            "App crashes",
            "Support response slow",
            "Portfolio inaccurate"
        ],
        "text": [
            "Mutual fund investments are smooth",
            "UPI payment failed multiple times",
            "App keeps crashing on portfolio page",
            "Support response took 3 days",
            "Portfolio value mismatch"
        ],
        "cleaned_title": [
            "Great investment platform", 
            "Payment failed", 
            "App crashes",
            "Support response slow",
            "Portfolio inaccurate"
        ],
        "cleaned_text": [
            "Mutual fund investments are smooth",
            "UPI payment failed multiple times",
            "App keeps crashing on portfolio page",
            "Support response took 3 days",
            "Portfolio value mismatch"
        ],
        "date": [
            "2023-10-01",
            "2023-10-02",
            "2023-10-03",
            "2023-10-04",
            "2023-10-05"
        ],
        "rating": [5, 2, 1, 3, 2],
        "theme": [
            "Investment Experience",
            "Payment, Banking and Money Flow",
            "App performance, Usability & Reliability",
            "Customer Support, Service and Trust",
            "Investment Experience"
        ]
    }
    
    df = pd.DataFrame(sample_data)
    report = generate_weekly_pulse(df)
    print(report)