import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    # n8n එකෙන් එවන Webhook URL එක GitHub environment එකෙන් ලබා ගැනීම
    n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    
    async with async_playwright() as p:
        # සර්වර් එකක් ඇතුළේ දුවන නිසා headless=True අනිවාර්ය වේ
        browser = await p.chromium.launch(headless=True)
        
        # Clipboard එක කියවීමට අවශ්‍ය විශේෂ Cloud Permissions ලබා දීම
        context = await browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = await context.new_page()
        
        print("1. Opening Mestri App live URL...")
        await page.goto("https://mestri-app.lovable.app")
        
        print("2. Entering credentials...")
        await page.wait_for_selector("input[type='email']")
        await page.fill("input[type='email']", "amnk.info@gmail.com") 
        await page.fill("input[type='password']", "admin123") 
        await page.click("button:has-text('Sign in'), input[type='submit']")
        
        print("3. Navigating to Settings section...")
        await page.click("text=Settings")
        await page.wait_for_timeout(2000)
        
        print("4. Triggering the Project Invite Link...")
        invite_btn = "text=Copy Invite Link"
        await page.wait_for_selector(invite_btn, timeout=5000)
        await page.click(invite_btn)
        print("✅ Click action executed on Copy Link button.")
        
        await page.wait_for_timeout(1000)
        
        # Playwright හරහා බ්‍රවුසර් එක ඇතුළෙන්ම Clipboard එක කියවීම
        copied_link = await page.evaluate("navigator.clipboard.readText()")
        print(f"\nCaptured Clipboard Value: {copied_link}\n")
        
        test_success = False
        if "mestri-app.lovable.app" in copied_link:
            print("🔬 ASSERTION SUCCESS: Link structure is valid!")
            test_success = True
        else:
            print("❌ ASSERTION FAILURE: Unexpected link template copied.")
            
        await page.screenshot(path="settings_verification.png")
        await browser.close()
        
        # 5. ටෙස්ට් එක ඉවර වූ පසු n8n එකට ප්‍රතිඵලය Cloud එකෙන්ම POST කිරීම
        if n8n_webhook_url:
            import requests
            payload = {
                "status": "SUCCESS" if test_success else "FAILED",
                "message": "Mestri App Live E2E Verification Passed cleanly." if test_success else "Automated test encountered a broken element.",
                "copied_link": copied_link
            }
            try:
                requests.post(n8n_webhook_url, json=payload)
                print("➡️ Test results securely sent back to n8n Cloud!")
            except Exception as e:
                print(f"⚠️ Failed to send results to n8n: {e}")
        else:
            print("ℹ️ N8N_WEBHOOK_URL not configured. Skipping notification.")

        if not test_success:
            sys.exit(1) # ටෙස්ට් එක ෆේල් නම් GitHub Actions එකට එය දැනුම් දීම

if __name__ == "__main__":
    asyncio.run(main())
