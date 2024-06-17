import scrapy, httpx, re, time
from auto24.helpers.helper import (
    create_session,
    delete_session
)
from scrapy.utils.project import get_project_settings
from datetime import date   # For getting current date

class LyhikeNimekiriSpider(scrapy.Spider):
    name = "lyhike_nimekiri"
    allowed_domains = ["www.auto24.ee"]
    # start_urls = ["https://www.auto24.ee/robots.txt"]
    counter = 0
    reset = 12
    pause = 15
    mydate = ""

    # This defines the scraped files
    custom_settings = {
        'FEEDS': {"./scraped_files/%(name)s/%(name)s_%(time)s.csv" : {"format": "csv"}},
    }

    def start_requests(self):
        settings=get_project_settings()
        self.session_id = settings.get('MY_SESSION_ID')
        self.mydate = date.today().strftime("%Y-%m-%d")
#        print("########################")
#        print(self.session_id)
#        print("########################")
#        start_url = "https://www.auto24.ee/kasutatud/nimekiri.php?ak=26000"
        start_url = "https://www.auto24.ee/kasutatud/nimekiri.php?af=100"
        create_session(url=start_url, session_id = self.session_id)
        yield scrapy.Request(
            url=start_url, 
            meta={"use_session": True}
        )

    def closed(self, reason):
        pass
        # Called when the spider closes. 
        delete_session(self.session_id)

    def parse(self, response):
        urls = response.css('.row-link::attr(href)').getall()
        for url in urls:
            yield {
#                "id": int(a.css('.row-link::attr(href)').re("\d+")[0]),
                "url": url,
                "date": self.mydate
            }
        # Järgmise lehe nupp:
        # response.css('button.btn-right::attr(onclick)').re("href='(.*)'")[0]
        next_page = response.css('button.btn-right::attr(onclick)').re("href='(.*)'")
        if len(next_page) != 0:
            next_page = "https://www.auto24.ee" + next_page[0]
        else:
            next_page = None
        if next_page is not None:
            # Take a break after every self.reset queries
            if self.counter >= self.reset:
                # reset counter
                self.counter = 0

                # Pause for a while
                self.logger.info(f"Pausing scrape job for {self.pause} seconds...")
                # Delete current session
                delete_session(self.session_id)

                self.crawler.engine.pause()
                time.sleep(self.pause)
                self.crawler.engine.unpause()
                self.logger.info(f"Resuming crawl...")

                # Recreate session
                create_session(url=next_page, session_id = self.session_id)


            self.counter += 1
            yield scrapy.Request(url=next_page, dont_filter = True)
            #yield response.follow(next_page, self.parse)
