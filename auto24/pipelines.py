# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging, re
from datetime import date

class AutoPipeline:
    mydate = date.today().strftime("%Y-%m-%d")

    def process_item(self, item, spider):
        # ID .+(\\.+)$ /\d+
        try:
            Id = re.search("\/(\d+)", item["Link"])
            item['Id'] = Id.group(1)
        except:
            pass
        # HIND
        try:
            item['Hind'] = item['Hind'].replace("\xa0","").replace("EUR","")
        except Exception as e:
            pass       

        # SOODUSHIND
        try:
            item['Soodushind'] = item['Soodushind'].replace("\xa0","").replace("EUR","")
        except Exception as e:
            pass        

        # ODOMEETER
        try:
            item['Odomeeter'] = item['Odomeeter'].replace(" ","").replace("km","")
        except Exception as e:
            pass        

        # VERSIOON
        try:
            item['Versioon'] = item['Nimi'].replace(item["Mark"], "").strip()
        except:
            item['Versioon'] = ""

        try:
            item['Versioon'] = item['Versioon'].replace(item["Mudel"], "").strip()
        except:
            pass

        try:
            item['Versioon'] = item['Versioon'].replace(item["Mootor"], "").strip()
        except:
            pass

        # ÜLEVAATUS
        try:
            item['Ülevaatus'] = item['Staatus'][1]
        except:
            pass
        try:
            item['Staatus'] = ''.join(item['Staatus'])
        except:
            pass

        item['Hind'] = self.trim_int(item['Hind'])
        item['Soodushind'] = self.trim_int(item['Soodushind'])
        if item['Soodushind'] == None:
            item['Soodushind'] = item['Hind']
        item["CO2"] = self.trim_float(item["CO2"])
        item["Kubatuur"] = self.trim_int(item["Kubatuur"])
        item["Kütusekulu"] = self.trim_float(item["Kütusekulu"])
        item["Mootori_maht"] = self.trim_float(item["Mootori_maht"])
        item["Võimsus_kW"] = self.trim_int(item["Võimsus_kW"])
        item["Võimsus_hj"] = self.trim_float(item["Võimsus_hj"])
        item["Täismass"] = self.trim_int(item["Täismass"])
        item["Tühimass"] = self.trim_int(item["Tühimass"])
        item["Pikkus"] = self.trim_int(item["Pikkus"])
        item["Laius"] = self.trim_int(item["Laius"])
        item["Kõrgus"] = self.trim_int(item["Kõrgus"])
        item["Teljevahe"] = self.trim_int(item["Teljevahe"])
        item["Odomeeter"] = self.trim_int(item["Odomeeter"])

        # Kas hinnale lisandub käibemaks
        try:
            if 'Hinnale lisandub' in item["VAT"]:
                try:
                    item['Hind'] = item['Hind'] * 1.22
                    item['Soodushind'] = item['Soodushind'] * 1.22
                except:
                    pass
        except:
            pass

        try:
            if 'käibemaksu ei lisandu' in item["VAT"]:
                item["VAT_Status"] = False
            else:
                item["VAT_Status"] = True
        except:
            pass

        try:
            kp = item["Esmareg"].split("/")
            if len(kp) == 2:
                item["Aasta"] = self.trim_int(kp[1])
                item["Kuu"] = self.trim_int(kp[0])
            else:
                item["Aasta"] = self.trim_int(item["Esmareg"])
        except:
            pass

        item["Date"] = self.mydate

        return item

    def trim_int(self, text):
        try:
            return int(text.strip())
        except:
            pass
#            print (f"error {type(text)}, {text}") 
#            return text

    def trim_float(self, text):
        try:
            return float(text.strip())
        except:
            pass

class ListPipeline:
    def process_item(self, item, spider):
        auto = ItemAdapter(item)

        auto["mudel"] = auto["mudel"].strip()           # Model-short
        model = auto["versioon"].strip()              # Model

        auto["versioon"] = model.replace(auto["mudel"], "").strip()
        auto["hind"] = int(auto["hind"].replace("\xa0","").replace("€",""))

        for a in response.css("div.result-row"):

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


        return item
