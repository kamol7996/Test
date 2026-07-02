import requests
import json
import time
from typing import Dict, Optional
from datetime import datetime

class APIHandler:
    def __init__(self):
        self.base_url = "https://og.com/api/proxy/private/authnz/v1"
        self.session = requests.Session()
        self.session_token = None
        self.tmx_session_id = None
        self.anonymous_id = None
        self.ac_value = None
        self.cookies = {}
    
    def initialize_session(self):
        """প্রথমে signup page visit করে initial session তৈরি করুন"""
        print(f"\n{'='*80}")
        print(f"INITIALIZING SESSION")
        print(f"{'='*80}")
        
        try:
            # Step 1: Signup page visit করুন
            print(f"→ Visiting signup page...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
            
            response = self.session.get("https://og.com/signup", headers=headers, timeout=30)
            print(f"  Status: {response.status_code}")
            
            # Cookies save করুন
            self.cookies = self.session.cookies.get_dict()
            print(f"  Cookies received: {list(self.cookies.keys())}")
            
            # Response থেকে ac value খুঁজুন (যদি থাকে)
            if 'uc_flow' in response.text:
                print(f"  ✓ UC flow found in response")
            
            print(f"  ✓ Session initialized successfully")
            return True
        
        except Exception as e:
            print(f"✗ Session initialization failed: {e}")
            return False
    
    def get_session_token(self, ac_value):
        """✅ /user/auth endpoint থেকে session token পান"""
        print(f"\n{'='*80}")
        print(f"STEP 0: Getting Session Token via /user/auth")
        print(f"{'='*80}")
        
        url = f"{self.base_url}/user/auth"
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": "https://og.com",
            "Referer": "https://og.com/signup",
        }
        
        payload = {
            "ac": ac_value
        }
        
        print(f"→ POST {url}")
        print(f"  Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            print(f"  Status Code: {response.status_code}")
            
            response_data = response.json()
            print(f"  Response: {json.dumps(response_data, indent=2)}")
            
            # Response body থেকে session_token extract করুন
            if 'data' in response_data and 'session_token' in response_data['data']:
                self.session_token = response_data['data']['session_token']
                print(f"  ✓ Session Token obtained: {self.session_token[:30]}...")
            
            # Response headers থেকেও check করুন
            if 'session-token' in response.headers:
                self.session_token = response.headers['session-token']
                print(f"  ✓ Session Token from headers: {self.session_token[:30]}...")
            
            if 'tmx-session-id' in response.headers:
                self.tmx_session_id = response.headers['tmx-session-id']
                print(f"  ✓ TMX Session ID: {self.tmx_session_id}")
            
            return response.status_code == 200
        
        except Exception as e:
            print(f"✗ Failed to get session token: {e}")
            return False
    
    def _make_request(self, method, endpoint, payload=None, headers=None):
        """API request করুন"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": "https://og.com",
            "Referer": "https://og.com/signup",
        }
        
        if headers:
            default_headers.update(headers)
        
        # Headers set করুন request এ (lowercase)
        if self.session_token:
            default_headers["session-token"] = self.session_token
        if self.tmx_session_id:
            default_headers["tmx-session-id"] = self.tmx_session_id
        if self.anonymous_id:
            default_headers["x-anonymous-id"] = self.anonymous_id
        
        print(f"\n[API REQUEST]")
        print(f"  Method: {method}")
        print(f"  Endpoint: {endpoint}")
        print(f"  URL: {url}")
        print(f"  Headers: {default_headers}")
        if payload:
            payload_display = payload.copy()
            if 'recaptcha_response_token' in payload_display:
                token_preview = payload_display['recaptcha_response_token']
                payload_display['recaptcha_response_token'] = token_preview[:30] + "..." if len(token_preview) > 30 else token_preview
            print(f"  Payload: {json.dumps(payload_display, indent=2)}")
        
        try:
            if method == "POST":
                response = self.session.post(url, json=payload, headers=default_headers, timeout=30)
            elif method == "GET":
                response = self.session.get(url, headers=default_headers, timeout=30)
            
            print(f"\n[API RESPONSE]")
            print(f"  Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"  Response: {json.dumps(response_data, indent=2)}")
            except:
                response_data = {"error": response.text, "code": -1}
                print(f"  Response: {response.text[:200]}")
            
            # Response headers থেকে tokens extract করুন (lowercase)
            if 'session-token' in response.headers:
                self.session_token = response.headers['session-token']
                print(f"  ✓ Updated Session Token from response headers")
            
            if 'tmx-session-id' in response.headers:
                self.tmx_session_id = response.headers['tmx-session-id']
                print(f"  ✓ Updated TMX Session ID from response headers")
            
            if 'x-anonymous-id' in response.headers:
                self.anonymous_id = response.headers['x-anonymous-id']
                print(f"  ✓ Updated Anonymous ID from response headers")
            
            return response_data
        
        except Exception as e:
            print(f"[✗ ERROR] API Request failed: {e}")
            return {"error": str(e), "code": -1}
    
    def step1_send_email(self, email, recaptcha_token):
        """✅ Step 1 - Email পাঠান (reCAPTCHA token সহ)"""
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
            payload=payload
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
            payload=payload
        )
        
        return response
    
    def step3_set_phone(self, phone_number, country_code, recaptcha_token):
        """✅ Step 3 - Phone Number Submit করুন (reCAPTCHA token সহ)"""
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
            payload=payload
        )
        
        return response

api_handler = APIHandler()
