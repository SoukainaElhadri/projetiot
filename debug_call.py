import os
import django
import requests
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from django.conf import settings

def test_call():
    username = settings.TELEGRAM_USERNAME
    print(f"Testing call to Telegram Username: {username}")
    
    message = "This is a test call from your IoT Incident System."
    encoded_message = requests.utils.quote(message)
    
    url = f"http://api.callmebot.com/start.php?user=@{username}&text={encoded_message}&lang=en-US-Standard-C&rpt=2"
    
    print(f"Requesting URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200 and "Success" in response.text:
            print("✅ Call API reported success!")
        else:
            print("❌ Call API reported failure or unexpected response.")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_call()
