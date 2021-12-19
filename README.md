Remember to respect the `robots.txt` of whatever site you're scraping!
___
# isitasale
Quick script for me to check if sites are really having sales or if it's a sales tatic.

Dumps a screenshot of the url, and its rendered html page in the following folder structure:
```
rootfolder
 | -> date
    | -> scrsht
    | -> assets
```

## Setup
1. Install python3
2. `pip3 install webdriver-manager`
3. `pip3 install selenium`
4. Edit your configuration in `runJob`.

## Usage
4. `./runJob`

## Chron Jobs
https://www.cyberciti.biz/faq/how-do-i-add-jobs-to-cron-under-linux-or-unix-oses/
## Windows scheduler
https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10

## TODO
Crawling for nested assets.
Generate reports.