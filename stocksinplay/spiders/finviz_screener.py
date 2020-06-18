# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from ..items import FinvizItem
from ..utils import get_tickets_list


class FinvizScreenerSpider(scrapy.Spider):
    name = 'finviz_screener'
    allowed_domains = ['finviz.com']
    start_urls = ['https://finviz.com/']

    abs_pages_url = []

    def start_requests(self):
        # Average Vol = 500K, Rel Vol = 0.75, Cur Vol = 1M, Industry = Stocks only, Price = Over $10, Av True Range = Over 0.5
        # options_url = 'screener.ashx?v=111&f=ind_stocksonly,sh_avgvol_o500,sh_curvol_o1000,sh_price_o10,sh_relvol_o0.75,ta_averagetruerange_o0.5'
        options_url = 'screener.ashx?v=111&f=ind_stocksonly,sh_avgvol_o500,sh_price_o10,ta_averagetruerange_o0.5'

        tickers = get_tickets_list()
        tickers_url = '&t=' + ','.join(map(str, tickers))

        yield scrapy.Request(
            url=self.start_urls[0] + options_url + tickers_url,
            method='GET',
            callback=self.parse)

    def parse(self, response):
        url_lst = response.xpath('//a[@class="screener-link-primary"]/@href').getall()
        for url in url_lst:
            abs_url = self.start_urls[0] + url

            yield scrapy.Request(
                url=abs_url,
                method='GET',
                callback=self.ticker_parse)

        # Check if button next exists and page list is empty
        if response.xpath('//a/b[contains(text(), "next")]') and not self.abs_pages_url:
            pages_url = response.xpath('//a[@class="screener-pages"]/@href').getall()
            self.abs_pages_url = [response.urljoin(url) for url in pages_url]

            for url in self.abs_pages_url:
                yield scrapy.Request(
                    url=url,
                    method='GET',
                    callback=self.parse)

    def ticker_parse(self, response):
        loader = ItemLoader(item=FinvizItem(), response=response)
        loader.add_xpath('ticker', '//a[@id="ticker"]/text()')
        loader.add_xpath('name', '//table[@class="fullview-title"]//b/text()')
        loader.add_xpath('sector', '//a[contains(@href, "&f=sec_")]/text()')
        loader.add_xpath('price', '//td[text()="Price"]/following-sibling::td/b/text()')

        yield loader.load_item()       # app.py saves data in broken json format, it needs to be cleaned
