# Groww Reviews Analyzer

An application that analyzes Groww product reviews and generates weekly pulse reports with actionable insights.

## Features

- Automated import of Groww app reviews from Google Play Store
- ML-driven classification into 5 business themes
- Weekly pulse report generation in Markdown
- Real email sending or draft creation
- Cron-like scheduling via `scheduler.py`

## Prerequisites

- Python 3.7+
- Internet connection (for model downloads)

## Installation

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in a `.env` file:
   ```env
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

## Usage

### Run Once
```bash
python main.py [--weeks N] [--max-reviews M]
```

### Schedule Weekly Runs
```bash
python scheduler.py --day monday --hour 9
```

## Google Play Store Reviews Integration

This application fetches real Google Play Store reviews using the free `google-play-scraper` library:

- No API key required
- Direct access to Google Play Store reviews
- Automatic fallback to sample data if scraping fails

The library is already included in the requirements.txt file and will be installed automatically.

## Output Files

- `raw_reviews.csv`: Raw scraped reviews
- `classified_reviews.csv`: Reviews with theme classifications
- `weekly_pulse_YYYYMMDD.md`: Generated pulse report
- `email_draft.txt`: Email draft if sending fails
- `app.log`: Application logs

## Themes

Reviews are classified into exactly 5 themes:
1. Investment Experience
2. Payment, Banking and Money Flow
3. Loans and Insurance Experience
4. Customer Support, Service and Trust
5. App performance, Usability & Reliability

## How to Rerun for a New Week

1. Simply run the application again:
   ```bash
   python main.py
   ```

2. The application will automatically:
   - Fetch the latest reviews from the previous week
   - Classify them into themes using ML/NLP
   - Generate a new pulse report
   - Send a real email or create an updated email draft

## Architecture

The application follows a 4-layer architecture:

1. **Data Import & Validation Layer**
   - Scraper for public Groww reviews from Google Play Store
   - Schema validator
   - PII detector
   - Deduplication mechanism

2. **Theme Extraction & Classification Layer**
   - Embedding generation using transformer models
   - Zero-shot classification with BART model
   - Theme labeling
   - Theme limit enforcement

3. **Content Generation Layer**
   - Quote extraction
   - Theme summarization
   - Action idea generation
   - Pulse document assembly

4. **Distribution & Feedback Layer**
   - Email template rendering
   - PII final check
   - Delivery system with SMTP
   - Read receipt tracker (optional)

## Security & Compliance

- Uses prompt and post-processing filters to redact PII
- Only uses publicly accessible endpoints for review import
- Groups themes and output structure are hardcoded for privacy
- No persistent storage of PII

## Customization

To customize the application:

1. Modify theme definitions in `config.py`
2. Adjust the review source URL in `config.py`
3. Update classification keywords in `theme_classifier.py`
4. Modify action idea templates in `pulse_generator.py`

## Advanced Features

### ML/NLP-Based Classification
The application uses state-of-the-art transformer models for:
- Zero-shot classification with Facebook's BART model
- Sentence embeddings with MiniLM
- Confidence scoring for classifications

### Real Email Sending
When email credentials are provided:
- Sends emails via SMTP with TLS encryption
- Supports attachments
- Comprehensive error handling

### Robust Error Handling
- Detailed logging to both file and console
- Graceful degradation when services fail
- Comprehensive exception handling

### Web Scraping
- Uses Selenium WebDriver for dynamic content
- Headless Chrome for background operation
- Automatic driver management with WebDriver Manager

## Limitations

Current limitations include:
- Google Play Store scraping may be affected by UI changes
- ML models require internet connectivity for first run (downloads models)
- Email sending requires proper SMTP configuration

## Troubleshooting

Common issues and solutions:

1. **Chrome WebDriver Issues**: Make sure Chrome is installed and up to date
2. **ML Model Downloads**: First run may take longer due to model downloads
3. **Email Sending**: Ensure you're using an App Password for Gmail
4. **Rate Limiting**: Google Play Store may rate limit requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.