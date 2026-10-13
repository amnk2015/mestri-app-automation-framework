import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    
    async with async_playwright() as p:
        # Cloud සර්වර් එකට Desktop Screen එකක් ලබා දීම
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            permissions=["clipboard-read", "clipboard-write"]
        )
        page = await context.new_page()
        
        print("1. Opening Mestri App live URL...")
        # ⚠️ මෙතැන නිවැරදි Mestri App URL එක ඇතුළත් කර ඇත
        await page.goto("https://lovable.app")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="step1_landing_page.png")
        
        print("2. Entering credentials...")
        try:
            await page.wait_for_selector("input[type='email']", timeout=5000)
            await page.fill("input[type='email']", "amnk.info@gmail.com") 
            await page.fill("input[type='password']", "admin123") 
            await page.screenshot(path="step2_before_login.png")
            await page.click("button:has-text('Sign in'), input[type='submit']")
        except Exception as e:
            print(f"ℹ️ Login fields not found directly, maybe already logged in or custom UI: {e}")
        
        # ලොගින් වූ පසු ඩෑෂ්බෝඩ් එක ලෝඩ් වන තෙක් රැඳී සිටීම
        await page.wait_for_timeout(4000)
        await page.screenshot(path="step3_dashboard.png")
        
        print("3. Navigating to Settings section...")
try:
    await page.wait_for_selector("text=Settings", timeout=10000)
    await page.click("text=Settings")
except Exception as e:
    print(f"⚠️ Text=Settings failed, trying fallback CSS selector: {e}")
    await page.click("a[href*='settings']")
        
        print("4. Waiting for Settings page content...")
        await page.wait_for_timeout(4000)
        await page.screenshot(path="step4_settings_page.png")
        
        invite_btn = "button:has-text('Copy Invite Link'), button:has-text('Invite'), [class*='invite']"
        
        try:
            print("5. Triggering the Project Invite Link...")
            await page.wait_for_selector(invite_btn, timeout=10000)
            await page.click(invite_btn)
            print("✅ Click action executed on Copy Link button.")
        except Exception as e:
            print(f"⚠️ Direct button not found, trying general text fallback... Error: {e}")
            await page.click("text=Copy Invite Link")
        
        await page.wait_for_timeout(1000)
        await page.screenshot(path="step5_final_state.png")
        
        # Clipboard එක කියවීම
        copied_link = await page.evaluate("navigator.clipboard.readText()")
        print(f"\nCaptured Clipboard Value: {copied_link}\n")
        
        test_success = False
        if copied_link and "mestri-app.lovable.app" in copied_link:
            print("🔬 ASSERTION SUCCESS: Link structure is valid!")
            test_success = True
        else:
            print("❌ ASSERTION FAILURE: Unexpected or empty link template copied.")
            
        await browser.close()
        
        # n8n වෙත ප්‍රතිඵල යැවීම
        if n8n_webhook_url:
            import requests
            payload = {
                "status": "SUCCESS" if test_success else "FAILED",
                "message": "Mestri App Live E2E Verification Passed." if test_success else "Automated test encountered a broken element.",
                "copied_link": copied_link if copied_link else "None"
            }
            try:
                requests.post(n8n_webhook_url, json=payload)
                print("➡️ Test results securely sent back to n8n Cloud!")
            except Exception as e:
                print(f"⚠️ Failed to send results to n8n: {e}")
        else:
            print("ℹ️ N8N_WEBHOOK_URL not configured.")

        if not test_success:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
