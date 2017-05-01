#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/home/darker/.local/lib/python2.7/site-packages');

import random
from random import randint

import scrapy
from scrapy.crawler import CrawlerProcess

file_name = randint(1000000, 999999999);

class AutoSpider(scrapy.Spider):
    name = "auto"
    allowed_domains = ["autoplius.lt"];

    def start_requests(self, domain=None, *args, **kwargs):
        sys.path
        super(AutoSpider, self).__init__(*args, **kwargs)

        #define auto-classified websites here
        websites = [
            {
            'title': 'autoplius',
            'url': 'https://autoplius.lt/skelbimai/naudoti-automobiliai/{0}/{1}'.format(self.manufacturer, self.model),
            }
        ]
        for website in websites:
            yield scrapy.Request(url=website['url'], callback=self.parse, meta={'website': website['title']})

    def parse(self, response):
        for item in response.css('div.item'):
            yield AutoSpider.get_rules(self, response.meta.get('website'), item)

    def get_rules(self, website, item):
        rules = {};
        if website == 'autoplius':
            rules = {
                    'year': item.css('.item-section .param-list div span[title="Pagaminimo data"]::text').extract_first(),
                    'gas_type': item.css('.item-section .param-list div span[title="Kuro tipas"]::text').extract_first(),
                    'gearbox': item.css('.item-section .param-list div span[title*="Pavar"]::text').extract(),
                    'power': item.css('.item-section .param-list div span[title="Galia"]::text').extract_first(),
                    'run': item.css('.item-section .param-list div span[title="Rida"]::text').extract_first(),
                    'city': item.css('.item-section .param-list div span[title="Miestas"]::text').extract_first(),
                    'title': item.css('.item-section .title-list a::text').extract_first(),
                    'price': ''.join(item.css('.fr .price-list .fl strong::text').re(r'\d+')),
                }
        return rules

    def closed(self, reason):
        if reason == "finished":
            print(file_name)

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': '{0}.json'.format(file_name)
})

process.crawl(AutoSpider, manufacturer=sys.argv[1], model=sys.argv[2])
process.start() # the script will block here until the crawling is finished