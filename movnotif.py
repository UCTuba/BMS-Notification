import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

# Pushover credentials (get from your pushover account)
PUSHOVER_USER_KEY = 'un4onxmxgi6swa2pmpe6kr4qhiar3t'
PUSHOVER_APP_TOKEN = 'ahs5cmqz5ec9tmru2h4ivqywfwfda3'

# URL of the BookMyShow movie page for the city
MOVIE_URL = "https://in.bookmyshow.com/buytickets/mr-perfect-hyderabad/movie-hyd-ET00006900-MT/20241022"

# Initialize Selenium WebDriver (SafariDriver since you are using Safari)
driver = webdriver.Safari()

def send_pushover_notification(message):
    """Send mobile notification using Pushover."""
    payload = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification:", response.text)

def get_current_showtimes():
    """Scrape current theater and showtime listings from BookMyShow."""
    driver.get(MOVIE_URL)
    time.sleep(5)  # Wait for the page to load fully
    
    # Dismiss pop-ups (assuming 'Not Now' button has ID 'wzrk-cancel')
    try:
        not_now_button = driver.find_element(By.ID, 'wzrk-cancel')
        not_now_button.click()
    except:
        pass  # Ignore if the button is not found
    
    theater_elements = driver.find_elements(By.CSS_SELECTOR, 'a.__venue-name')
    theaters = [theater.text for theater in theater_elements]

    # Scrape showtimes
    showtime_elements = driver.find_elements(By.CSS_SELECTOR, 'div.__text')
    showtimes = [showtime.text.strip() for showtime in showtime_elements]
    
    theater_showtimes = {}
    
    for idx, theater in enumerate(theaters):
        showtimes = []
        try:
            showtime_elements = showtime_elements[idx].find_elements(By.CSS_SELECTOR, 'div.__text')
            for showtime in showtime_elements:
                time_text = showtime.text.strip()
                # A simple check to see if the text looks like a time (e.g., "07:30 AM")
                if any(am_pm in time_text for am_pm in ["AM", "PM"]):
                    showtimes.append(time_text)
        except IndexError:
            pass  # If there's an indexing error, just skip the theater
        
        theater_showtimes[theater] = showtimes

    return theater_showtimes

def main():
    """Main loop to check for new listings and send notifications."""
    last_known_showtimes = {}
    
    while True:
        current_showtimes = get_current_showtimes()
        
        if current_showtimes != last_known_showtimes:
            # Send notification of new showtimes
            message = f"New showtimes added: {json.dumps(current_showtimes, indent=2)}"
            send_pushover_notification(message)
            last_known_showtimes = current_showtimes
        else:
            print("No new updates.")

        # Wait for 15 minutes before checking again
        time.sleep(120)

if __name__ == "__main__":
    main()

