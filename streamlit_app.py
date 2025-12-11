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

def main():
    st.set_page_config(
        page_title="Groww Reviews Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    # Load data
    reviews = load_review_data()
    pulse_data = parse_pulse_report()
    
    # Get theme distribution
    theme_counts = {}
    if reviews:
        for review in reviews:
            theme = review['theme']
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Main title
    st.title("🌱 Groww Reviews Analyzer Dashboard")
    st.markdown("---")
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Reviews Analyzed", len(reviews))
    
    with col2:
        st.metric("Themes Identified", len(pulse_data.get('themes', [])))
    
    with col3:
        st.metric("Key Quotes", len(pulse_data.get('quotes', [])))
    
    st.markdown("---")
    
    # Theme distribution chart
    if theme_counts:
        st.subheader("Theme Distribution")
        fig = px.bar(
            x=list(theme_counts.keys()),
            y=list(theme_counts.values()),
            labels={'x': 'Themes', 'y': 'Number of Reviews'},
            color=list(theme_counts.keys()),
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Pulse report sections
    st.subheader("Weekly Pulse Report Insights")
    
    tab1, tab2, tab3 = st.tabs(["Top Themes", "Key Quotes", "Action Ideas"])
    
    with tab1:
        if pulse_data.get('themes'):
            for theme in pulse_data['themes']:
                st.markdown(f"**{theme['name']}**")
                st.markdown(f"{theme['description']}")
                st.markdown("---")
        else:
            st.info("No themes data available")
    
    with tab2:
        if pulse_data.get('quotes'):
            for i, quote in enumerate(pulse_data['quotes']):
                st.markdown(f"{i+1}. {quote}")
        else:
            st.info("No quotes data available")
    
    with tab3:
        if pulse_data.get('actions'):
            for i, action in enumerate(pulse_data['actions']):
                st.markdown(f"{i+1}. {action}")
        else:
            st.info("No action ideas available")
    
    # Recent reviews
    st.subheader("Recent Reviews")
    if reviews:
        df_reviews = pd.DataFrame(reviews)
        st.dataframe(df_reviews[['title', 'text', 'date', 'rating', 'theme']].head(10))
        
        # Download button for full dataset
        st.markdown(get_table_download_link(df_reviews, "classified_reviews.csv"), unsafe_allow_html=True)
    else:
        st.info("No reviews data available")
    
    # Footer
    st.markdown("---")
    st.caption("Groww Reviews Analyzer • Powered by ML/NLP Technology")

if __name__ == "__main__":
    main()