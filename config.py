import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration for the Groww Reviews Analyzer Application
CONFIG = {
    # Review source configuration - Groww investment app
    "REVIEW_SOURCE_URL": "https://play.google.com/store/apps/details?id=com.nextbillion.groww",
    
    # Date range for reviews (in weeks)
    "REVIEW_PERIOD_WEEKS": 12,
    
    # Themes for categorization
    "THEMES": [
        "Investment Experience",
        "Payment, Banking and Money Flow",
        "Loans and Insurance Experience",
        "Customer Support, Service and Trust",
        "App performance, Usability & Reliability"
    ],
    
    # Theme descriptions for better classification
    "THEME_DESCRIPTIONS": {
        "Investment Experience": "Reviews related to Mutual fund investment process, Stock trading experience, Order execution speed, portfolio display and accuracy, SIP experience etc.",
        "Payment, Banking and Money Flow": "Reviews related to UPI deposits, Withdrawals to bank account, Settlement time, KYC and onboarding experience, Bank linking, payment failures, Auto-pay/SIP payment etc",
        "Loans and Insurance Experience": "Reviews related to Loan approval process, credit limit accuracy, interest charges, repayment handling, insurance buying experience, claims support, document verification.",
        "Customer Support, Service and Trust": "Reviews related to Help center experience, chatbot/agent responsiveness, issue resolution speed, problem solving attitude, Transparency of charges, Trust & Security, Communication quality during outages",
        "App performance, Usability & Reliability": "Reviews related to App Speed, login issues, bugs and crashes, UI clarity, Dark mode, charts and navigation, overall experience of using the app etc."
    },
    
    # Output settings
    "OUTPUT_DIR": "output",
    "MAX_WORD_COUNT": 250,
    
    # Email settings
    "EMAIL_RECIPIENT": "product-team@groww.in",
    "EMAIL_SENDER": "weekly-pulse@groww.in"
}