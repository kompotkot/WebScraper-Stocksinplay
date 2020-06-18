# -*- coding: utf-8 -*-
import scrapy

from collections import OrderedDict


class BriefingEarningsSpider(scrapy.Spider):
    name = 'briefing_earnings'
    allowed_domains = ['www.briefing.com']
    start_urls = ['https://www.briefing.com/Inv/content/Auth/Calendar/Earnings/week1.htm']  # Current week (week1)

    def parse(self, response):
        dates_lst = response.xpath('//*[@class="calDATE"]/text()').getall()    # Get list of days (dates)
        dates = {dates_lst[day]: day for day in range(len(dates_lst))}
        dates_sort = OrderedDict(sorted(dates.items(), key=lambda x: x[1]))     # Ordered dict to save que

        for i, day in enumerate(dates_sort):
            block = response.xpath('//*[@class="calDATE"]/following-sibling::ul')[i]    # Block for day
            events_lst = block.xpath('.//div[contains(@class,"calEVENT")]')             # Block for ticket

            tickets = OrderedDict()

            for event in events_lst:
                ticket = event.xpath('.//span/@data-ticker-search').get()
                name = event.xpath('.//strong/text()').get()
                surprise_value = event.xpath(
                    './/span[contains(text(), "Surprise:")]/following-sibling::span/text()').get()
                act_value = event.xpath('.//span[contains(text(), "Act:")]/following-sibling::span/text()').get()
                cons_value = event.xpath('.//span[contains(text(), "Cons:")]/following-sibling::span/text()').get()

                tickets.update({ticket: {'name': name,
                                         'surprise_value': surprise_value,
                                         'actual_value': act_value,
                                         'consensus_value': cons_value}})

            dates_sort.update({day: tickets})  # Add all tickets with values for day

        yield dates_sort
