import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# A simple mapping from keywords in reel to an "appropriate" emoji reaction.
# Adjust or expand this dictionary based on your preferences.
KEYWORD_EMOJI_MAP = {
    'funny': '😂', 
    'cat': '😻',
    'dog': '🐶',
    'wow': '😮',
    'dance': '🕺',
    'food': '🤤',
    # fallback for everything else:
    'default': '❤️',
}

def get_appropriate_emoji(reel_description):
    reel_description_lower = reel_description.lower()
    for keyword, emoji in KEYWORD_EMOJI_MAP.items():
        if keyword in reel_description_lower:
            return emoji
    return KEYWORD_EMOJI_MAP['default']

def main():
    # Initialize the WebDriver (Chrome in this example)
    driver = webdriver.Chrome()  # or specify the path: webdriver.Chrome(executable_path='path/to/chromedriver')
    
    # Go to Instagram login page
    driver.get("https://www.instagram.com/accounts/login/")
    wait = WebDriverWait(driver, 20)
    
    # Wait for the login fields to be present
    username_field = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
    password_field = driver.find_element(By.NAME, 'password')
    
    # Log in
    username_field.send_keys("YOUR_USERNAME")
    password_field.send_keys("YOUR_PASSWORD")
    password_field.send_keys(Keys.ENTER)
    
    # Optional: handle "Save Your Login Info?" pop-up or "Turn on Notifications?" pop-up
    # Dismiss them if they appear
    try:
        not_now_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now')]"))
        )
        not_now_button.click()
    except:
        pass
    
    time.sleep(5)
    
    # Navigate to direct messages (DMs)
    driver.get("https://www.instagram.com/direct/inbox/")
    time.sleep(5)
    
    # Wait for your list of chats to appear
    chat_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._ab8w")))
    
    # For simplicity, let's just open the first chat to demonstrate.
    # In a real script, you might iterate over multiple chats or filter by unread status.
    if chat_list:
        chat_list[0].click()
    
    time.sleep(5)
    
    # Now we parse the messages in the chat to find Reels.
    # Each message bubble can be identified by some container element.
    # This selector could change if Instagram updates its site.
    messages = driver.find_elements(By.CSS_SELECTOR, "div._aacl._aaco._aacw._aacx._aada")
    
    for message in messages:
        # Attempt to find a reel link
        try:
            reel_link_element = message.find_element(By.CSS_SELECTOR, "a")
            reel_url = reel_link_element.get_attribute("href")
            if "instagram.com/reel/" in reel_url:
                # We found a reel. We have no direct reel description here in the DM,
                # so let's just base the emoji on the link or a known set of keywords.
                # If you can scrape the reel's page or text snippet, pass that text to get_appropriate_emoji.
                # For now, we'll assume there's a keyword in the link or rely on default.
                
                # Example: if the reel link has 'funny' in it, react with laughing
                chosen_emoji = get_appropriate_emoji(reel_url)
                
                # Hover or click on the message to open reaction panel
                # In many cases, you can open the reaction popover by double-clicking or by
                # clicking a reaction button. The actual approach depends on the current DOM.
                message.click()
                time.sleep(2)
                
                # As a placeholder, we might look for an emoji button to click:
                # This is a hypothetical selector. You’d have to locate the actual reaction button.
                try:
                    reaction_button = message.find_element(By.XPATH, ".//button[contains(@aria-label, 'Emoji reaction')]")
                    reaction_button.click()
                    time.sleep(2)
                    
                    # Now send the chosen emoji
                    # Another hypothetical approach: There's often a text input in the reaction pop-up
                    reaction_input = driver.find_element(By.XPATH, "//input[@aria-label='Search emojis']")
                    reaction_input.send_keys(chosen_emoji)
                    time.sleep(1)
                    reaction_input.send_keys(Keys.ENTER)
                    time.sleep(2)
                except:
                    # If the reaction pop-up fails, fallback to sending a direct reply with emoji
                    text_box = driver.find_element(By.XPATH, "//textarea[@placeholder='Message...']")
                    text_box.send_keys(chosen_emoji)
                    text_box.send_keys(Keys.ENTER)
                    time.sleep(2)
                    
        except:
            pass
    
    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
