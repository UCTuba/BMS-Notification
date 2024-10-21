# BMS-Notification
Notifies if new showtimes and theatres were listed in a given time in Book My Show.  

Required Libraries:
```
Selenium (to scrape dynamic content)
Requests (for API calls)
Pushover or Twilio (for mobile notifications)
```
Set up a Pushover account:
```
Go to Pushover, sign up, and create a new application.
Get your user_key and app_token from the dashboard.
```
## OUTPUT Sample in Pushover app

### When a new theatre and show time were found from Previous Run 
```
"Mallikarjuna 70mm A/C DTS: Kukatpally": ["07:30 AM", "10:30 AM", "01:30 PM", "04:30 PM", "07:30 PM"],
  "Viswanath 70MM Theatre: Kukatpally": ["08:00 AM", "11:00 AM", "02:00 PM", "05:00 PM"],
  "Sree Ramulu 70mm 4k Laser: Moosapet": ["07:30 AM", "10:30 AM", "01:30 PM"],
```

### When no new listings were found
```
New showtimes added: {}
```
> [!Note]
> Error i'm facing 

```
error of block from site : Blocked from accessing BookMyShow. Please check manually.

after first automation will try to tackle by different methonds in future:

Usage of Proxies
Randomizing Request Intervals
Rotating User Agents
Using Headless Browsing with Browser Detection Bypass
Using a Residential IP or VPN
Lowering the Scraping Frequency

Check for Web API
```
