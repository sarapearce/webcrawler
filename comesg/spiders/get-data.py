from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from comesg.items import ComesgItem

class AttractionSpider(CrawlSpider):
    name = "get-data"
    allowed_domains = ["http://www.realclearpolitics.com"]
    start_urls = [
        "http://www.realclearpolitics.com/epolls/latest_polls/elections/"
    ]
    rules = ()

#    intact from orig author
    def __init__(self, name=None, **kwargs):
        super(AttractionSpider, self).__init__(name, **kwargs)
        self.items_buffer = {}
        self.base_url = "http://www.realclearpolitics.com"
        from scrapy.conf import settings
            settings.overrides['DOWNLOAD_TIMEOUT'] = 360

#    intact from orig author
    def parse(self, response):
        print "Start scrapping election data...."
        try:
            hxs = HtmlXPathSelector(response)
#            TODO: this linking might not be necessary. Delete if not used
            links = hxs.select("//*[@id='table-1']//a[@style='color:black']/@href")
            if not links:
                return
                log.msg("No Data to scrape")

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

#    unique to the website
    def parse_details(self, response):
        print "Collecting data points...."
        try:
            hxs = HtmlXPathSelector(response)
            poll_data = ComesgItem()
#            update this part to traverse down ML nodes specific to a given site

#            for RCP, this traverses to the innerHTML of the 1st tables cells
            v_name = hxs.select("/html/body/div[@id='container']/div[@id='alpha-container']/div[@id='alpha']/div[@id='table-1']/table/tbody/tr/td/a/text()").extract()
            if not v_name:
#                might get an array of tables returned, specify index to try again
                v_name = hxs.select("/html/body/div[@id='container']/div[@id='alpha-container']/div[@id='alpha']/div[@id='table-1']/table[0]/tbody/tr/td/a/text()").extract()
#            On RealClearPolitics, all tables have a header of the poll, grab that name
            title = hxs.select("/html/body/div[@id='container']/div[@id='alpha-container']/div[@id='alpha']/div[@id='page_title']/div/text()").extract()
    
#            TODO: this is now a test item. fix whitespace error after I figure out how to see whitespace in Brackets
#            not title:
#                title="no title found"
            poll_data["Title"] = title[0].strip()

#            assign base var so we do not have to write long strings for traversing to deep nodes
            base = hxs.select("//*[@id='table-1']")
            tables = base.select("table").extract()

            i_d = 0
            if tables:
                for table in tables:
                    print "processing table  " + i_d
                    tds = table.select("tbody/tr/td")
#                        fill in the poll_data object with cell data
                    print tds
                        if tds:
                            for td in tds:
                                td_class = td.extract()
                                if "date" in td_class:
                                    poll_data["Date"] = td.text()
                                if "lp-race" in td_class:
                                    poll_data["RaceOrTopic"] = td.text()
                                if "lp-poll" in td_class:
                                    poll_data["Poll"] = td.text()
                                if "lp-results" in td_class:
                                    poll_data["Results"] = td.text()
                                if "lp-spread" in td_class:
                                    poll_data["Spread"] = td.text()
                    i_d += 1

            yield poll_data
            print poll_data
        except Exception as e:
            log.msg("Parsing failed for URL {%s}"%format(response.request.url))
            raise

#            run this line in the root folder of this directory to run the script
#            scrapy crawl get-data -t csv -o rcp-data-1.csv