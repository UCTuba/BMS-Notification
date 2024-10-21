import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

# URL of the BookMyShow movie page for the city
MOVIE_URL = "https://in.bookmyshow.com/buytickets/venom-the-last-dance-3d-hyderabad/movie-hyd-ET00413299-MT/20241024"

# Pushover API credentials
PUSHOVER_USER_KEY = 'un4onxmxgi6swa2pmpe6kr4qhiar3t'
PUSHOVER_APP_TOKEN = 'ahs5cmqz5ec9tmru2h4ivqywfwfda3'

# Initialize Selenium WebDriver (SafariDriver)
driver = webdriver.Safari()

def send_notification(message):
    """Send a notification via Pushover."""
    url = 'https://api.pushover.net/1/messages.json'
    data = {
        'token': PUSHOVER_APP_TOKEN,
        'user': PUSHOVER_USER_KEY,
        'message': message
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification.")

def get_current_showtimes():
    """Scrape current theater and showtime listings from BookMyShow."""
    try:
        driver.get(MOVIE_URL)
        time.sleep(5)  # Wait for the page to load fully
        
        # Check if access is blocked (you may need to adjust this condition based on the page)
        if "blocked" in driver.page_source.lower():  # Look for a keyword indicating blocked access
            return "blocked"
        
        # Dismiss pop-ups (assuming 'Not Now' button has ID 'wzrk-cancel')
        try:
            not_now_button = driver.find_element(By.ID, 'wzrk-cancel')
            not_now_button.click()
        except:
            pass  # Ignore if the button is not found

        # Scrape theater names
        theater_elements = driver.find_elements(By.CSS_SELECTOR, 'a.__venue-name')
        theaters = [theater.text.strip() for theater in theater_elements if theater.text.strip()]

        # Scrape showtimes and group them by theaters
        showtime_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.showtime-pill-wrapper')  # Parent of showtimes for each theater
        
        theater_showtimes = {}
        
        for idx, theater in enumerate(theaters):
            showtimes = []
            try:
                showtime_elements = showtime_blocks[idx].find_elements(By.CSS_SELECTOR, 'div.__text')
                for showtime in showtime_elements:
                    time_text = showtime.text.strip()
                    if any(am_pm in time_text for am_pm in ["AM", "PM"]):
                        showtimes.append(time_text)
            except IndexError:
                pass  # If there's an indexing error, just skip the theater
            
            if not showtimes:
                showtimes.append("No showtimes available")
            
            theater_showtimes[theater] = showtimes

        return theater_showtimes
    except Exception as e:
        print(f"Error occurred: {e}")
        return "error"

def main():
    previous_data = {}  # Store previously fetched showtimes
    while True:
        current_showtimes = get_current_showtimes()

        if current_showtimes == "blocked":
            send_notification("Blocked from accessing BookMyShow. Please check manually.")
        elif current_showtimes == "error":
            send_notification("An error occurred while scraping the site.")
        elif current_showtimes != previous_data:
            if current_showtimes:
                message = "New showtimes added:\n"
                for theater, showtimes in current_showtimes.items():
                    message += f"{theater}: {', '.join(showtimes)}\n"
                send_notification(message)
            previous_data = current_showtimes
        else:
            send_notification("No new updates.")
        
        print("No new updates.")
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()

