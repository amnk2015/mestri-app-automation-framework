import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            permissions=["clipboard-read", "clipboard-write"]
        )
        page = await context.new_page()
        
        print("1. Opening Mestri App live URL...")
        await page.goto("https://mestri-app.lovable.app")
        await page.wait_for_timeout(3000)
        
        print("2. Entering credentials...")
        try:
            await page.wait_for_selector("input[type='email']", timeout=5000)
            await page.fill("input[type='email']", "amnk.info@gmail.com") 
            await page.fill("input[type='password']", "admin123") 
            await page.click("button:has-text('Sign in'), input[type='submit'], button[type='submit']")
            print("✅ Sign in button clicked.")
        except Exception as e:
            print(f"ℹ️ Login fields not visible, active session might exist: {e}")
        
        await page.wait_for_timeout(5000)
        
        print("3. Navigating to Settings section...")
        try:
            # වඩාත්ම පැහැදිලි Settings ලින්ක් එක සෙවීම
            await page.wait_for_selector("text=Settings", timeout=10000)
            await page.click("text=Settings")
            print("✅ Successfully clicked Settings.")
        except Exception as e:
            print(f"❌ Failed to click Settings text: {e}")
            # පිටුවේ දැනට පෙනෙන්නට තිබෙන සියලුම බටන් සහ ලින්ක්ස් ලොග් එකේ ප්‍රින්ට් කිරීම
            buttons = await page.locator("button, a").all_inner_texts()
            print(f"📊 Currently visible buttons/links on screen: {buttons}")
            await browser.close()
            sys.exit(1)
        
        await page.wait_for_timeout(4000)
        
        print("4. Inspecting Settings Page Elements...")
        # පිටුවේ දැනට පවතින සියලුම බොත්තම් වල නම් ටර්මිනල් එකේ ප්‍රින්ට් කිරීම (Advanced Debugging)
        all_buttons = await page.locator("button").all_inner_texts()
        print(f"➔ [DEBUG] Found these buttons inside Settings: {all_buttons}")
        
        print("5. Triggering the Project Invite Link...")
        invite_success = False
        
        # පිටුවේ තිබෙන බටන් එකින් එක පරීක්ෂා කර "Invite" හෝ "Link" අඩංගු එක ක්ලික් කිරීම
        for btn_text in all_buttons:
            if "invite" in btn_text.lower() or "link" in btn_text.lower() or "copy" in btn_text.lower():
                print(f"🎯 Matching button found: '{btn_text}'. Attempting click...")
                await page.click(f"button:has-text('{btn_text}')")
                invite_success = True
                break
                
        if not invite_success:
            print("⚠️ Standard button matching failed. Trying direct text click as fallback...")
            try:
                await page.click("text=Copy Invite Link", timeout=5000)
                invite_success = True
            except Exception:
                print("❌ Could not find any Invite Link button on this page.")
        
        await page.wait_for_timeout(2000)
        
        # Clipboard එක කියවීම
        copied_link = await page.evaluate("navigator.clipboard.readText()")
        print(f"\nCaptured Clipboard Value: {copied_link}\n")
        
        test_success = False
        if copied_link and "mestri-app.lovable.app" in copied_link:
            print("🔬 ASSERTION SUCCESS: Link structure is valid!")
            test_success = True
        else:
            print("❌ ASSERTION FAILURE: Unexpected link template copied.")
            
        await page.screenshot(path="settings_verification.png")
        await browser.close()
        
        # n8n වෙත ප්‍රතිඵල යැවීම
        if n8n_webhook_url:
            import requests
            payload = {
                "status": "SUCCESS" if test_success else "FAILED",
                "message": "Mestri App Live E2E Verification Finished." if test_success else "Automated test failed.",
                "copied_link": copied_link if copied_link else "None"
            }
            try:
                requests.post(n8n_webhook_url, json=payload)
            except Exception:
                pass

        if not test_success:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
