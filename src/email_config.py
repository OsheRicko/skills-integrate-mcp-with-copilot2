"""
Email Configuration Module

This module handles email service configuration using environment variables
for secure credential management.
"""

import os
from typing import Optional
from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_email_config() -> ConnectionConfig:
    """
    Get email connection configuration from environment variables.
    
    Environment Variables:
        MAIL_USERNAME: Email account username
        MAIL_PASSWORD: Email account password
        MAIL_FROM: Sender email address
        MAIL_PORT: SMTP port (default: 587)
        MAIL_SERVER: SMTP server (default: smtp.gmail.com)
        MAIL_TLS: Use TLS (default: True)
        MAIL_SSL: Use SSL (default: False)
    
    Returns:
        ConnectionConfig: FastAPI Mail connection configuration
    """
    return ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME", "noreply@mergington.edu"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
        MAIL_FROM=os.getenv("MAIL_FROM", "noreply@mergington.edu"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_STARTTLS=os.getenv("MAIL_TLS", "True").lower() == "true",
        MAIL_SSL_TLS=os.getenv("MAIL_SSL", "False").lower() == "true",
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER="./src/email_templates"
    )


def is_email_enabled() -> bool:
    """
    Check if email service is properly configured.
    
    Returns:
        bool: True if email credentials are set, False otherwise
    """
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    return bool(username and password)
