from django.core.mail import send_mail
from django.conf import settings
import requests
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

def send_email_alert(incident):
    if 'your-' in settings.EMAIL_HOST_USER:
        logger.info(f"MOCK Email sent for incident {incident.id}")
        return True # Mock success

    subject = f"Incident Alert: {incident.description}"
    message = f"An incident occurred at {incident.timestamp}.\n\nTemperature: {incident.dht_reading.temp}°C\nDescription: {incident.description}\n\nPlease acknowledge this incident immediately."
    # recipient_list = [settings.EMAIL_HOST_USER]
    recipient_list = ["ayo11ub10@gmail.com"]
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        logger.info(f"Email sent for incident {incident.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_telegram_alert(incident):
    if 'your-' in settings.TELEGRAM_BOT_TOKEN:
        logger.info(f"MOCK Telegram sent for incident {incident.id}")
        return True

    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    message = f"🚨 *Incident Alert* 🚨\n\nTemp: {incident.dht_reading.temp}°C\nTime: {incident.timestamp}\nStatus: Unresolved\n\nPlease check the dashboard!"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        response = requests.post(url, data={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'})
        if response.status_code == 200:
            logger.info(f"Telegram sent for incident {incident.id}")
            return True
        else:
            logger.error(f"Telegram failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to send Telegram: {e}")
        return False

def make_phone_call(incident):
    if 'your-' in settings.TELEGRAM_USERNAME:
        logger.info(f"MOCK CallMeBot call for incident {incident.id}")
        return True

    username = settings.TELEGRAM_USERNAME
    message = f"Alert! Temperature incident. {incident.description}. Please acknowledge."
    # URL encode the message
    encoded_message = requests.utils.quote(message)
    url = f"https://api.callmebot.com/start.php?user=@{username}&text={encoded_message}&lang=en-US-Standard-C&rpt=2"
    
    try:
        response = requests.get(url)
        if response.status_code == 200 and "Success" in response.text:
             logger.info(f"CallMeBot initiated for incident {incident.id}")
             return True
        elif "User not authorized" in response.text:
             logger.error(f"CallMeBot Auth Failed: You must authorize the bot. See dashboard/logs.")
             return False
        else:
             logger.error(f"CallMeBot failed: {response.text}")
             return False
    except Exception as e:
        logger.error(f"Failed to make CallMeBot call: {e}")
        return False

def notify_supervisors(incident):
    logger.warning(f"ESCALATION: Notify supervisors for incident {incident.id}")
    return True
