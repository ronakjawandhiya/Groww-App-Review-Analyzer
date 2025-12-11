"""
Module for classifying Groww product reviews into predefined themes using ML/NLP
"""
import pandas as pd
from datetime import datetime
import re
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from tqdm import tqdm

from config import CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize sentence transformer model for embedding generation
try:
    # Using a lightweight transformer model for embeddings
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Transformer model loaded successfully")
except Exception as e:
    logger.error(f"Error loading transformer model: {e}")
    tokenizer, model = None, None

# Initialize zero-shot classification pipeline
try:
    classifier = pipeline("zero-shot-classification", 
                         model="facebook/bart-large-mnli",
                         device=0 if torch.cuda.is_available() else -1)
    logger.info("Zero-shot classifier loaded successfully")
except Exception as e:
    logger.error(f"Error loading zero-shot classifier: {e}")
    classifier = None


def get_embeddings(texts):
    """
    Generate embeddings for a list of texts using transformer model
    
    Args:
        texts (list): List of text strings
        
    Returns:
        numpy.ndarray: Array of embeddings
    """
    if not tokenizer or not model:
        logger.warning("Transformer model not available, using fallback method")
        return None
        
    try:
        # Tokenize texts
        encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
        
        # Generate embeddings
        with torch.no_grad():
            model_output = model(**encoded_input)
        
        # Use mean pooling to get sentence embeddings
        embeddings = model_output.last_hidden_state.mean(dim=1).numpy()
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return None


def classify_review_theme_ml(review_title, review_text):
    """
    Classify a single review into one of the predefined themes using ML/NLP
    
    Args:
        review_title (str): Title of the review
        review_text (str): Text content of the review
        
    Returns:
        tuple: (theme, confidence_score, reason)
    """
    # Combine title and text for analysis
    full_text = f"{review_title} {review_text}"
    
    # If transformer models are available, use them
    if classifier:
        try:
            # Use zero-shot classification
            candidate_labels = CONFIG["THEMES"]
            result = classifier(full_text, candidate_labels)
            
            best_theme = result['labels'][0]
            confidence = result['scores'][0]
            reason = f"Zero-shot classification confidence: {confidence:.2f}"
            
            return best_theme, confidence, reason
        except Exception as e:
            logger.warning(f"Zero-shot classification failed: {e}")
    
    # Fallback to keyword-based classification
    return classify_review_theme_keyword(review_title, review_text)


def classify_review_theme_keyword(review_title, review_text):
    """
    Classify a single review into one of the predefined themes using keyword matching
    
    Args:
        review_title (str): Title of the review
        review_text (str): Text content of the review
        
    Returns:
        tuple: (theme, confidence_score, reason)
    """
    # Combine title and text for analysis
    full_text = f"{review_title} {review_text}".lower()
    
    # Theme keywords for classification
    theme_keywords = {
        "Investment Experience": [
            "mutual fund", "investment", "portfolio", "sip", "trading", 
            "order execution", "fund performance", "investing", "mf", 
            "buy fund", "sell fund", "fund purchase"
        ],
        "Payment, Banking and Money Flow": [
            "upi", "payment", "bank", "withdrawal", "deposit", "kyc",
            "onboarding", "settlement", "autopay", "transaction",
            "bank account", "banking", "money transfer"
        ],
        "Loans and Insurance Experience": [
            "loan", "credit", "interest", "repayment", "insurance", 
            "claim", "emi", "borrow", "lending", "credit limit",
            "loan approval", "insurance policy"
        ],
        "Customer Support, Service and Trust": [
            "support", "help center", "chatbot", "agent", "resolution",
            "trust", "security", "communication", "service", "customer care",
            "helpdesk", "assistance", "problem solved"
        ],
        "App performance, Usability & Reliability": [
            "app", "crash", "bug", "speed", "ui", "navigation", 
            "dark mode", "interface", "performance", "usability",
            "slow", "lag", "freeze", "user experience"
        ]
    }
    
    # Count keyword matches for each theme
    theme_scores = {}
    for theme, keywords in theme_keywords.items():
        score = 0
        matched_keywords = []
        for keyword in keywords:
            # Count occurrences of each keyword
            matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', full_text))
            if matches > 0:
                score += matches
                matched_keywords.append(keyword)
        
        theme_scores[theme] = {
            "score": score,
            "matched_keywords": matched_keywords
        }
    
    # Find the theme with the highest score
    best_theme = max(theme_scores, key=lambda x: theme_scores[x]["score"])
    best_score = theme_scores[best_theme]["score"]
    
    # If no keywords matched, default to App performance theme
    if best_score == 0:
        best_theme = "App performance, Usability & Reliability"
        reason = "Default classification for general app feedback"
    else:
        matched_keywords = theme_scores[best_theme]["matched_keywords"]
        reason = f"Matched keywords: {', '.join(matched_keywords[:3])}"
    
    # Confidence score based on number of matched keywords
    confidence = min(best_score / 5.0, 1.0)  # Cap at 1.0
    
    return best_theme, confidence, reason


def classify_reviews(reviews_df):
    """
    Classify all reviews in a DataFrame into themes using ML/NLP
    
    Args:
        reviews_df (pandas.DataFrame): DataFrame containing reviews
        
    Returns:
        pandas.DataFrame: DataFrame with added theme classification columns
    """
    if reviews_df.empty:
        return reviews_df
    
    logger.info(f"Classifying {len(reviews_df)} reviews...")
    
    # Apply classification to each review with progress bar
    classifications = []
    for _, row in tqdm(reviews_df.iterrows(), total=len(reviews_df), desc="Classifying reviews"):
        theme, confidence, reason = classify_review_theme_ml(
            row.get('cleaned_title', ''), 
            row.get('cleaned_text', '')
        )
        classifications.append((theme, confidence, reason))
    
    # Add classification results to DataFrame
    reviews_df['theme'] = [cls[0] for cls in classifications]
    reviews_df['confidence'] = [cls[1] for cls in classifications]
    reviews_df['classification_reason'] = [cls[2] for cls in classifications]
    
    logger.info("Classification completed")
    return reviews_df


def get_theme_statistics(classified_reviews):
    """
    Get statistics about theme distribution
    
    Args:
        classified_reviews (pandas.DataFrame): DataFrame with theme classifications
        
    Returns:
        dict: Theme distribution statistics
    """
    if classified_reviews.empty:
        return {}
    
    theme_counts = classified_reviews['theme'].value_counts()
    total_reviews = len(classified_reviews)
    
    stats = {}
    for theme in CONFIG["THEMES"]:
        count = theme_counts.get(theme, 0)
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        stats[theme] = {
            "count": count,
            "percentage": round(percentage, 2)
        }
    
    return stats


# For testing purposes
if __name__ == "__main__":
    # Sample data for testing
    sample_data = {
        "review_id": ["1", "2", "3"],
        "title": ["Great investment platform", "Payment failed", "App crashes"],
        "text": [
            "Mutual fund investments are smooth",
            "UPI payment failed multiple times",
            "App keeps crashing on portfolio page"
        ],
        "cleaned_title": ["Great investment platform", "Payment failed", "App crashes"],
        "cleaned_text": [
            "Mutual fund investments are smooth",
            "UPI payment failed multiple times",
            "App keeps crashing on portfolio page"
        ]
    }
    
    df = pd.DataFrame(sample_data)
    classified_df = classify_reviews(df)
    print(classified_df[['title', 'theme']])