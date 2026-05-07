import logging

import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_verification_sms(mobile, code):
    """Send OTP verification code via SMS"""
    return _send_sms(mobile, "your-app-template", token=code)


@shared_task
def send_success_enrollment_lead_sms(mobile, name):
    """Send enrollment confirmation SMS"""
    return _send_sms(mobile, "your-app-template", token=name)


def _send_sms(receptor, template, token=None, token2=None, token3=None):
    """Internal function to send SMS via SMS gateway"""
    api_key = getattr(settings, "SMS_API_KEY", None)
    
    if not api_key:
        logger.error("SMS_API_KEY is not configured")
        return None
    
    url = f"https://api.smsgateway.com/v1/{api_key}/verify/lookup.json"
    payload = {"receptor": receptor, "template": template}
    
    if token:
        payload["token"] = str(token)
    if token2:
        payload["token2"] = str(token2)
    if token3:
        payload["token3"] = str(token3)
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("return", {}).get("status") == 200:
                logger.info(f"SMS sent to {receptor}")
                return response
            else:
                logger.error(f"API error: {result}")
        else:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException:
        logger.error(f"Network error sending SMS to {receptor}", exc_info=True)
    
    return None
