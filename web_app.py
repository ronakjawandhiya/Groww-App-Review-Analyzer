"""
Web interface for the Groww Reviews Analyzer Application
"""
import os
import pandas as pd
from flask import Flask, render_template, jsonify, send_file
from datetime import datetime
import json

app = Flask(__name__)

# Configuration
OUTPUT_DIR = "output"
DATA_FILE = os.path.join(OUTPUT_DIR, "classified_reviews.csv")
PULSE_FILE = None

# Find the latest pulse file
if os.path.exists(OUTPUT_DIR):
    pulse_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("weekly_pulse_") and f.endswith(".md")]
    if pulse_files:
        # Sort by date and get the most recent
        pulse_files.sort(reverse=True)
        PULSE_FILE = os.path.join(OUTPUT_DIR, pulse_files[0])

def load_review_data():
    """Load review data from CSV file"""
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        df = pd.read_csv(DATA_FILE)
        # Convert to dictionary format for JSON serialization
        reviews = []
        for _, row in df.iterrows():
            reviews.append({
                'review_id': row.get('review_id', ''),
                'title': row.get('title', ''),
                'text': row.get('text', ''),
                'date': row.get('date', ''),
                'rating': row.get('rating', 0),
                'theme': row.get('theme', ''),
                'confidence': row.get('confidence', 0),
                'classification_reason': row.get('classification_reason', '')
            })
        return reviews
    except Exception as e:
        print(f"Error loading review data: {e}")
        return []

def parse_pulse_report():
    """Parse the pulse report markdown file"""
    if not PULSE_FILE or not os.path.exists(PULSE_FILE):
        return {}
    
    try:
        with open(PULSE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        
        # Parse the report
        report_data = {
            'title': '',
            'overview': '',
            'themes': [],
            'quotes': [],
            'actions': []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('# '):
                report_data['title'] = line[2:]
            elif line.startswith('**Overview:**'):
                report_data['overview'] = line.replace('**Overview:**', '').strip()
            elif line.startswith('**Top Themes:**'):
                current_section = 'themes'
            elif line.startswith('**Key Quotes:**'):
                current_section = 'quotes'
            elif line.startswith('**Action Ideas:**'):
                current_section = 'actions'
            elif line.startswith('- ') and current_section:
                if current_section == 'themes':
                    # Parse theme line
                    theme_text = line[2:]  # Remove "- "
                    if ':' in theme_text:
                        theme_name, theme_desc = theme_text.split(':', 1)
                        report_data['themes'].append({
                            'name': theme_name.strip(),
                            'description': theme_desc.strip()
                        })
                elif current_section == 'quotes':
                    report_data['quotes'].append(line[2:])  # Remove "- "
                elif current_section == 'actions':
                    report_data['actions'].append(line[2:])  # Remove "- "
        
        return report_data
    except Exception as e:
        print(f"Error parsing pulse report: {e}")
        return {}

@app.route('/')
def index():
    """Main dashboard page"""
    # Load data
    reviews = load_review_data()
    pulse_data = parse_pulse_report()
    
    # Get theme distribution
    theme_counts = {}
    if reviews:
        for review in reviews:
            theme = review['theme']
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Prepare data for charts
    chart_data = {
        'labels': list(theme_counts.keys()),
        'values': list(theme_counts.values())
    }
    
    return render_template('dashboard.html', 
                         reviews=reviews[:10],  # Show first 10 reviews
                         pulse_data=pulse_data,
                         chart_data=chart_data,
                         total_reviews=len(reviews))

@app.route('/api/reviews')
def api_reviews():
    """API endpoint for reviews data"""
    reviews = load_review_data()
    return jsonify(reviews)

@app.route('/api/pulse')
def api_pulse():
    """API endpoint for pulse report data"""
    pulse_data = parse_pulse_report()
    return jsonify(pulse_data)

@app.route('/api/themes')
def api_themes():
    """API endpoint for theme distribution"""
    reviews = load_review_data()
    theme_counts = {}
    if reviews:
        for review in reviews:
            theme = review['theme']
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
    return jsonify(theme_counts)

@app.route('/download/pulse')
def download_pulse():
    """Download the pulse report"""
    if PULSE_FILE and os.path.exists(PULSE_FILE):
        return send_file(PULSE_FILE, as_attachment=True)
    return "Pulse report not found", 404

@app.route('/download/csv')
def download_csv():
    """Download the classified reviews CSV"""
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True)
    return "CSV file not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)