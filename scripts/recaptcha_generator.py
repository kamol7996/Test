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
            print(f"🔐 reCAPTCHA TOKEN GENERATION STARTED (USA IP)")
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
                        '--disable-dev-shm-usage',
                        '--disable-extensions',
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York'
                )
                page = await context.new_page()
                
                # USA location simulate করুন
                await context.set_geolocation({"latitude": 40.7128, "longitude": -74.0060})
                await context.grant_permissions(["geolocation"])
                
                print(f"→ Navigating to og.com/signup (USA IP)...")
                try:
                    await page.goto("https://og.com/signup", wait_until="domcontentloaded", timeout=30000)
                    print(f"  ✓ Page loaded successfully from USA")
                except Exception as e:
                    print(f"  ⚠️ Navigation: {e}")
                
                # reCAPTCHA script load হওয়ার জন্য অপেক্ষা করুন
                print(f"→ Waiting for reCAPTCHA script...")
                await page.wait_for_timeout(3000)
                
                # Token generate করুন
                print(f"→ Generating reCAPTCHA token...")
                token = await page.evaluate(f"""
                    async () => {{
                        return new Promise((resolve, reject) => {{
                            let attempts = 0;
                            const maxAttempts = 100;
                            
                            const tryExecute = () => {{
                                attempts++;
                                
                                if (!window.grecaptcha) {{
                                    if (attempts < maxAttempts) {{
                                        setTimeout(tryExecute, 100);
                                    }} else {{
                                        reject(new Error('grecaptcha not found after ' + (maxAttempts * 100) + 'ms'));
                                    }}
                                    return;
                                }}
                                
                                try {{
                                    // Try Enterprise first
                                    if (window.grecaptcha.enterprise && window.grecaptcha.enterprise.ready) {{
                                        window.grecaptcha.enterprise.ready(() => {{
                                            window.grecaptcha.enterprise.execute('{self.site_key}', {{action: 'submit'}})
                                                .then(token => {{
                                                    console.log('Enterprise token generated');
                                                    resolve(token);
                                                }})
                                                .catch(e => {{
                                                    console.error('Enterprise error:', e);
                                                    reject(e);
                                                }});
                                        }});
                                    }} 
                                    // Fallback to v3
                                    else if (window.grecaptcha.ready) {{
                                        window.grecaptcha.ready(() => {{
                                            window.grecaptcha.execute('{self.site_key}', {{action: 'submit'}})
                                                .then(token => {{
                                                    console.log('v3 token generated');
                                                    resolve(token);
                                                }})
                                                .catch(e => {{
                                                    console.error('v3 error:', e);
                                                    reject(e);
                                                }});
                                        }});
                                    }}
                                    else {{
                                        reject(new Error('No grecaptcha execution method available'));
                                    }}
                                }} catch (e) {{
                                    console.error('Execution error:', e);
                                    reject(e);
                                }}
                            }};
                            
                            tryExecute();
                            
                            // Timeout: 25 seconds
                            setTimeout(() => {{
                                reject(new Error('Token generation timeout after 25s'));
                            }}, 25000);
                        }});
                    }}
                """)
                
                self.token = token
                self.token_timestamp = datetime.now()
                
                print(f"✅ Token generated successfully (USA IP)!")
                print(f"   Length: {len(token)} characters")
                print(f"   First 50 chars: {token[:50]}...")
                print(f"   Generated at: {self.token_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                await browser.close()
                return token
        
        except Exception as e:
            print(f"❌ Token generation failed: {e}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
            return None
    
    async def get_fresh_token(self):
        """নতুন token তৈরি করুন প্রতিবার"""
        print(f"\n[TOKEN REQUEST] Generating fresh reCAPTCHA token from USA IP...")
        return await self.generate_token()

# Global instance
recaptcha_generator = RecaptchaTokenGenerator()
