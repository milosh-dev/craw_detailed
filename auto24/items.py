# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass

class ListItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()         #
    mark = scrapy.Field()       #
    mudel = scrapy.Field()      #
    versioon = scrapy.Field()   #
    aasta = scrapy.Field()      # Esmareg
    mootor = scrapy.Field()     #
    kW = scrapy.Field()         #
    kubatuur = scrapy.Field()   #
    hind = scrapy.Field()       #
    odomeeter = scrapy.Field()  #
    vat = scrapy.Field()        #
    kütus = scrapy.Field()      #
    käigukast = scrapy.Field()  #
    kere = scrapy.Field()       #
    vedav = scrapy.Field()      #
    url = scrapy.Field()        #

class AutoItem(scrapy.Item):
    Id = scrapy.Field()    #serializer=int)
    Link = scrapy.Field()    #serializer=str)
    Nimi = scrapy.Field()    #serializer=str)
    Liik = scrapy.Field()    #serializer=str)
    Keretüüp = scrapy.Field()    #serializer=str)
    Esmareg = scrapy.Field()    #serializer=str)
    Mootor = scrapy.Field()    #serializer=str)
    Kütus = scrapy.Field()    #serializer=str)
    Odomeeter = scrapy.Field()    #serializer=int)
    Istekohti = scrapy.Field()    #serializer=int)
    Mootori_maht = scrapy.Field()    #serializer=float)
    Võimsus_kW = scrapy.Field()    #serializer=int)
    Võimsus_hj = scrapy.Field()    #serializer=float)
    Tühimass = scrapy.Field()    #serializer=int)
    Täismass = scrapy.Field()    #serializer=int)
    Kütusekulu = scrapy.Field()    #serializer=float)
    CO2 = scrapy.Field()    #serializer=float)
    Ostetud_Riigist = scrapy.Field()    #serializer=str)
    Käigukast = scrapy.Field()    #serializer=str)
    Vedav_Sild = scrapy.Field()    #serializer=str)
    Pikkus = scrapy.Field()    #serializer=int)
    Laius = scrapy.Field()    #serializer=int)
    Kõrgus = scrapy.Field()    #serializer=int)
    Teljevahe = scrapy.Field()    #serializer=int)
    Hind = scrapy.Field()    #serializer=int)
    Soodushind = scrapy.Field()    #serializer=int)
    Liigitus = scrapy.Field()    #serializer=str)
    Mark = scrapy.Field()    #serializer=str)
    Mudel = scrapy.Field()    #serializer=str)
    Staatus = scrapy.Field()    #serializer=str)
    VAT = scrapy.Field()    #serializer=str)
    VAT_Status = scrapy.Field()     #serializer=bool)
    Versioon = scrapy.Field()    #serializer=str)
    Kere = scrapy.Field()    #serializer=str)
    Kubatuur = scrapy.Field()    #serializer=int)
    Aasta = scrapy.Field()    #serializer=int)
    Kuu = scrapy.Field()    #serializer=int)
    Ülevaatus = scrapy.Field()    #serializer=str)
    Date = scrapy.Field()