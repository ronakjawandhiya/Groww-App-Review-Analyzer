"""
Module for sending email drafts with pulse reports
"""
import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import ssl

from config import CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_email_message(sender, recipient, subject, body, attachment_path=None):
    """
    Create an email message with optional attachment
    
    Args:
        sender (str): Sender email address
        recipient (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
        attachment_path (str, optional): Path to file to attach
        
    Returns:
        MIMEMultipart: Email message object
    """
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    
    # Add body to email
    msg.attach(MIMEText(body, 'plain'))
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename= {os.path.basename(attachment_path)}",
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Error attaching file {attachment_path}: {e}")
    
    return msg


def send_email_smtp(sender_email, sender_password, recipient_email, subject, body, smtp_server="smtp.gmail.com", smtp_port=587, attachment_path=None):
    """
    Send an email using SMTP
    
    Args:
        sender_email (str): Sender email address
        sender_password (str): Sender email password or app password
        recipient_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP server port
        attachment_path (str, optional): Path to file to attach
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if credentials are dummy/test credentials
    if sender_email == 'test@example.com' and sender_password == 'dummy_password':
        logger.info("Test credentials detected. Saving as draft instead of sending real email.")
        return save_email_draft(recipient_email, subject, body, attachment_path)
    
    try:
        # Create email message
        message = create_email_message(sender_email, recipient_email, subject, body, attachment_path)
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(sender_email, sender_password)
        
        # Send email
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        # If sending fails, save as draft
        logger.info("Saving as draft due to sending failure...")
        return save_email_draft(recipient_email, subject, body, attachment_path)


def save_email_draft(recipient, subject, body, attachment_path=None):
    """
    Save an email draft to a file (simulating email sending)
    
    Args:
        recipient (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
        attachment_path (str, optional): Path to file to attach
        
    Returns:
        bool: True if successful, False otherwise
    """
    # In a real implementation, this would connect to an email service
    # For now, we'll just save the draft to a file
    
    draft_content = f"To: {recipient}\n"
    draft_content += f"Subject: {subject}\n"
    draft_content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    draft_content += body
    
    if attachment_path and os.path.exists(attachment_path):
        draft_content += f"\n\nAttachment: {os.path.basename(attachment_path)}"
    
    # Save draft
    draft_path = os.path.join(CONFIG["OUTPUT_DIR"], "email_draft.txt")
    try:
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)
        logger.info(f"Email draft saved to: {draft_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving email draft: {e}")
        return False


def send_email_draft(recipient=None, subject=None, body=None, attachment_path=None):
    """
    Send an email draft using configured settings or save as draft if config missing
    
    Args:
        recipient (str, optional): Recipient email address
        subject (str, optional): Email subject
        body (str, optional): Email body content
        attachment_path (str, optional): Path to file to attach
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Use provided values or defaults from config
    recipient = recipient or CONFIG.get("EMAIL_RECIPIENT", "product-team@groww.in")
    sender = CONFIG.get("EMAIL_SENDER", "weekly-pulse@groww.in")
    subject = subject or f"Weekly Groww Product Pulse Report - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Check if email credentials are configured
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if email_user and email_password:
        # Send real email or save as draft if test credentials
        logger.info("Email credentials configured. Attempting to send email...")
        return send_email_smtp(
            sender_email=email_user,
            sender_password=email_password,
            recipient_email=recipient,
            subject=subject,
            body=body or "Please find attached the weekly pulse report.",
            attachment_path=attachment_path
        )
    else:
        # Save as draft
        logger.info("Email credentials not configured. Saving as draft...")
        return save_email_draft(recipient, subject, body or "Please find attached the weekly pulse report.", attachment_path)


# For testing purposes
if __name__ == "__main__":
    # Test the email functionality
    success = send_email_draft(
        recipient="product-team@groww.in",
        subject="Test Email",
        body="This is a test email body."
    )
    
    if success:
        print("Email draft created successfully")
    else:
        print("Failed to create email draft")