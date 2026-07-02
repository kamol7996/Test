import requests
import json
import time
from typing import Dict, Optional
from datetime import datetime

class APIHandler:
    def __init__(self):
        self.base_url = "https://og.com/api/proxy/private/authnz/v1"
        self.session_token = None
        self.tmx_session_id = None
        self.anonymous_id = None
    
    def _make_request(self, method, endpoint, payload=None, headers=None):
        """API request করুন"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": "https://og.com",
        }
        
        if headers:
            default_headers.update(headers)
        
        if self.session_token:
            default_headers["Session-Token"] = self.session_token
        if self.tmx_session_id:
            default_headers["Tmx-Session-Id"] = self.tmx_session_id
        if self.anonymous_id:
            default_headers["X-Anonymous-Id"] = self.anonymous_id
        
        print(f"\n[API REQUEST]")
        print(f"  Method: {method}")
        print(f"  Endpoint: {endpoint}")
        print(f"  URL: {url}")
        if payload:
            payload_display = payload.copy()
            if 'recaptcha_response_token' in payload_display:
                payload_display['recaptcha_response_token'] = payload_display['recaptcha_response_token'][:30] + "..."
            print(f"  Payload: {json.dumps(payload_display, indent=2)}")
        
        try:
            if method == "POST":
                response = requests.post(url, json=payload, headers=default_headers, timeout=30)
            elif method == "GET":
                response = requests.get(url, headers=default_headers, timeout=30)
            
            print(f"\n[API RESPONSE]")
            print(f"  Status Code: {response.status_code}")
            response_data = response.json()
            print(f"  Response: {json.dumps(response_data, indent=2)}")
            
            return response_data
        
        except Exception as e:
            print(f"[✗ ERROR] API Request failed: {e}")
            return {"error": str(e), "code": -1}
    
    def step1_send_email(self, email, recaptcha_token):
        """Step 1: Email পাঠান"""
        print(f"\n{'='*80}")
        print(f"STEP 1: Send Email")
        print(f"{'='*80}")
        
        payload = {
            "email": email,
            "preferred_locale": "en",
            "recaptcha_response_token": recaptcha_token,
            "subscribe_newsletters": True,
            "utm": {}
        }
        
        response = self._make_request(
            "POST",
            "/authentication/email",
            payload=payload,
            headers={
                "Referer": "https://og.com/signup"
            }
        )
        
        return response
    
    def step2_verify_email_otp(self, otp_code):
        """Step 2: Email OTP Verify করুন"""
        print(f"\n{'='*80}")
        print(f"STEP 2: Verify Email OTP")
        print(f"{'='*80}")
        
        payload = {"otp": otp_code}
        
        response = self._make_request(
            "POST",
            "/authentication/email/verify-email-otp",
            payload=payload,
            headers={
                "Referer": "https://og.com/authentication/email-verify-otp"
            }
        )
        
        return response
    
    def step3_set_phone(self, phone_number, country_code, recaptcha_token):
        """Step 3: Phone Number Submit করুন"""
        print(f"\n{'='*80}")
        print(f"STEP 3: Set Phone Number")
        print(f"{'='*80}")
        
        # Country code এর সাথে phone format করুন
        full_phone = f"+{country_code}{phone_number}"
        
        payload = {
            "phone": full_phone,
            "recaptcha_response_token": recaptcha_token
        }
        
        response = self._make_request(
            "POST",
            "/registration/email/set-phone",
            payload=payload,
            headers={
                "Referer": "https://og.com/signup/phone-enter"
            }
        )
        
        return response

api_handler = APIHandler()
