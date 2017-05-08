#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/home/darker/.local/lib/python2.7/site-packages');

import random
from random import randint

import scrapy
from scrapy.crawler import CrawlerProcess

import json

websites = [
    {
      'title': 'autoplius',
      'brand-element': '#make_id option',
      'url': 'https://autoplius.lt/',
    }
]

items = {}

for website in websites:
    items[website['title']] = []

class BrandSpider(scrapy.Spider):
    global websites
    global items

    name = "auto"
    allowed_domains = ["autoplius.lt", "autogidas.lt"];


    def start_requests(self, domain=None, *args, **kwargs):
        sys.path
        super(BrandSpider, self).__init__(*args, **kwargs)
        #define auto-classified websites here
        for website in websites:
            yield scrapy.Request(url=website['url'], callback=self.parse, meta={'website': website['title'], 'brand-element': website['brand-element']})

    def parse(self, response):
        for item in response.css(response.meta.get('brand-element'))[2:]:
            parsed = BrandSpider.get_rules(self, response.meta.get('website'), item)
            items[response.meta.get('website')].append(parsed)
            yield parsed

    def get_rules(self, website, item):
        rules = {};

        if website == 'autogidas':
            rules = {
                }

        if website == 'autoplius':
            rules = {
                    'brand_id': item.css('::attr(value)').extract_first(),
                    'brand_name': item.css('::text').extract_first(),
                }

        return rules

    def closed(self, reason):
        if reason == "finished":
            print(json.dumps(items))

def load_lines(path):
    with open(path, 'rb') as f:
        return [line.strip() for line in
                f.read().decode('utf8').splitlines()
                if line.strip()]

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'ROTATING_PROXY_LIST': load_lines('proxies.txt'),
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    }
})


process.crawl(BrandSpider)
process.start() # the script will block here until the crawling is finished
