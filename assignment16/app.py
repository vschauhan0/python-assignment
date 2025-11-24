# save as fb_post.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

# CONFIG
EMAIL = "vansh17chauhan@gmail.com"
PASSWORD = "#vansh@1786"
FB_URL = "https://www.facebook.com/"

# Setup driver (auto-download driver)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--disable-blink-features=AutomationControlled")  # optional

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get(FB_URL)

    # wait for email field (ID is stable)
    email_el = wait.until(EC.presence_of_element_located((By.ID, "email")))
    email_el.clear()
    email_el.send_keys(EMAIL)

    # password (ID 'pass' is usually stable)
    pass_el = wait.until(EC.presence_of_element_located((By.ID, "pass")))
    pass_el.clear()
    pass_el.send_keys(PASSWORD)

    # prefer locating login button by name="login"
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.NAME, "login")))
    except TimeoutException:
        # fallback: try to find a button with text "Log In" or "Log in"
        login_btn = None
        candidates = driver.find_elements(By.TAG_NAME, "button")
        for b in candidates:
            txt = (b.text or "").strip().lower()
            if txt in ("log in", "log in", "log in", "log in", "log in", "log in", "log in", "log in"):  # lenient
                login_btn = b
                break
    if not login_btn:
        raise NoSuchElementException("Could not locate a Facebook login button (name='login' / fallback failed).")
    login_btn.click()

    # wait for news feed / composer to appear
    # Facebook often uses a contenteditable div for status; try several locators
    sleep(3)  # short pause to let any redirects happen

    # Try several possible locators for the status box
    status_locator_candidates = [
        (By.NAME, "xhpc_message"),                      # old
        (By.XPATH, "//div[@role='textbox' and @contenteditable='true']"),  # common composer
        (By.XPATH, "//div[contains(@aria-label,'on your mind') and @role='textbox']"),  # english
        (By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']"),
    ]

    status_el = None
    for locator in status_locator_candidates:
        try:
            status_el = wait.until(EC.element_to_be_clickable(locator))
            if status_el:
                break
        except Exception:
            continue

    if not status_el:
        # maybe the composer is not visible yet or FB uses a different layout
        raise NoSuchElementException("Could not locate the status composer. Check if logged in or UI changed.")

    # Click into composer and write status
    status_el.click()
    status_el.send_keys("Hi there")

    sleep(2)  # let FB render the post button

    # Try to find "Post" button
    post_button = None
    # Common approach: find a button with text "Post"
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in buttons:
        try:
            if (b.text or "").strip().lower() == "post":
                post_button = b
                break
        except Exception:
            continue

    # If we found it, click; otherwise try pressing Ctrl+Enter as alternative
    if post_button:
        post_button.click()
    else:
        # fallback: send Ctrl+Enter to submit post
        from selenium.webdriver.common.keys import Keys
        status_el.send_keys(Keys.CONTROL, Keys.ENTER)

    print("Done — attempted to post status (check browser).")

except Exception as e:
    print("Error:", repr(e))
    # save screenshot for debugging
    driver.save_screenshot("fb_error_screenshot.png")
    print("Screenshot saved to fb_error_screenshot.png")

finally:
    # keep browser open for manual inspection for a little while
    sleep(5)
    # driver.quit()
