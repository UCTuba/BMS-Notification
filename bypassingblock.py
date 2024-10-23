import time
import random
import sqlite3
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests


MOVIE_URL = "" #Paste URL of movie booking page 

# Pushover API credentials
PUSHOVER_USER_KEY = ''
PUSHOVER_APP_TOKEN = ''

Ua = UserAgent()
driver = webdriver.Safari()


def create_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS showtimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theater TEXT NOT NULL,
            showtime TEXT NOT NULL,
            UNIQUE(theater, showtime)  -- Add unique constraint
        )
    ''')
    
    conn.commit()
    return conn


def store_showtimes(conn, theater_showtimes):
    cursor = conn.cursor()
    for theater, showtimes in theater_showtimes.items():
        for showtime in showtimes:
                cursor.execute('''
                INSERT OR IGNORE INTO showtimes (theater, showtime) 
                VALUES (?, ?)
            ''', (theater, showtime))  
    conn.commit()


def get_existing_showtimes(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT theater, showtime FROM showtimes')

    existing_showtimes = {}
    for theater, showtime in cursor.fetchall():
        if theater not in existing_showtimes:
            existing_showtimes[theater] = []
        existing_showtimes[theater].append(showtime)
    return existing_showtimes


def send_notification(message):
    """Send a notification via Pushover."""
    MAX_MESSAGE_LENGTH = 1024  

    if len(message) > MAX_MESSAGE_LENGTH:
        parts = [message[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
        for part in parts:
            data = {
                'token': PUSHOVER_APP_TOKEN,
                'user': PUSHOVER_USER_KEY,
                'message': part
            }
            response = requests.post('https://api.pushover.net/1/messages.json', data=data)
            if response.status_code == 200:
                print("Notification part sent successfully!")
            else:
                print("Failed to send notification part.")
    else:
        data = {
            'token': PUSHOVER_APP_TOKEN,
            'user': PUSHOVER_USER_KEY,
            'message': message
        }
        response = requests.post('https://api.pushover.net/1/messages.json', data=data)
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print("Failed to send notification.")

def scroll_page(driver):
    """Scrolls the page to the bottom to load all dynamic content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(5)

        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  
        last_height = new_height

def get_current_showtimes():
    """Scrape current theater and showtime listings from BookMyShow."""
    try:
        driver.get(MOVIE_URL)
        time.sleep(random.uniform(5, 15)) 
        

        if "blocked" in driver.page_source.lower():  
            return "blocked"
        

        try:
            not_now_button = driver.find_element(By.ID, 'wzrk-cancel')
            not_now_button.click()
        except:
            pass

        scroll_page(driver)


        theater_elements = driver.find_elements(By.CSS_SELECTOR, 'a.__venue-name')
        theaters = [theater.text.strip() for theater in theater_elements if theater.text.strip()]


        showtime_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.showtime-pill-wrapper')  
        
        theater_showtimes = {}
        
        for idx, theater in enumerate(theaters):
            print(f"Scraping theater {theater} ({idx + 1}/{len(theaters)})")  
            showtimes = set()
            try:
                showtime_elements = showtime_blocks[idx].find_elements(By.CSS_SELECTOR, 'div.__text')
                for showtime in showtime_elements:
                    time_text = showtime.text.strip()
                    if any(am_pm in time_text for am_pm in ["AM", "PM"]):
                        showtimes.add(time_text)
            except IndexError:
                pass  
            
            if not showtimes:
                showtimes.add("No showtimes available")
            
            theater_showtimes[theater] = sorted(showtimes)

        return theater_showtimes
    except Exception as e:
        print(f"Error occurred: {e}")
        return "error"

def main():
    conn = create_database()  
    previous_data = get_existing_showtimes(conn)  

    while True:
        current_showtimes = get_current_showtimes()
        
        if current_showtimes == "error":
            send_notification("An error occurred while scraping the site.")
            break  # Terminate script
        else:
            # Prepare to collect new showtimes
            new_showtimes = {}
            for theater, showtimes in current_showtimes.items():
                previous_showtimes = set(previous_data.get(theater, []))  # Get previous showtimes for the theater
                # Identify truly new showtimes
                added_showtimes = set(showtimes) - previous_showtimes
                if added_showtimes:
                    new_showtimes[theater] = sorted(added_showtimes)

            
            if new_showtimes:
                
                message = "New showtimes added:\n"
                for theater, showtimes in new_showtimes.items():
                    message += f"{theater}: {', '.join(showtimes)}\n"
                send_notification(message)

                
                store_showtimes(conn, current_showtimes)

                for theater, showtimes in current_showtimes.items():
                    if theater not in previous_data:
                        previous_data[theater] = showtimes
                    else:
                        previous_data[theater].extend(showtimes)

               
                for theater in previous_data:
                    previous_data[theater] = sorted(set(previous_data[theater]))


            else:
                print("No new updates.")  
                send_notification("No new updates.")  
            break
 

    conn.close()  # Close the database connection

if __name__ == "__main__":
    main()

