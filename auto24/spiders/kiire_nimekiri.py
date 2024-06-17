import scrapy, httpx, re, time
from auto24.helpers.helper import (
    create_session,
    delete_session
)
from scrapy.utils.project import get_project_settings
from datetime import date   # For getting current date

class KiireNimekiriSpider(scrapy.Spider):
    name = "kiire_nimekiri"
    allowed_domains = ["www.auto24.ee"]
    # start_urls = ["https://www.auto24.ee/robots.txt"]
    counter = 0
    reset = 50
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
#        start_url = "https://www.auto24.ee/kasutatud/nimekiri.php?af=100&ak=26000"
        start_url = "https://www.auto24.ee/kasutatud/nimekiri.php?af=100"
        create_session(url=start_url, session_id = self.session_id)
        yield scrapy.Request(url=start_url)

    def closed(self, reason):
        # Called when the spider closes. 
        delete_session(self.session_id)

    def parse(self, response):
        kw = ""
        cbm = ""
        for a in response.css("div.result-row"):
            # MUDEL
            mudel_pikk = a.css(".description .title .main .model::text").get()
            if isinstance(mudel_pikk, str):
                mudel_pikk = mudel_pikk.strip()
            else:
                mudel_pikk = ""

            mudel_lyhike = a.css(".description .title .main .model-short::text").get()
            if isinstance(mudel_lyhike, str):
                mudel_lyhike = mudel_lyhike.strip()
            else:
                mudel_lyhike = ""

            mudel_t2psustus = mudel_pikk.replace(mudel_lyhike, "").strip()

            # HIND
            price = a.css(".price::text").get()
            if isinstance(price, str):
                price = int(price.replace("\xa0","").replace("€",""))

            if isinstance(a.css(".finance .small::text").get(), str):
                vat = True
                vat_suurus = a.css(".finance .small::text").get()
                if "22" in vat_suurus:
                    price = 1.22 * price            
            else:
                vat = False
            # LÄBISÕIT
            odo = a.css(".mileage::text").get()
            if isinstance(odo, str):
                odo = int(odo.replace("\xa0","").replace("km",""))

            # MOOTOR
            engine = a.css(".description .title .main .engine::text").get()
            if isinstance(engine, str):
                #kw = engine.re("\s(\d+)kW")[0]
                kw = re.findall("\s(\d+)kW", engine)
                if len(kw) != 0:
                    kw = int(kw[0])
                else:
                    kw = ""

                #cbm = engine.re("(\d+\.\d+)\s")[0]
                cbm = re.findall("(\d+\.\d+)\s", engine)
                if len(cbm) != 0:
                    cbm = float(cbm[0])
                else:
                    cbm = ""

            yield {
                "id": int(a.css('.row-link::attr(href)').re("\d+")[0]),
                "mark": a.css(".description .title .main span::text").get(),
                "mudel": mudel_lyhike,
                "versioon": mudel_t2psustus,
                "aasta": a.css(".description .title .year::text").get(),
#                "mootor": a.css(".description .title .main .engine::text").get(),
                "mootor": engine,
                "kW": kw,
                "kubatuur": cbm,
                "hind": price,
                "odomeeter": odo,
                "vat": vat,
#                "vat_suurus": a.css(".finance .small::text").get(),
                "kütus": a.css('.fuel::text').get(),
                "käigukast": a.css('.transmission::text').get(),
                "kere": a.css('.bodytype::text').get(),                
                "vedav": a.css('.drive::text').get(),                
                "url": a.css('.row-link::attr(href)').get()
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
            yield scrapy.Request(url=next_page)
            #yield response.follow(next_page, self.parse)
