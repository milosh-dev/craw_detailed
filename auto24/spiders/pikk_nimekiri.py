import scrapy, httpx, re, time
from auto24.helpers.helper import (
    create_session,
    delete_session
)
from scrapy.utils.project import get_project_settings
from auto24.items import AutoItem
from datetime import date   # For getting current date

class PikkNimekiriSpider(scrapy.Spider):
    name = "pikk_nimekiri"
    allowed_domains = ["www.auto24.ee"]
    # start_urls = ["https://www.auto24.ee/soidukid/4005053"]
    counter = 0
    reset = 50
    pause = 3
    mydate = ""

    custom_settings = {
        'FEEDS': {"./scraped_files/%(name)s/%(name)s_%(time)s.csv" : {"format": "csv"}},
        "ITEM_PIPELINES" : {
            "auto24.pipelines.AutoPipeline": 300,
        }
    }

    def start_requests(self):
        settings=get_project_settings()
        self.session_id = settings.get('MY_SESSION_ID')
        self.mydate = date.today().strftime("%Y-%m-%d")
        #start_url = "https://www.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&ad=1&ae=8&af=50"
        start_url = "https://www.auto24.ee/kasutatud/nimekiri.php?ae=8&af=100"
        #create_session(url=start_url, session_id = self.session_id)
        yield scrapy.Request(url=start_url)

    def closed(self, reason):
        # Called when the spider closes. 
        delete_session(self.session_id)

    def parse(self, response):
        # Otsi üles terve nimekiri
        urls = response.css('.row-link::attr(href)').getall()
        # Nopi kõigi autode andmed
        for url in urls:
            auto = "https://www.auto24.ee" + url
            #yield from response.follow_all(auto, self.parse_auto)
            #self.crawler.engine.pause()
            #print(f"PAUS {self.pause} sekundit")
            #time.sleep(self.pause)
            #self.crawler.engine.unpause()
            yield scrapy.Request(
                url = auto, 
                meta={"dont_filter": True},
                callback=self.parse_auto, 
                cb_kwargs = {
                    'url': auto,
                })

        next_page = response.css('button.btn-right::attr(onclick)').re("href='(.*)'")
        # Pause for a while
        # self.logger.info(f"Pausing scrape job for {self.pause} seconds...")
        # Delete current session
        # delete_session(self.session_id)

        # self.crawler.engine.pause()
        # time.sleep(self.pause)
        # self.crawler.engine.unpause()
        # self.logger.info(f"Resuming crawl...")

        # Recreate session
        # create_session(url=next_page, session_id = self.session_id)

        if len(next_page) != 0:
            next_page = "https://www.auto24.ee" + next_page[0]
        else:
            next_page = None
        if next_page is not None:
            yield scrapy.Request(
                url=next_page,
                meta={"dont_filter": True}
            )        
        
    def parse_auto(self, response, url):
        auto = AutoItem()
        #auto["Id"] = response.url.re("\d+")[0]
#        auto["Link"] = response.url
        auto["Link"] = url
        auto["Nimi"] = response.css('h1::text').get()
        auto["Liik"] = response.css('.field-liik td.field span::text').get()
        auto["Keretüüp"] = response.css('.field-keretyyp td.field span::text').get()
        auto["Esmareg"] = response.css('.field-month_and_year td.field span::text').get()
        auto["Mootor"] = response.css('.field-mootorvoimsus td.field span::text').get()
        auto["Kütus"] = response.css('.field-kytus td.field span::text').get()
        auto["Odomeeter"] = response.css('.field-labisoit td.field span::text').get()
        auto["Istekohti"] = response.css("tr:contains('istekohti:') td.value::text").get()
        auto["Mootori_maht"] = response.css("tr:contains('maht') td:contains('l').value::text").get()
        auto["Võimsus_kW"] = response.css("tr:contains('kW') td.value::text").get()
        auto["Võimsus_hj"] = response.css("tr:contains('hj') td.value::text").get()
        auto["Tühimass"] = response.css("tr:contains('tühimass:') td.value::text").get()
        auto["Täismass"] = response.css("tr:contains('täismass:') td.value::text").get()
        auto["Kütusekulu"] = response.css("tr:contains('keskmine') td:contains('l/100 km').value::text").get()
        auto["CO2"] = response.css("tr:contains('g/km') td.value::text").get()
        auto["Ostetud_Riigist"] = response.css(".-brought_from b::text").get()
        auto["Käigukast"] = response.css(".field-kaigukast_kaikudega span.value::text").get()
        auto["Vedav_Sild"] = response.css(".field-vedavsild .value::text").get()
        auto["Pikkus"] = response.css("tr:contains('pikkus') td.value::text").get()
        auto["Laius"] = response.css("tr:contains('laius') td.value::text").get()
        auto["Kõrgus"] = response.css("tr:contains('kõrgus') td.value::text").get()
        auto["Teljevahe"] = response.css("tr:contains('kõrgus') td.value::text").get()
        auto["Hind"] = response.css(".field-hind span.value::text").get()
        auto["Soodushind"] = response.css(".field-soodushind span.value::text").get()
        auto["Liigitus"] = response.css("a.b-breadcrumbs__item:nth-of-type(1)::text").get()
        auto["Mark"] = response.css("a.b-breadcrumbs__item:nth-of-type(2)::text").get()
        auto["Mudel"] = response.css("a.b-breadcrumbs__item:nth-of-type(3)::text").get()
#        auto["Staatus"] = response.css("div.-status").get()
        auto["Staatus"] = response.xpath("//div[@class='-status']//text()").extract()
        auto["VAT"] = response.css(".vat-value::text").get()
        auto["Kubatuur"] = response.css("tr:contains('maht') td:contains('cm').value::text").get()

        yield auto