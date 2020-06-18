import os
import glob
import time
import argparse
from collections import ChainMap

from stocksinplay.utils import correct_json, process_final, output_dir

from scrapy.utils import project
from scrapy import spiderloader

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging


# ARGUMENTS
defaults = {'start': False, 'list': False, 'google': False}

parser = argparse.ArgumentParser(description='Execute spiders in a row. Type: python app.py -s -g')
parser.add_argument('-s', '--start', action="store_true", help='Start crawl')
parser.add_argument('-g', '--google', action="store_true", help='Write to google sheet')
parser.add_argument('-l', '--list', action="store_true", help='List all spiders (This option for DEBUG only)')

args = parser.parse_args()
new_dict = {key: value for key, value in vars(args).items() if value}

sets = ChainMap(new_dict, defaults)


# OUR SPIDERS
class SpiderWork():
    def __init__(self):
        self.settings = project.get_project_settings()  # There we grab all settings from settings.py file
        configure_logging()
        self.runner = CrawlerRunner(self.settings)

    def get_spiders(self):
        spider_loader = spiderloader.SpiderLoader.from_settings(self.settings)
        return spider_loader.list()

    @defer.inlineCallbacks
    def start_crawl(self, chosen_feed='json'):

        self.settings.set('FEED_URI', f'{output_dir}/briefing_parsed.{chosen_feed}')
        self.settings.set('FEED_TYPE', chosen_feed)
        yield self.runner.crawl('briefing_earnings')

        self.settings.set('FEED_URI', f'{output_dir}/finviz_parsed.{chosen_feed}')
        self.settings.set('FEED_TYPE', chosen_feed)
        yield self.runner.crawl('finviz_screener')

        reactor.stop()


# MAIN INITIATOR
def main():
    start_time = time.time()

    spider_work = SpiderWork()

    if sets['list']:
        spiders = [spider for spider in spider_work.get_spiders()]
        print(spiders)

    if sets['start']:
        for file in glob.glob(f'{output_dir}/*_parsed.json'):
            os.remove(file)                             # Delete previous output files

        spider_work.start_crawl()
        reactor.run()

        correct_json()                                  # Correct our broken finviz_parsed.json
        process_final(googlewrite=sets['google'])       # Create final output file

    print(f'Required time: {(time.time() - start_time):.1f} sec')


if __name__ == '__main__':
    main()
