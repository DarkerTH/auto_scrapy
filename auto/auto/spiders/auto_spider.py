#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

class AutoSpider(scrapy.Spider):
    name = "auto"
    allowed_domains = ["autoplius.lt"];

    def start_requests(self, domain=None, *args, **kwargs):
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