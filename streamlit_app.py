"""
Streamlit dashboard for the Groww Reviews Analyzer Application
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import base64

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
        # Convert to dictionary format
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
        st.error(f"Error loading review data: {e}")
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
        st.error(f"Error parsing pulse report: {e}")
        return {}

def get_table_download_link(df, filename):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

def get_sentiment_color(rating):
    """Return color based on rating"""
    if rating >= 4:
        return "#00C853"  # Green for positive
    elif rating >= 3:
        return "#FFD600"  # Yellow for neutral
    else:
        return "#D50000"  # Red for negative

def main():
    # Custom CSS for investment app theme
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #00d09c, #00b386);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        height: 150px;
        border: 1px solid #e9ecef;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00d09c;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        font-weight: 500;
    }
    
    .theme-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #00d09c;
    }
    
    .quote-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #00d09c;
    }
    
    .action-card {
        background: #e8f5e9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #4caf50;
    }
    
    .review-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .rating-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        color: white;
    }
    
    .theme-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        background: #00d09c;
        color: white;
        margin-bottom: 10px;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.9rem;
        margin-top: 30px;
    }
    
    .pulse-title {
        color: #00d09c;
        border-bottom: 2px solid #00d09c;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.set_page_config(
        page_title="Groww Reviews Analyzer",
        page_icon="📈",
        layout="wide"
    )
    
    # Header with investment theme
    st.markdown("""
    <div class="main-header">
        <h1>📈 Groww Investment App Review Analyzer</h1>
        <p>Data-driven insights from customer feedback to enhance your investment experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    reviews = load_review_data()
    pulse_data = parse_pulse_report()
    
    # Get theme distribution
    theme_counts = {}
    if reviews:
        for review in reviews:
            theme = review['theme']
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Enhanced key metrics with icons and better styling
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">📋</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Reviews Analyzed</div>
        </div>
        """.format(len(reviews)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">🏷️</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Business Themes</div>
        </div>
        """.format(len(theme_counts)), unsafe_allow_html=True)
    
    with col3:
        avg_rating = sum([r['rating'] for r in reviews]) / len(reviews) if reviews else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">⭐</div>
            <div class="metric-value">{:.1f}</div>
            <div class="metric-label">Average Rating</div>
        </div>
        """.format(avg_rating), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Theme distribution chart with investment colors
    if theme_counts:
        st.subheader("📊 Theme Distribution Analysis")
        fig = px.bar(
            x=list(theme_counts.keys()),
            y=list(theme_counts.values()),
            labels={'x': 'Business Themes', 'y': 'Number of Reviews'},
            color=list(theme_counts.keys()),
            color_discrete_sequence=['#00d09c', '#ff6b35', '#3b82f6', '#8b5cf6', '#f59e0b']
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, width='stretch')
    
    # Pulse report sections with improved styling
    st.markdown('<h2 class="pulse-title">Weekly Pulse Report Insights</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎯 Top Themes", "💬 Key Quotes", "🚀 Action Ideas"])
    
    with tab1:
        st.markdown("### Business Themes Identified")
        if pulse_data.get('themes'):
            for theme in pulse_data['themes']:
                st.markdown(f"""
                <div class="theme-card">
                    <h4>{theme['name']}</h4>
                    <p>{theme['description']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No themes data available")
    
    with tab2:
        st.markdown("### Customer Voice")
        if pulse_data.get('quotes'):
            for i, quote in enumerate(pulse_data['quotes']):
                st.markdown(f"""
                <div class="quote-card">
                    <p><strong>#{i+1}</strong> {quote}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No quotes data available")
    
    with tab3:
        st.markdown("### Recommended Actions")
        if pulse_data.get('actions'):
            for i, action in enumerate(pulse_data['actions']):
                st.markdown(f"""
                <div class="action-card">
                    <p><strong>Action #{i+1}:</strong> {action}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No action ideas available")
    
    # Recent reviews with enhanced styling
    st.markdown('<h2 class="pulse-title">Recent Customer Reviews</h2>', unsafe_allow_html=True)
    if reviews:
        # Show first 10 reviews with enhanced styling
        for review in reviews[:10]:
            rating_color = get_sentiment_color(review['rating'])
            st.markdown(f"""
            <div class="review-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4>{review['title']}</h4>
                        <div class="theme-badge">{review['theme']}</div>
                        <p>{review['text']}</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="rating-badge" style="background-color: {rating_color};">
                            ⭐ {review['rating']}/5
                        </div>
                        <div style="font-size: 0.9rem; color: #666; margin-top: 10px;">
                            {review['date']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Download button for full dataset
        df_reviews = pd.DataFrame(reviews)
        st.markdown(get_table_download_link(df_reviews, "classified_reviews.csv"), unsafe_allow_html=True)
    else:
        st.info("No reviews data available")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Groww Reviews Analyzer • Powered by ML/NLP Technology</p>
        <p>Analyze customer feedback to drive product excellence in investment services</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()