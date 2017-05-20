#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/home/darker/.local/lib/python2.7/site-packages');

import random
from random import randint

import scrapy
from scrapy.crawler import CrawlerProcess

import json

items = []

class AutoSpider(scrapy.Spider):
    name = "auto"
    allowed_domains = ["autoplius.lt", "autogidas.lt"];

    def start_requests(self, domain=None, *args, **kwargs):
        websites = [
            {
              'title': 'autogidas',
              'ad-div': '.item-link',
              'url': 'https://autogidas.lt/automobiliai/?f_1%5B1%5D={0}&f_model_14%5B1%5D={1}&f_41={2}&f_42={3}&f_215={4}&f_216={5}&f_60=6315&f_50=atnaujinimo_laika_asc'.format(self.manufacturer_model['autogidas']['manufacturer'], self.manufacturer_model['autogidas']['model'], self.year_from, self.year_to, self.price_from, self.price_to),
            },
            {
              'title': 'autoplius',
              'ad-div': 'div.item',
              'url': 'https://autoplius.lt/skelbimai/naudoti-automobiliai/?make_id={0}&model_id={1}&engine_capacity_from=&engine_capacity_to=&power_from=&power_to=&kilometrage_from=&kilometrage_to=&has_damaged_id=&color_id=&condition_type_id=&make_date_from={2}&make_date_to={3}&sell_price_from={4}&sell_price_to={5}&fuel_id=&gearbox_id=&body_type_id=&wheel_drive_id=&number_of_seats_id=&number_of_doors_id=&fk_place_countries_id=&steering_wheel_id=&origin_country_id=&older_not=-1&qt=&order_by=3&order_direction=DESC'.format(self.manufacturer_model['autoplius']['manufacturer'], self.manufacturer_model['autoplius']['model'], self.year_from, self.year_to, self.price_from, self.price_to),
            }
        ]

        super(AutoSpider, self).__init__(*args, **kwargs)
        for website in websites:
            yield scrapy.Request(url=website['url'], callback=self.parse, meta={'website': website, 'ad-div': website['ad-div']})

    def parse(self, response):
        website = response.meta.get('website')
        for item in response.css(response.meta.get('ad-div')):
            parsed = AutoSpider.get_rules(self, website['title'], item)
            items.append(parsed)
            yield parsed

        if website['title'] == 'autoplius':
            next = response.css('.next ::attr(href)').extract_first()

        if website['title'] == 'autogidas':
            next = response.css('.next-page-block a::attr(href)').extract_first()

        if next:
            if website['title'] == 'autoplius':
                next = ''.join(['https://autoplius.lt', next])

            if website['title'] == 'autogidas':
                next = ''.join(['https://autogidas.lt', next])

            yield scrapy.Request(url=next, callback=self.parse, meta={'website': website, 'ad-div': website['ad-div']})

    def get_rules(self, website, item):
        rules = {};

        if website == 'autogidas':
            letter_e = 'ė'.decode('utf-8');
            rules = {
                    'id': int(item.css('.item-link .ad ::attr(data-ad-id)').extract_first()),
                    'url': ''.join(['https://autogidas.lt', item.css('::attr(href)').extract_first()]),
                    'img_url': item.css('.ad .right .image img::attr(src)').extract_first(),
                    'title': item.css('.ad .right .description .item-title::text').extract_first(),
                    'year': item.css('.ad .right .description .item-description .primary::text').re('\d{4}\-\d{2}')[0],
                    'gearbox': ''.join([item.css('.ad .right .description .item-description .primary::text').re('Automatin|Mechanin')[0], letter_e]),
                    'mileage': ''.join(item.css('.ad .right .description .item-description .primary::text').re('\, (\d{1,3} \d{1,3}) km')).replace(" ", ""),
                    'fuel': item.css('.ad .right .description .item-description .secondary::text').extract_first().strip().split(',')[0],
                    #'engine_capacity': item.css('.ad .right .description .item-description .secondary::text').re('(\d{1}\.\d{1}) l')[0],
                    'power': ''.join(item.css('.ad .right .description .item-description .secondary::text').re('(\d{2,5}) kW')),
                    'city': item.css('.ad .left .city::text').extract_first().encode('utf-8'),
                    'inserted_before': item.css('.ad .left .inserted-before::text').re('(\d{1,2} (?:val|min|d))\.'),
                    'price': ''.join(item.css('.ad .right .description .item-price::text').re(r'\d+')),


                }

        if website == 'autoplius':
            rules = {
                    'id': int(item.css('.item-section .title-list a::attr(href)').re(r'(?:.*)-([0-9]{1,10})')[0]),
                    'url': item.css('.item-section .title-list a::attr(href)').extract_first(),
                    'img_url': item.css('.thumb a img::attr(src)').extract_first(),
                    'title': item.css('.item-section .title-list a::text').extract_first(),
                    'year': item.css('.item-section .param-list div span[title="Pagaminimo data"]::text').extract_first(),
                    'fuel': item.css('.item-section .param-list div span[title="Kuro tipas"]::text').extract_first(),
                    'gearbox': item.css('.item-section .param-list div span[title*="Pavar"]::text').extract()[0],
                    'power': ''.join(item.css('.item-section .param-list div span[title="Galia"]::text').re(r'\d+')),
                    'mileage': ''.join(item.css('.item-section .param-list div span[title="Rida"]::text').re(r'\d+')),
                    'city': item.css('.item-section .param-list div span[title="Miestas"]::text').extract_first().encode('utf-8'),
                    'inserted_before': item.css('.item-menu .tools-right::text').re('(\d{1,2} (?:val|min|d))\.'),
                    'price': ''.join(item.css('.fr .price-list .fl strong::text').re(r'\d+')),
                }

        rules['website'] = website
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
    'ROTATING_PROXY_LIST': load_lines('/var/www/html/auto_scrapy/auto/spiders/proxies.txt'),
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    }
})

process.crawl(AutoSpider, manufacturer_model=json.loads(sys.argv[1]), year_from=sys.argv[2], year_to=sys.argv[3], price_from=sys.argv[4], price_to=sys.argv[5])
process.start() # the script will block here until the crawling is finished
