import asyncio
from fastapi import FastAPI, BackgroundTasks
import uvicorn
from playwright.async_api import async_playwright
import pyperclip

app = FastAPI()

async def run_mestri_test():
    print("🚀 Starting Automated Test inside Local Machine...")
    async with async_playwright() as p:
        # headless=False දමා ඇති නිසා ඔන්ලයින් n8n එකෙන් බිලtrigger කලාම ඔබේ පරිගණකයේ බ්‍රවුසර් එක ඇරෙනවා බලාගත හැක
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        print("1. Navigating to Mestri App...")
        await page.goto("https://mestri-app.lovable.app")
        
        print("2. Entering credentials...")
        await page.wait_for_selector("input[type='email']")
        await page.fill("input[type='email']", "amnk.info@gmail.com") 
        await page.fill("input[type='password']", "admin123") 
        await page.click("button:has-text('Sign in'), input[type='submit']")
        
        print("3. Navigating to Settings...")
        await page.click("text=Settings")
        await page.wait_for_timeout(2000)
        
        print("4. Clicking Copy Invite Link...")
        invite_btn = "text=Copy Invite Link"
        await page.wait_for_selector(invite_btn, timeout=5000)
        await page.click(invite_btn)
        
        await page.wait_for_timeout(1000)
        copied_link = pyperclip.paste()
        
        print(f"Captured Link: {copied_link}")
        
        if "mestri-app.lovable.app" in copied_link:
            print("🔬 ASSERTION SUCCESS: Test Passed!")
        else:
            print("❌ ASSERTION FAILURE: Test Failed!")
            
        await page.screenshot(path="settings_verification.png")
        await browser.close()
        print("🏁 Test Finished Successfully!")

@app.post("/run-test")
def trigger_test(background_tasks: BackgroundTasks):
    # n8n එකෙන් මැසේජ් එක ආපු ගමන් ටෙස්ට් එක Background එකේ දුවන්න පටන් ගනී
    background_tasks.add_task(run_mestri_test)
    return {"status": "Test triggered on your local machine", "message": "Running Playwright..."}

if __name__ == "__main__":
    # ඔබේ පරිගණකයේ Port 8000 එක හරහා API එක සක්‍රීය වේ
    uvicorn.run(app, host="127.0.0.1", port=8000)