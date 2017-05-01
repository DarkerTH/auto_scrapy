# Car-classified crawler

##HTTPS support:
* `sudo apt-get install libssl-dev`
* `pip install pyopenssl --upgrade`

##How to run
* `cd auto/auto/spiders`
* `scrapy runspider auto_spider.py -a manufacturer=ford -a model=mondeo -o auto.json`

`auto.json` should now contain crawled data.
