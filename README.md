# Car-ads crawler
Crawl data from various Lithuanian car-ads websites.  

## Requirements
* Python 2.7+

## How to run
* Navigate to the spider directory: `cd auto/spiders`
* Execute the spider with `python auto_spider.py {filename} {manufacturer} {model} {year_from} {year_to} {price_from} {price_to}`

Example: `python auto_spider.py response audi a4 2000 2006 0 3000` - this will crawl Audi A4 cars by 2000-2006 years and price 0-3000. Crawled result is saved on {filename}.json

## HTTPS support:
In case you need to crawl websites with SSL certificate
* `sudo apt-get install libssl-dev`
* `pip install pyopenssl --upgrade`

## To-Do:
* Proxy support
* In-depth ad crawling
* Random delays
