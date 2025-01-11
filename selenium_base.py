import time
import os
import torch
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

# Hugging Face BLIP for image captioning
from transformers import BlipProcessor, BlipForConditionalGeneration

# =========================================
# (A) Setup Model for Image Captioning
# =========================================
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image_path):
    image = Image.open(image_path).convert('RGB')
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_length=50)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

# =========================================
# (B) Map Keywords to Emojis
# =========================================
KEYWORD_EMOJI_MAP = {
    "cat": "😸",
    "dog": "🐶",
    "dance": "🕺",
    "funny": "😂",
    "food": "🍔",
    "wow": "😮",
    # fallback
    "default": "❤️"
}

def pick_emoji_from_caption(caption):
    caption_lower = caption.lower()
    for keyword, emoji in KEYWORD_EMOJI_MAP.items():
        if keyword in caption_lower:
            return emoji
    return KEYWORD_EMOJI_MAP["default"]

# =========================================
# (C) Main Automation Code
# =========================================
def main():
    # Replace with your real credentials
    instagram_username = "YOUR_USERNAME"
    instagram_password = "YOUR_PASSWORD"

    # Optional: path to your chromedriver, if not in PATH
    # driver = webdriver.Chrome(executable_path='/path/to/chromedriver')
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)

    # 1) Go to Instagram login
    driver.get("https://www.instagram.com/accounts/login/")
    
    # 2) Login flow
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys(instagram_username)
    password_field.send_keys(instagram_password)
    password_field.send_keys(Keys.ENTER)

    # 3) Handle "Not Now" or notifications pop-ups if they appear
    try:
        not_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now')]")))
        not_now.click()
    except:
        pass

    time.sleep(5)

    # 4) Navigate to DMs
    driver.get("https://www.instagram.com/direct/inbox/")
    time.sleep(5)

    # 5) Open the first chat in the list (adjust logic as needed)
    chats = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._ab8w")))
    if chats:
        chats[0].click()
    else:
        print("No chats found. Exiting.")
        driver.quit()
        return
    
    time.sleep(5)

    # 6) Find all messages in the current chat
    messages = driver.find_elements(By.CSS_SELECTOR, "div._aacl._aaco._aacw._aacx._aada")

    for message in messages:
        # Try to find a link
        try:
            link_element = message.find_element(By.CSS_SELECTOR, "a")
            reel_url = link_element.get_attribute("href")
            if "instagram.com/reel/" in reel_url:
                # 7) Open Reel in a new tab
                driver.execute_script(f"window.open('{reel_url}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)

                # 8) Scroll or do any steps needed to ensure the reel is visible
                # Let's do a quick page scroll (arbitrary)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # 9) Take a screenshot of the visible part
                screenshot_path = "reel_screenshot.png"
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                driver.save_screenshot(screenshot_path)

                # 10) Generate a caption from the screenshot using BLIP
                caption = generate_caption(screenshot_path)
                print("Caption generated:", caption)

                # 11) Pick an emoji based on the caption
                chosen_emoji = pick_emoji_from_caption(caption)
                print("Chosen emoji:", chosen_emoji)

                # 12) Close the reel tab and switch back to DM
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                # 13) Send the emoji as a reply
                try:
                    text_box = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Message...']"))
                    )
                    text_box.send_keys(chosen_emoji)
                    text_box.send_keys(Keys.ENTER)
                    time.sleep(2)
                except Exception as e:
                    print("Failed to send emoji in chat:", e)

        except:
            # No link found or some other error, ignore
            pass

    driver.quit()

if __name__ == "__main__":
    main()
