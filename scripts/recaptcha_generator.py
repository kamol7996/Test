import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime

class RecaptchaTokenGenerator:
    """Google reCAPTCHA Enterprise থেকে token generate করে"""
    
    def __init__(self):
        self.site_key = "6LeLx-csAAAAAI5IKPoVcsv5J5v2hl0dfELo_e1x"
        self.token = None
        self.token_timestamp = None
    
    async def generate_token(self):
        """reCAPTCHA Enterprise token generate করুন"""
        try:
            print(f"\n{'='*80}")
            print(f"🔐 reCAPTCHA TOKEN GENERATION STARTED")
            print(f"{'='*80}")
            print(f"→ Launching headless browser...")
            
            async with async_playwright() as p:
                # Headless Chrome লঞ্চ করুন
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-gpu',
                    ]
                )
                
                page = await browser.new_page()
                
                # User agent সেট করুন
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
                })
                
                print(f"→ Navigating to og.com/signup...")
                try:
                    await page.goto("https://og.com/signup", wait_until="networkidle", timeout=30000)
                    print(f"  ✓ Page loaded successfully")
                except Exception as e:
                    print(f"  ⚠️ Navigation warning: {e}")
                
                print(f"→ Waiting for reCAPTCHA to load...")
                await page.wait_for_timeout(3000)  # 3 সেকেন্ড অপেক্ষা
                
                # reCAPTCHA token এক্সট্র্যাক্ট করুন
                print(f"→ Extracting reCAPTCHA token...")
                token = await page.evaluate(f"""
                    async () => {{
                        return new Promise((resolve, reject) => {{
                            let attempts = 0;
                            const checkGrecaptcha = setInterval(() => {{
                                attempts++;
                                if (window.grecaptcha) {{
                                    clearInterval(checkGrecaptcha);
                                    
                                    if (window.grecaptcha.enterprise) {{
                                        // reCAPTCHA Enterprise v3
                                        grecaptcha.enterprise.ready(() => {{
                                            grecaptcha.enterprise.execute('{self.site_key}', {{action: 'submit'}})
                                                .then(token => {{
                                                    resolve(token);
                                                }})
                                                .catch(error => {{
                                                    reject(error);
                                                }});
                                        }});
                                    }} else {{
                                        // reCAPTCHA v2/v3 fallback
                                        grecaptcha.ready(() => {{
                                            grecaptcha.execute('{self.site_key}', {{action: 'submit'}})
                                                .then(token => {{
                                                    resolve(token);
                                                }})
                                                .catch(error => {{
                                                    reject(error);
                                                }});
                                        }});
                                    }}
                                }} else if (attempts > 150) {{
                                    clearInterval(checkGrecaptcha);
                                    reject(new Error('reCAPTCHA not found after 15 seconds'));
                                }}
                            }}, 100);
                            
                            setTimeout(() => {{
                                clearInterval(checkGrecaptcha);
                                reject(new Error('Token generation timeout'));
                            }}, 15000);
                        }});
                    }}
                """)
                
                self.token = token
                self.token_timestamp = datetime.now()
                
                print(f"✅ Token generated successfully!")
                print(f"   Length: {len(token)} characters")
                print(f"   First 50 chars: {token[:50]}...")
                print(f"   Generated at: {self.token_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                await browser.close()
                return token
        
        except Exception as e:
            print(f"❌ Token generation failed: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return None
    
    async def get_fresh_token(self):
        """নতুন token তৈরি করুন প্রতিবার"""
        print(f"\n[TOKEN REQUEST] Generating fresh reCAPTCHA token...")
        return await self.generate_token()

# Global instance
recaptcha_generator = RecaptchaTokenGenerator()
