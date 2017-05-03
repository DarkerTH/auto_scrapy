#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/home/darker/.local/lib/python2.7/site-packages');

import random
from random import randint

import scrapy
from scrapy.crawler import CrawlerProcess

import json

file_name = sys.argv[1]
items = []

class AutoSpider(scrapy.Spider):
    name = "auto"
    allowed_domains = ["autoplius.lt", "autogidas.lt"];

    def start_requests(self, domain=None, *args, **kwargs):
        sys.path
        super(AutoSpider, self).__init__(*args, **kwargs)
        #define auto-classified websites here
        websites = [
            {
              'title': 'autogidas',
              'ad-div': '.item-link',
              'url': 'https://autogidas.lt/automobiliai/?f_1%5B1%5D={0}&f_model_14%5B1%5D={1}&f_41={2}&f_42={3}&f_215={4}&f_216={5}&f_60=6315&f_50=atnaujinimo_laika_asc'.format(self.manufacturer, self.model, self.year_from, self.year_to, self.price_from, self.price_to),
            },
            {
              'title': 'autoplius',
              'ad-div': 'div.item',
              'url': 'https://autoplius.lt/skelbimai/naudoti-automobiliai/{0}/{1}?engine_capacity_from=&engine_capacity_to=&power_from=&power_to=&kilometrage_from=&kilometrage_to=&has_damaged_id=&color_id=&condition_type_id=&make_date_from={2}&make_date_to={3}&sell_price_from={4}&sell_price_to={5}&fuel_id=&gearbox_id=&body_type_id=&wheel_drive_id=&number_of_seats_id=&number_of_doors_id=&fk_place_countries_id=&steering_wheel_id=&origin_country_id=&older_not=-1&qt=&order_by=3&order_direction=DESC'.format(self.manufacturer, self.model, self.year_from, self.year_to, self.price_from, self.price_to),
            }
        ]
        for website in websites:
            yield scrapy.Request(url=website['url'], callback=self.parse, meta={'website': website['title'], 'ad-div': website['ad-div']})

    def parse(self, response):
        for item in response.css(response.meta.get('ad-div')):
            parsed = AutoSpider.get_rules(self, response.meta.get('website'), item)
            items.append(parsed)
            yield parsed

    def get_rules(self, website, item):
        rules = {};

        if website == 'autogidas':
            letter_e = 'ė'.decode('utf-8');
            rules = {
                    'url': ''.join(['https://autogidas.lt', item.css('::attr(href)').extract_first()]),
                    'title': item.css('.ad .right .description .item-title::text').extract_first(),
                    'year': item.css('.ad .right .description .item-description .primary::text').re('\d{4}\-\d{2}')[0],
                    'gearbox': ''.join([item.css('.ad .right .description .item-description .primary::text').re('Automatin|Mechanin')[0], letter_e]),
                    'run': ''.join(item.css('.ad .right .description .item-description .primary::text').re('\, (\d{1,3} \d{1,3}) km')).replace(" ", ""),
                    'gastype': item.css('.ad .right .description .item-description .secondary::text').extract_first().strip().split(',')[0],
                    #'engine_capacity': item.css('.ad .right .description .item-description .secondary::text').re('(\d{1}\.\d{1}) l')[0],
                    'power': ''.join(item.css('.ad .right .description .item-description .secondary::text').re('(\d{2,5}) kW')),
                    'city': item.css('.ad .left .city::text').extract_first(),
                    'inserted_before': item.css('.ad .left .inserted-before::text').re('(\d{1,2} (?:val|min|d))\.'),
                    'price': ''.join(item.css('.ad .right .description .item-price::text').re(r'\d+')),


                }

        if website == 'autoplius':
            rules = {
                    'url': item.css('.item-section .title-list a::attr(href)').extract_first(),
                    'title': item.css('.item-section .title-list a::text').extract_first(),
                    'year': item.css('.item-section .param-list div span[title="Pagaminimo data"]::text').extract_first(),
                    'gas_type': item.css('.item-section .param-list div span[title="Kuro tipas"]::text').extract_first(),
                    'gearbox': item.css('.item-section .param-list div span[title*="Pavar"]::text').extract()[0],
                    'power': ''.join(item.css('.item-section .param-list div span[title="Galia"]::text').re(r'\d+')),
                    'run': ''.join(item.css('.item-section .param-list div span[title="Rida"]::text').re(r'\d+')),
                    'city': item.css('.item-section .param-list div span[title="Miestas"]::text').extract_first(),
                    'inserted_before': item.css('.item-menu .tools-right::text').re('(\d{1,2} (?:val|min|d))\.'),
                    'price': ''.join(item.css('.fr .price-list .fl strong::text').re(r'\d+')),
                }

        rules['website'] = website
        return rules

    def closed(self, reason):
        if reason == "finished":
            print(json.dumps(items))

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_EXPORT_ENCODING': 'utf-8',
    'FEED_URI': 'result.json'.format(file_name)
})

process.crawl(AutoSpider, manufacturer=sys.argv[2], model=sys.argv[3], year_from=sys.argv[4], year_to=sys.argv[5], price_from=sys.argv[6], price_to=sys.argv[7])
process.start() # the script will block here until the crawling is finished
