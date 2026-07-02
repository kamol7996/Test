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
                        '--disable-dev-shm-usage',
                    ]
                )
                
                context = await browser.new_context()
                page = await context.new_page()
                
                # User agent সেট করুন
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
                })
                
                print(f"→ Navigating to og.com/signup...")
                try:
                    await page.goto("https://og.com/signup", wait_until="domcontentloaded", timeout=30000)
                    print(f"  ✓ Page loaded")
                except Exception as e:
                    print(f"  ⚠️ Navigation: {e}")
                
                # reCAPTCHA script load হওয়ার জন্য অপেক্ষা করুন
                print(f"→ Waiting for reCAPTCHA script...")
                await page.wait_for_timeout(2000)
                
                # Token generate করুন
                print(f"→ Generating token...")
                token = await page.evaluate(f"""
                    async () => {{
                        // ইতিমধ্যে token থাকলে তা ফিরিয়ে দিন
                        if (window.__recaptchaToken) {{
                            return window.__recaptchaToken;
                        }}
                        
                        return new Promise((resolve, reject) => {{
                            let attempts = 0;
                            
                            const tryExecute = () => {{
                                attempts++;
                                console.log('Attempt ' + attempts, 'grecaptcha:', !!window.grecaptcha);
                                
                                if (!window.grecaptcha) {{
                                    if (attempts < 50) {{
                                        setTimeout(tryExecute, 100);
                                    }} else {{
                                        reject(new Error('grecaptcha not available'));
                                    }}
                                    return;
                                }}
                                
                                try {{
                                    if (window.grecaptcha.enterprise) {{
                                        window.grecaptcha.enterprise.ready(() => {{
                                            window.grecaptcha.enterprise.execute('{self.site_key}', {{action: 'submit'}})
                                                .then(token => {{
                                                    window.__recaptchaToken = token;
                                                    resolve(token);
                                                }})
                                                .catch(e => reject(e));
                                        }});
                                    }} else if (window.grecaptcha.ready) {{
                                        window.grecaptcha.ready(() => {{
                                            window.grecaptcha.execute('{self.site_key}', {{action: 'submit'}})
                                                .then(token => {{
                                                    window.__recaptchaToken = token;
                                                    resolve(token);
                                                }})
                                                .catch(e => reject(e));
                                        }});
                                    }} else {{
                                        reject(new Error('grecaptcha.ready not available'));
                                    }}
                                }} catch (e) {{
                                    reject(e);
                                }}
                            }};
                            
                            tryExecute();
                            
                            // Timeout: 20 seconds
                            setTimeout(() => {{
                                reject(new Error('Token generation timeout'));
                            }}, 20000);
                        }});
                    }}
                """)
                
                self.token = token
                self.token_timestamp = datetime.now()
                
                print(f"✅ Token generated!")
                print(f"   Length: {len(token)} chars")
                print(f"   First 40 chars: {token[:40]}...")
                
                await browser.close()
                return token
        
        except Exception as e:
            print(f"❌ Token generation failed: {e}")
            return None
    
    async def get_fresh_token(self):
        """নতুন token তৈরি করুন প্রতিবার"""
        print(f"\n[TOKEN REQUEST] Generating fresh reCAPTCHA token...")
        return await self.generate_token()

# Global instance
recaptcha_generator = RecaptchaTokenGenerator()
