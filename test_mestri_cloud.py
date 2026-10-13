import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # සර්වර් එකේ Screen එක තවත් විශාල (1920x1080) Desktop එකක් ලෙස බලෙන් සකස් කිරීම
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
            print(f"ℹ️ Login fields not visible: {e}")
        
        await page.wait_for_timeout(5000)
        
        print("3. Checking for Mobile Menu / Sidebar...")
        # Screen size එක නිසා මෙනු එක හැංගිලා නම්, Hamburger Menu Icon එකක් ඇත්නම් එය ක්ලික් කිරීම
        menu_selectors = [
            "button[aria-label*='menu']", 
            "button[aria-label*='sidebar']",
            "button:has([class*='menu'])",
            "svg[class*='menu']",
            ".menu-button"
        ]
        for selector in menu_selectors:
            try:
                if await page.locator(selector).is_visible():
                    print(f"🎯 Mobile menu icon found: {selector}. Clicking it...")
                    await page.click(selector)
                    await page.wait_for_timeout(1000)
                    break
            except Exception:
                pass

        print("4. Navigating to Settings section...")
        try:
            # වඩාත්ම ආරක්ෂිත ක්‍රම කිහිපයකින් Settings සෙවීම
            settings_selectors = [
                "text=Settings",
                "a[href*='settings']",
                "button:has-text('Settings')",
                "[aria-label*='settings']"
            ]
            
            settings_clicked = False
            for selector in settings_selectors:
                try:
                    # element එක පෙනෙන්න නැතත් බලෙන්ම (force=True) ක්ලික් කිරීම
                    await page.click(selector, timeout=3000, force=True)
                    print(f"✅ Successfully clicked Settings using: {selector}")
                    settings_clicked = True
                    break
                except Exception:
                    pass
            
            if not settings_clicked:
                raise Exception("All settings selectors failed.")
                
        except Exception as e:
            print(f"❌ Failed to click Settings: {e}")
            buttons = await page.locator("button, a").all_inner_texts()
            print(f"📊 Current buttons/links: {buttons}")
            await browser.close()
            sys.exit(1)
        
        await page.wait_for_timeout(4000)
        
        print("5. Inspecting Settings Page Elements...")
        all_buttons = await page.locator("button").all_inner_texts()
        print(f"➔ [DEBUG] Found these buttons inside Settings: {all_buttons}")
        
        print("6. Triggering the Project Invite Link...")
        invite_success = False
        
        for btn_text in all_buttons:
            if "invite" in btn_text.lower() or "link" in btn_text.lower() or "copy" in btn_text.lower():
                print(f"🎯 Matching button found: '{btn_text}'. Attempting click...")
                await page.click(f"button:has-text('{btn_text}')", force=True)
                invite_success = True
                break
                
        if not invite_success:
            try:
                await page.click("text=Copy Invite Link", timeout=5000, force=True)
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
