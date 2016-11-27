#!/usr/bin/python3
# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.linkextractors.sgml import SgmlLinkExtractor
#from scrapy import log
from comesg.items import ComesgItem
import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')
logger = logging.getLogger()
logger.debug('often makes a very good meal of %s', 'visiting tourists')

class RCPSpider(CrawlSpider):

    name = 'get-data'
    allowed_domains = ['http://www.realclearpolitics.com']
    start_urls = [
		"http://www.realclearpolitics.com/epolls/latest_polls/elections/"
	]
    rules = ()

    def __init__(self, name=None, **kwargs):
        super(RCPSpider, self).__init__(name, **kwargs)
        self.items_buffer = {}
        self.base_url = 'http://www.realclearpolitics.com/epolls/latest_polls/elections/'
        from scrapy.conf import settings
        settings.overrides['DOWNLOAD_TIMEOUT'] = 360

    def parse(self, response):
		print "Start scrapping Attractions...."
		try:
			hxs = HtmlXPathSelector(response)
			links = hxs.select("//*[@id='table-1']")
			
			if not links:
				return
				log.msg("No Data to scrap")

			for link in links:
				v_url = ''.join( link.extract() )
								
				if not v_url:
					continue
				else:
					_url = self.base_url + v_url
					yield Request( url= _url, callback=self.parse_details )
		except Exception as e:
			log.msg("Parsing failed for URL {%s}"%format(response.request.url))
			raise 

    def parse_details(self, response):
        logging.info('Collecting data points....')
        try:
            poll_data = ComesgItem()

#            On RealClearPolitics, all tables have a header of the poll, grab that name

            title = \
                scrapy.Selector("/html/body/div[@id='container']/div[@id='alpha-container']/div[@id='alpha']/div[@id='page_title']/div/text()"
                                ).extract()
            logging.info(title)

#            TODO: this is now a test item. fix whitespace error after I figure out how to see whitespace in Brackets
#            not title:
#                title="no title found"

            poll_data['Title'] = title[0].strip()

            base = scrapy.Selector("//*[@id='table-1']")
            tables = base.select('table').extract()

            i_d = 0
            if tables:
                for table in tables:
                    logging.info('processing table  ' + i_d)
                    tds = table.select('tbody/tr/td')

#                   fill in the poll_data object with cell data

                    if tds:
                        for td in tds:
                            td_class = td.extract()
                            print td_class
                            if 'date' in td_class:
                                poll_data['Date'] = td.text()
                            if 'lp-race' in td_class:
                                poll_data['RaceOrTopic'] = td.text()
                            if 'lp-poll' in td_class:
                                poll_data['Poll'] = td.text()
                            if 'lp-results' in td_class:
                                poll_data['Results'] = td.text()
                            if 'lp-spread' in td_class:
                                poll_data['Spread'] = td.text()
                i_d += 1
            yield poll_data
        except Exception, e:
            log.msg('Parsing failed for URL {%s}'
                    % format(response.request.url))

#            TODO: lookup what 'raise' does

            raise


#line to run the script
#       scrapy3 crawl get-data -t csv -o rcp-data-1.csv
