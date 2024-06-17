import scrapy, httpx, re, time
from auto24.helpers.helper import (
    create_session,
    delete_session,
    send_mail
)
from scrapy.utils.project import get_project_settings
from auto24.items import AutoItem
# from scrapy.mail import MailSender
# import config
# from datetime import date   # For getting current date

class YksikSoidukSpider(scrapy.Spider):
    name = "yksik_soiduk"
    allowed_domains = ["www.auto24.ee"]
    # start_urls = ["https://www.auto24.ee/soidukid/4005053"]
    counter = 0
    reset = 50
    pause = 15
#    mydate = ""

    # This defines the scraped files
    custom_settings = {
        # 'FEED_STORAGES' : {
        #     "gdrive": "scrapy_gdrive_exporter.gdrive_exporter.GoogleDriveFeedStorage",
        # },
        # 'GDRIVE_SERVICE_ACCOUNT_CREDENTIALS_JSON' : { 
        #     "type": "service_account",
        #     "project_id": "strategic-cacao-100620",
        #     "private_key_id": "f710fc7e61055e39554ce3019e976741737482ef",
        #     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQD07ydVsMFY/p3m\nhX0ODwuWEjp3VJwPlsnKgOK8XQzC58fMVjUcw5gou0x8Jeh/C4cpRGCB6l/kDSbn\nOiVe8wJ4maKIHpRYteSKW7X+r8QPSshwElyOctAFsrijMVbpmn/4Va7Vsh0PR346\nOMUlh6nBkjzeXqQbGwpM2C4eeGQk5TTacccQW79t8euQA5yzMcQ60egot84383cd\niYbQ9Zd5BE8bmGWTWh4pIEm/S4rQg8lbccL+0T3yqxkGIstoGRBAlM1ZoHgZAjtx\nB+jazJH7ZMPZMIZi2yQYeClP5KNPEv0A9n912qcH0Pc4oSyoiknfRPrEnasoqPoO\nOWYXAS0JAgMBAAECggEAOaIwkkRGKqe3BfAxLeayZjyhz0R0eGKV1vWe5I3Mm+wo\nIlfCpaMMocD4zVmqLILM6hPx1YAN0j6aAdy3wHDUCwazrO3tIDaksT3FREmdi6+g\nHGblqosvkbetJJFOjydQp2GaAySnG9pJxG9pTFxwwGClu/lvCgXB1bUknPzdK6Th\ngc6UB78gBnptLc8LfUIxpDZqFNRZ9u2yTKw/1WWUWbSlHQ7WPupz6ZVuI8EN6mXK\nDK7sW1clIMbNrTIFDbtLez+gvN3fR5rjvXHmIFQtP1RM1+1Zg2pxaQhaD3rdgwUw\nbERdz83CfoaRtKFrfC2A9Dh1ZlYzpBaQkzncNqaCRQKBgQD9WBhAEI4YIoShTVeZ\niqMww5gmdlVaprfoste9+74BnvTNgkPda4GRjbeeJTzn8ubWnme5FWOsBdjmGqqX\niKzi6GnpwuxZk7MK/DGB4I1IwiozkHBjYH4Tphlfv6WOLAQz7Bh1dwdBwlbOBUBd\n+c1DpnMVAoTp4OsloR4eBwqXDwKBgQD3gH0wPQY3S8jdjg1ap+gOQTB0kNPJwPLk\nHslqYWuMxDbNnmCtteuG2JOv+zfT/xGHG6W0A+XZ6D2MYZa+bThlWKWrFpGnVgtR\n2f3nDGdEhGNISHLR3mP02TL+OUsAhU5PJDn9PkOpVGZzt9VXtjV6IgUu+ImB8ZBM\nr3gWxCs6ZwKBgGEm40XOE2+V7R6eNjWfQK12lGZLgrfcrzIBQ1KLs3WTq3UTu0qx\n62IR4pQ224BnWbZ70HLdjPdu1pqHJ1wtAX+SeOs34MMJLOPNin6vyf5Y1y4m+bJi\nUnbef2SEbcxzfLkclNSW7KV/DSK8SM7A+MI0lnU8HhRCOGqZup7xPFJpAoGAQu9g\n6/bVA4dfX2vXeLkILTK8JAo2/M1N4xvgZQDL0VoPaDR4+QHGHMXdyy4pvw+wcdWs\nTq7vLqt8Wcbauc1X/zCmPUrxQUwn648E98OG+iTDpPzS8KcwaTuEavSbsBxdPVIS\nzMZWDilhO9JvxDTm6Yzh0f4tUhM+bz7VP3L2LekCgYEAjIEEkAJ8nKU/wtnpCFPN\njiAId/NFNzaA25H7wPfxH/VOLJJmO8MViV9GkUAQArV50lEC4O5NrnKlzcYnZrbw\nnXkIWUQGh7vYJU0+m4Hm4OTExuH2SkrwFd/07AsIEhkGP5xlW0lvuL/BOoNtr2Uw\n/q8EkYs+dkaRyRJ98pkU/ak=\n-----END PRIVATE KEY-----\n",
        #     "client_email": "auto24@strategic-cacao-100620.iam.gserviceaccount.com",
        #     "client_id": "111103906931787996863",
        #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        #     "token_uri": "https://oauth2.googleapis.com/token",
        #     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        #     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/auto24%40strategic-cacao-100620.iam.gserviceaccount.com",
        #     "universe_domain": "googleapis.com"
        # },
        'FEEDS': {
            "./scraped_files/%(name)s/%(name)s_%(time)s.csv" : {"format": "csv"},
#            "gdrive://drive.google.com/1mtRqiQGTz08L-W8BzGt9UK43yGunbo7s/%(name)s_%(time)s.csv": {"format": "csv"}
        },
    }

# EMAILi saatmiseks
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(YksikSoidukSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.feed_exporter_closed, signal=scrapy.signals.feed_exporter_closed)
        return spider

    def feed_exporter_closed(self):
        stats = self.crawler.stats.get_stats()
        print("start sending")
        send_mail(
            title = "Crawlab: " + self.name,
            scraper = self.name,
            message = f"Andmete kogumine on lõppenud\n\nStatistika on selline:\n{stats}"
        )
        print("end sending")

# EMAILi saatmiseks

    def start_requests(self):
        settings=get_project_settings()
        self.session_id = settings.get('MY_SESSION_ID')
#        self.mydate = date.today().strftime("%Y-%m-%d")
        #start_url = "https://www.auto24.ee/kasutatud/nimekiri.php?af=100"
        start_url = "https://www.auto24.ee/soidukid/3947685"
        create_session(url=start_url, session_id = self.session_id)
        yield scrapy.Request(url=start_url)

    def closed(self, reason):
        # Called when the spider closes. 
        delete_session(self.session_id)

        
    def parse(self, response):
        auto = AutoItem()
        #auto["Id"] = response.url.re("\d+")[0]
        auto["Link"] = response.url
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
