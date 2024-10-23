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
Intilize Data base :
```
Setup a database so code can verify it further.
```
## OUTPUT Sample in Pushover app

### When a new theatre and show time were found from Previous Run 
```
New showtimes added:
AMB Cinemas: Gachibowli: 08:30 PM
Indra Venkataramana Padmavati Cinema: Kachiguda: 06:25 PM, 09:15 PM
```

### When no new listings were found
```
No new updates.
```
> [!Note]
> Idea of bypassing the blocking from Book My Show Website 

```
error of block from site : Blocked from accessing BookMyShow. was been showed in prev code 
so I created a database and linked it to the code so when ever i restart the automation it checks if any new shows were added with the database.
By this I solved two of my problems
1: Block from the site
2: Freedom of choosing when should the code run.

I guess I cant fully automate the whole thing but will ponder ideas of improving this :)

```

