# Cutted micro-version of the spider for a demo

This spider parse two sites in a row:
* The first spider takes data of the companies earnings and guidance for the current week
* The second spider filters on another site parsed tickers of the previous step 
* At the end, we get a "stocks in play" workbook for week
* The final data writes to the Google Sheet via API

![alt text](https://github.com/kompotkot/WebScraper-Stocksinplay/blob/master/demo.gif?raw=true)


Structure:
* app.py - The main file for working with spiders
* output - Temporary data in json format
* stocksinplay - Directory with spiders
* creds.json - Google Drive API credentials


## Build
```
docker build -t stocksinplay:latest .
```

## Launch
```
docker run stocksinplay app.py -s -g
```

Or run from the environment
```
python3 app.py -h
```

## Developed
2019
