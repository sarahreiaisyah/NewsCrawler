import os
import re
import json
import locale
import dateutil.parser
import pendulum

from scrapy.http import Request, FormRequest
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from scrapy import Selector
from datetime import datetime, timezone, timedelta, date
from dateutil import tz
import time
import logging

from config import CONFIG
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

class PortalSpider(Spider):
    name = 'portalspider'
    allowed_domains = CONFIG['ALLOWED_DOMAIN']

    def start_requests(self):
        if self.portal['NAME'] == 'CNN':
            yield Request(self.portal['START'] % self.date, headers={'User-Agent': CONFIG['USER_AGENT']}, dont_filter=True, meta=self.meta)
        elif self.portal['NAME'] == 'Bisnis':
            yield Request(self.portal['START'] % self.date, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'Kontan':
            # date_tmp = datetime.strptime(self.date, '%Y-%m-%d')
            date_tmp = self.date
            day = date_tmp.strftime("%d")
            month = date_tmp.strftime("%m")
            year = date_tmp.strftime("%Y")
            yield Request(self.portal['START'] % (day, month, year), headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'VIVA':
            self.portal['FORM_DATA']['last_publish_date'] = self.date + " 23:59:59"
            yield FormRequest(self.portal['START'], headers={'User-Agent': CONFIG['USER_AGENT']}, formdata=self.portal['FORM_DATA'], meta=self.meta)
        elif self.portal['NAME'] in ["Media Indonesia", "Jakarta Post", "Berita Jakarta"]:
            yield Request(self.portal['START'], headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'Antara News':
            date_tmp = datetime.strptime(self.date, '%Y-%m-%d')
            date_tmp = datetime.strftime(date_tmp, '%d-%m-%Y')
            yield Request(self.portal['START'] % self.date, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'Pikiran Rakyat':
            yield Request(self.portal['START'], headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Inilah':
            date = self.date.split("-")
            self.portal['FORM_DATA']['tanggal'] = str(int(date[2]))
            self.portal['FORM_DATA']['bulan'] = str(int(date[1]))
            self.portal['FORM_DATA']['tahun'] = str(int(date[0]))
            yield FormRequest(self.portal['START'], headers={'User-Agent': CONFIG['USER_AGENT']}, formdata=self.portal['FORM_DATA'], meta=self.meta)
        elif self.portal['NAME'] == 'Suara':
            print("DATE "+str(self.date))
            year = str(self.date).split("-")[0]
            print("YEAR "+year)
            yield Request(self.portal['START'] % year, headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Republika':
            date_tmp = datetime.strptime(self.date, '%Y-%m-%d')
            self.portal['FORM_DATA']['day'] = date_tmp.strftime("%d")
            self.portal['FORM_DATA']['month'] = date_tmp.strftime("%m")
            self.portal['FORM_DATA']['year'] = date_tmp.strftime("%Y")
            yield Request(self.portal['START'] % (0, self.portal['FORM_DATA']['year'], self.portal['FORM_DATA']['month'], self.portal['FORM_DATA']['day']), headers={'User-Agent': self.portal['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'Kumparan':
            yield Request(self.portal['START'], headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'INews':
            date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
            date_tmp = datetime.strftime(date_tmp, '%d-%m-%Y')
            yield Request(self.portal['START'] % date_tmp, headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Jpnn':
            date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
            day = date_tmp.strftime("%d")
            month = date_tmp.strftime("%m")
            year = date_tmp.strftime("%Y")
            yield Request(self.portal['START'] % (day, month, year), headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Medcom':
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            yield Request(self.portal['START'], callback=self.parse_medcom, headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Wartaekonomi':
            date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
            date_tmp = datetime.strftime(date_tmp, '%Y%m%d')
            yield Request(self.portal['START'] % date_tmp, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'Voi':
            yield Request(self.portal['START'] % str(self.date), headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Grid':
            date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
            day = date_tmp.strftime("%d")
            month = date_tmp.strftime("%m")
            year = date_tmp.strftime("%Y")
            yield Request(self.portal['START'] % (year, month, day), headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Merdeka':
            date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
            date_tmp = datetime.strftime(date_tmp, '%Y/%m/%d')
            yield Request(self.portal['START'] % date_tmp, headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == 'Tribun':
            print('self date', self.date)
            date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
            day = date_tmp.strftime("%d")
            month = date_tmp.strftime("%m")
            year = date_tmp.strftime("%Y")
            month_int = int(month)
            new_date = year + "-" + str(month_int) + "-" + day
            yield Request(self.portal['START'] % new_date, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'Indozone':
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
            day = str(int(date_tmp.strftime("%d")))
            month = date_tmp.strftime("%B").replace("Peb", "Feb")
            year = date_tmp.strftime("%Y")
            date_range = '%20'.join([day, month, year, '-', day, month, year])
            start = self.portal['START'] + date_range
            yield Request(start, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        else:
            yield Request(self.portal['START'] % self.date, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)

    def __init__(self, date='', portal='DETIK', meta=None, **kwargs):
        super().__init__(**kwargs)
        self.portal = CONFIG[portal.upper()]
        self.meta = meta
        self.tz = pendulum.timezone('Asia/Jakarta')

        if self.portal['NAME'] in ['Liputan6', 'Okezone', 'Metrotvnews','CNBC', 'CNN']:
            date = str(date).replace('-', '/')
        elif self.portal['NAME'] == 'Berita Satu':
            tmp = date.split("-")
            date = "{}-{}-{}".format(tmp[2], tmp[1], tmp[0])
        elif self.portal['NAME'] == 'Detik':
            # tmp = date.split("-")
            # date = "{}/{}/{}".format(tmp[1], tmp[2], tmp[0])
            date = date.strftime("%m/%d/%Y")
            # tmp = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            # date = tmp.strftime("%m/%d/%Y")
        elif self.portal['NAME'] == 'Jakarta Post':
            locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
            self.stop = False
        elif self.portal['NAME'] == 'Berita Jakarta':
            self.data_json = json.loads("{}")
            self.stop = False
        elif self.portal['NAME'] == 'Suara':
            date = str(date)
            self.stop = False

        self.cnn_attr = {
            'page': 1,
            'articles_size': 0
        }

        self.kumparan_attr = {
            'page': 1,
            'articles_size': 0
        }

        self.jawapos_attr = {
            'page': 0,
            'articles_size': 0
        }

        self.date = date

        self.links = []

    def parse(self, response):
        if self.portal['NAME'] == "Jawapos" and self.portal['FORM_DATA']['date'] != '':
            jsonresponse = json.loads(response.body.decode("utf-8"))
            selector = Selector(text=jsonresponse['posts'], type="html")
            articles = selector.xpath(self.portal['ARTICLES']).extract()
        else:
            articles = response.xpath(self.portal['ARTICLES']).extract()
        #self.links.append(articles)
        print('ARTICLES: {}'.format(articles))
        #print('LINKS: {}'.format(self.links))
        #with open("/mnt/c/Users/muham/Documents/Datalyst/dataset/news-links/Links_{}_{}.json".format(self.portal['NAME'], self.date.replace('-','').replace('/','')), "w") as text_file:
        #    final_links = json.dumps(self.links)
        #    text_file.write(final_links)
        count = 0
        skip_count = 0
        category = ''
        for article in articles:
            if self.portal['NAME'] == "Tribun" or self.portal['NAME'] in CONFIG["TRIBUN_2"]:
                if self.filter_by_date(response, count) == 1:
                    article = '{}?page=all'.format(article)
                    count = count + 1
                else:
                    if skip_count == 20:
                        return
                    else:
                        skip_count = skip_count + 1
                        count = count + 1
                        continue
            elif self.portal['NAME'] == "CNN":
                article = article.replace("\\", "")
            elif self.portal['NAME'] == "Kumparan":
                article = 'https://www.kumparan.com{}'.format(article)
            elif self.portal['NAME'] == "Liputan6" and "/foto-" in article:
                continue
            elif self.portal['NAME'] == "Bisnis" and "koran.bisnis" in article:
                continue
            elif self.portal['NAME'] == "Kontan":
                article = '{}?page=all'.format(article)
            elif self.portal['NAME'] in ["Media Indonesia", "Pikiran Rakyat"]:
                if self.filter_by_date(response, count) == 0:
                    return
                elif self.filter_by_date(response, count) == 2:
                    count = count + 1
                    continue
                count = count + 1
            elif self.portal['NAME'] == "Antara News":
                if ("www.antaranews.com/video" in article) or ("www.antaranews.com/foto" in article):
                    count = count + 1
                    continue
                category = self.get_category_from_article_list(response, count)
                count = count + 1
            elif self.portal['NAME'] == "Okezone" and "lifestyle" in article:
                continue
            elif self.portal['NAME'] == "VIVA":
                if self.filter_by_date(response, count) != 1:
                    return
                count = count + 1
            elif self.portal['NAME'] in ["Jakarta Post", "Suara"] and self.stop:
                return  
            elif self.portal['NAME'] == "Merdeka":
                if "foto" in article:
                    continue
                if self.filter_by_date(response, count) != 1:
                    return
                article = "https://www.merdeka.com"+article+"?page=all"
                count = count + 1
            elif self.portal['NAME'] == "Sindo":
                if ("gensindo.sindonews.com" in article) or ("makassar.sindonews.com" in article):
                    continue
            elif self.portal['NAME'] == "Detik":
                if ("20.detik.com" in article) or ("news.detik.com/foto-news" in article):
                    continue
                article = article + '?single=1'
            elif self.portal['NAME'] == 'Republika' and self.portal['FORM_DATA']['csrf_token_1f575b49'] == '':
                break
            elif self.portal['NAME'] in ['Wartaekonomi', 'Grid', 'Kompas']:
                article = article + '?page=all'
            elif self.portal['NAME'] == 'Jawapos' and self.portal['FORM_DATA']['date'] == '':
                break

            req = Request(article, callback=self.parse_article, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)   
            req.meta['item'] = {}

            if category:
                req.meta['item'] = {'category':category}
            else:
                req.meta['item'] = {}
            time.sleep(1)  
            yield req

        pages = []
        if self.portal['NAME'] == 'CNN'  and len(articles) > 0:
            self.cnn_attr['articles_size'] = len(articles)
            self.cnn_attr['page'] = self.cnn_attr['page'] + 1
            new_page = self.parse_cnn_next_page()
            pages.append(new_page)
        elif self.portal['NAME'] == 'Republika':
            self.portal['FORM_DATA']['csrf_token_1f575b49'] = response.xpath(self.portal['CSRF_TOKEN']).extract_first()
            pages = []
            if len(articles) > 0:
                self.portal['FORM_DATA']['offset'] = str(int(self.portal['FORM_DATA']['offset']) + 50)
                yield Request(self.portal['START'] % (self.portal['FORM_DATA']['offset'], self.portal['FORM_DATA']['year'], self.portal['FORM_DATA']['month'], self.portal['FORM_DATA']['day']), self.parse, headers={'User-Agent': self.portal['USER_AGENT']}, meta=self.meta)
        elif self.portal['NAME'] == 'Kumparan':
            self.kumparan_attr['articles_size'] = len(articles)
            self.kumparan_attr['page'] = self.kumparan_attr['page'] + 1
            self.portal['PAYLOAD']['variables']['cursor'] = self.kumparan_attr['page']
            yield Request(self.portal['NEXT_PAGES'], self.parse, method="POST", body=json.dumps(self.portal['PAYLOAD']), meta=self.meta)
        elif self.portal['NAME'] == 'VIVA':
            pages = []
            data = response.xpath(
                '//script/text()')[-1].re("window.last_publish_date = (.+?);\n")
            self.portal['FORM_DATA']['last_publish_date'] = data[0].strip('\"')
            yield FormRequest(self.portal['START'], self.parse, headers={'User-Agent': CONFIG['USER_AGENT']}, formdata=self.portal['FORM_DATA'], meta=self.meta)
        elif self.portal['NAME'] == "Berita Jakarta" and self.stop:
            pages = []
        elif self.portal['NAME'] == 'Suara':
            next_page = response.xpath(self.portal['NEXT_PAGES']).extract()
            if response.xpath('//li[@class="active"]/span/text()').extract_first() == '500':
                next_page = None
            else:
                next_page = next_page[-1]
            if next_page is not None:
                year = str(self.date).split("-")[0]
                yield Request(self.portal['START'] % year + next_page, self.parse, headers={'User-Agent': CONFIG['USER_AGENT']})
        elif self.portal['NAME'] == "Jawapos":
            pages = []
            self.jawapos_attr['page'] += 1
            self.portal['FORM_DATA']['date'] = self.date
            self.portal['FORM_DATA']['page_no'] = self.jawapos_attr['page']
            print(self.portal['FORM_DATA'])
            if len(articles) > 0:
                yield Request(self.portal['NEXT_PAGES'], self.parse, method="POST", body=json.dumps(self.portal['FORM_DATA']), meta=self.meta)
        else:
            pages = response.xpath(self.portal['NEXT_PAGES']).extract()

        for next_page in pages:
            if self.portal['NAME'] == 'Suara Merdeka':
                next_page = "https://www.suaramerdeka.com/index.php/news/indeks{}".format(next_page)
            else:
                yield response.follow(next_page, self.parse, headers={'User-Agent': CONFIG['USER_AGENT']}, meta=self.meta)
        
    def parse_title(self, response):
        title = response.xpath(self.portal['TITLE']).extract_first()
        if self.portal['NAME'] == 'Tempo':
            regex = re.compile(r'[\n\r\t]')
            title = regex.sub("", title)
        elif self.portal['NAME'] == 'CNN':
            title = self.strip(title)
        elif self.portal['NAME'] == 'Berita Jakarta':
            title = self.data_json['description']
        elif self.portal['NAME'] == 'Kontan':
            title = title.replace(" - Page all", "")
        elif self.portal['NAME'] == 'Republika':
            if title:
                title = title.replace(" | Republika Online", "").replace(" | IHRAM", "")
        elif self.portal['NAME'] == 'Suara':
            if title.strip() == '':
                title = response.xpath('//article[@class="detail"]//h1/text()').extract_first()
            if title == None:
                title = response.xpath('//div[@class="writer"]/span/author/text()').extract_first()

        if title is not None:
            title = title.strip()
        else:
            title = ""

        return title

    def parse_author(self, response):
        author = response.xpath(self.portal['AUTHOR']).extract_first()
        if self.portal['NAME'] in ['Tribun', 'Antara News']:
            if author:
                nrt_strip = re.compile(r'[\n\r\t]')
                author = nrt_strip.sub("", author)
                author = author.replace("Editor: ", "").replace("Penulis: ", "")
        elif self.portal['NAME'] in ['Pikiran Rakyat', "Jakarta Post"]:
            author = self.strip(author)
        elif self.portal['NAME'] == "Metrotvnews":
            author = author.split('•')
            author = author[0]
            author = self.strip(author)
        elif self.portal['NAME'] == "Suara Merdeka":
            regex = re.compile(r'\(.+\/.+\/.+\)', re.IGNORECASE)
            author = response.xpath('//p[@style="font-weight: bold;"]/text()').extract_first()
            author = regex.findall(author)[0]
            author = author.split('/')
            author = author[0][1:]
        elif self.portal['NAME'] == 'Berita Jakarta':
            author = self.data_json['author']['name']
        elif self.portal['NAME'] == 'Kumparan':
            author = response.xpath(self.portal['AUTHOR']).re('\"name\":\"([^"\n\r]*)\"')[0]
        elif self.portal['NAME'] == 'Suara':
            if author.strip() == '':
                author = response.xpath('span[@class="pull-left"]/text()').extract_first()
            if author == None:
                author = response.xpath('div[@class="writer"]/span/author/text()').extract_first()
        elif self.portal['NAME'] == 'INews':
            author = author.split('·')
            author = author[0]
            author = author.strip()
        elif self.portal['NAME'] == 'Medcom':
            if author is None:
                author = response.xpath('//div[@class="name"]/text()').extract_first()
            else:
                author = author[:author.find('•')-1]
        elif self.portal['NAME'] == 'Voi':
            author = response.xpath(self.portal['AUTHOR']).extract()
            if len(author) == 1:
                author = author[0]
            else:
                author = "Reporter: " + author[0].strip() + '| Editor: ' + author[1]

        if author is not None:
            author = author.strip()
        else:
            author = ""

        return author

    def change_date_format(self,date):
        component = date.split(" ")
        months = ["Januari","Februari", "Maret", "April","Mei", "Juni","Juli","Agustus", "September", "Oktober","November","Desember"]
        indeks = 0
        for month in months:
            indeks+=1
            if indeks < 10:
                ind = "0"+str(indeks)
            else:
                ind = str(indeks)
            if month  == component[1]:
                return ind+"-"+component[0]+"-"+component[2]
        return date

    def parse_date(self, response):
        date = response.xpath(self.portal['DATE']).extract_first()
        if self.portal['NAME'] == "Media Indonesia":
            date = date.replace("Pada: ", "")
        elif self.portal['NAME'] == "Metrotvnews":
            date = date.split('•')
            date = date[1]
            date = self.strip(date)
        elif self.portal['NAME'] == 'Inilah':
            datas = response.xpath('//h6/text()').extract()
            for data in datas:
                if "|" in data:
                    date = data.split("|")
                    if len(date[0]) <= 5:
                        date = date[1]
                    else:
                        date = date[0]
        elif self.portal['NAME'] == 'Berita Jakarta':
            date = self.data_json['datePublished']
        elif self.portal['NAME'] in ['Suara Merdeka', 'Idntimes']:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.replace(tzinfo=self.tz).astimezone(tz=timezone.utc)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] == 'Kumparan':
            date = response.xpath(self.portal['DATE']).re('\"datePublished\":\"([^"\n\r]*)\"')[-1]
        elif self.portal['NAME'] == 'Medcom':
            if date is None:
                date = response.xpath('//div[@class="date"]/text()').extract_first()
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            date = date.replace("Februari", "Pebruari")
            if date.find('/') == -1:
                date = date[date.find('•')+1:].strip()
                date = datetime.strptime(date, self.portal['DATE_FORMAT'])        
            else:
                date = datetime.strptime(date, '%A %d %B %Y / %H:%M')
            date = date.replace(tzinfo=self.tz).astimezone(tz=timezone.utc)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] == 'Voi':
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            date = date[:date.find('|')].strip()
            date = date.replace("Feb", "Peb")
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.replace(tzinfo=self.tz).astimezone(tz=timezone.utc)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] == 'CNN':
            date = str(date).replace('/', '-')
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.replace(tzinfo=self.tz).astimezone(tz=timezone.utc)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] in ['Idntimes','CNBC','Detik','Grid','Kompas','Kontan','Suara','VIVA']:
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.replace(tzinfo=self.tz).astimezone(tz=timezone.utc)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] == 'Jpnn':
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            remove_char = date[-11]
            date = date.replace(remove_char, "-")
            date = date.replace("Februari", "Pebruari")
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] == 'Merdeka':
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            date = date + ':00'
            date = date.replace("Februari", "Pebruari")
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] in ['Tribun','Rmolsumsel', 'Pikiran Rakyat', 'Sindo', 'Wartaekonomi', 'Tempo']:
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            date = date.replace("Februari", "Pebruari")
            date = date.replace("Jum'at", "Jumat")
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] in CONFIG['TRIBUN_2']:
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] == ['INews']:
            date = datetime.strptime(date, self.portal['DATE_FORMAT'])
            date = date.replace(tzinfo=self.tz).astimezone(tz=timezone.utc)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            if 'WITA' in date:
                date = date + timedelta(hours=1)
            elif 'WIT' in date:
                date = date + timedelta(hours=2)
            
        # Date normalizer
        if date is not None:
            date = dateutil.parser.parse(date)
        else:
            date = dateutil.parser.parse(self.date)
        return int(date.timestamp() * 1000)

    def parse_tag(self, response):
        tags = response.xpath(self.portal['TAG']).extract()
        if self.portal['NAME'] in ['Suara','INews','Medcom','Jpnn','Wartaekonomi','Voi','Indozone','Rmolsumsel','Grid']:
            tag = response.xpath(self.portal['TAG']).extract_first()
            return tag
        elif self.portal['NAME'] == 'Media Indonesia':
            cleaned_tags = [tag.strip().replace('#', '') for tag in tags if tag.strip()]
            return ', '.join(cleaned_tags)
        else:
            return ', '.join([tag.strip() for tag in tags if tag.strip()])

    def parse_category(self, response):
        category = response.xpath(self.portal['CATEGORY']).extract_first()

        if self.portal['NAME'] == 'Republika':
            if category is None:
                category = '-'
            else:
                category = self.strip(category)
        elif self.portal['NAME'] == 'Berita Satu':
            category = response.request.url.split("/")[3]
        elif self.portal['NAME'] == 'Suara Merdeka':
            category = category.split("\\")[2]
            category = self.strip(category)
        elif self.portal['NAME'] == 'Inilah':
            category = response.request.url.split("/")[2]
            category = category.split(".")[0]
        elif self.portal['NAME'] == 'Suara':
            if category is None:
                category = response.xpath(self.portal['ALT_CATEGORY']).extract_first()
        elif self.portal['NAME'] == 'INews':
            category = response.xpath(self.portal['CATEGORY']).extract()
            if len(category) == 1:
                category = category[0]
            else:
                category = category[1]
        elif self.portal['NAME'] in ['Jpnn','Wartaekonomi', 'Voi','Rmolsumsel']:
            category = response.xpath(self.portal['CATEGORY']).extract()
            if len(category) != 0:
                category = category[1]
        elif self.portal['NAME'] == 'Medcom':
            if category is None:
                category = '-'
            elif len(category) != 0:
                category = category[1]
            else:
                category = response.xpath('//script/text()').extract_first()
                category = category[category.find('dimension3')+14:]
                category = category[:category.find(',')-1].replace("'","")
        elif self.portal['NAME'] == 'Idntimes':
            if len(category) != 0:
                category = category[2]

        if category is not None:
            category = category.strip()
        else:
            category = ""

        return category

    def parse_content(self, response):
        regex = re.compile(r'[\n\r\t]')
        try:
            exclude_link = response.xpath(
                self.portal['EXCLUDE_LINK']).extract()
        except Exception:
            exclude_link = []

        has_exclude_text = False
        if 'EXCLUDE_TEXT' in self.portal:
            has_exclude_text = True
            exclude_text = re.compile(
                self.portal['EXCLUDE_TEXT'], re.IGNORECASE)

        has_stop_criteria = False
        if 'STOP_CRITERION' in self.portal:
            has_stop_criteria = True
            stop_criteria = re.compile(
                self.portal['STOP_CRITERION'], re.IGNORECASE)

        contents_result = ''
        contents = response.xpath(self.portal['CONTENTS']).extract()
        if self.portal['NAME'] == "Media Indonesia":
            contents = contents[7:]
        elif self.portal['NAME'] == "Suara":
            if len(contents) == 0:
                contents = response.xpath('//div[@class="detail--content"]/p//text()').extract()
        elif self.portal['NAME'] == 'INews':
            contents = contents[:-4]
        elif self.portal['NAME'] == 'Wartaekonomi':
            contents = contents[:-5]

        for content in contents:
            if content in exclude_link:
                continue
            elif has_exclude_text and exclude_text.match(content):
                continue
            elif "googletag" in content:
                continue
            
            content_norm = regex.sub("", content)

            if has_stop_criteria and stop_criteria.match(content):
                break
            
            contents_result = '{} {}'.format(contents_result, content_norm)
            contents_result = self.strip(contents_result)

        if contents_result is not None:
            contents_result = contents_result.strip()
        else:
            contents_result = ""

        return contents_result

    def parse_article(self, response):
        item = response.meta['item']
        is_store = True

        if self.portal['NAME'] == 'Berita Jakarta':
            data = response.xpath(
                '//script[@type="application/ld+json"][2]/text()').extract_first()
            self.data_json = json.loads(data)
            if self.filter_by_date(response, 0) == 0:
                self.stop = True
                return
            elif self.filter_by_date(response, 0) == 2:
                return

        if self.portal['NAME'] in ["Jakarta Post", "Kumparan", "Suara"]:
            if self.filter_by_date(response, 0) == 0:
                self.stop = True
                return
            elif self.filter_by_date(response, 0) == 2:
                return
        elif self.portal['NAME'] == 'CNN':
            art_date = response.xpath('//div[@class="date"]/text()').extract_first()
            print('art_date cnn', art_date)
            art_date = datetime.strptime(art_date, "%A, %d %b %Y %H:%M WIB")
            # art_date = art_date.replace("Feb", "Peb")
            art_date = art_date.replace(tzinfo=self.tz).astimezone(tz=timezone.utc)
            art_date = datetime.strftime(art_date,'%Y/%m/%d')
            print('art_date after formatted', art_date)
            print('self date', self.date)
            if(art_date != self.date):
                print('stop crawling')
        try:
            item['title'] = self.parse_title(response)
            item['date'] = self.parse_date(response)
            item['author'] = self.parse_author(response)
            item['tags'] = self.parse_tag(response)

            if self.portal['NAME'] == "Antara News":
                item['category'] = item['category']
            else:
                item['category'] = self.parse_category(response)
            if 'content' in item:
                item['content'] = item['content'] + ' ' + self.parse_content(response)
            else:
                item['content'] = self.parse_content(response)
            if 'link' not in item:
                item['link'] = response.request.url
            item['media'] = self.portal['NAME']
            item['link_next_page'] = self.parse_link_next_page(response)
        except Exception as e:
            print("Error", e.args[0])
            print("============================================================")
            is_store = False
        
        if is_store:
            if item['link_next_page']:
                if self.meta is not None:
                    return Request(item['link_next_page'], callback=self.parse_article, meta={'item': item, "proxy":self.meta["proxy"]})
                else:
                    return Request(item['link_next_page'], callback=self.parse_article, meta={'item': item})
            else:
                del item['link_next_page']
                return item

    def strip(self, string):
        result = string.rstrip()
        result = result.lstrip()

        return result

    def filter_by_date(self, response, count):
        if self.portal['NAME'] == "Media Indonesia":
            # art_date_tmp = response.xpath(
            #     self.portal['ART_DATE']).extract()[count]
            # art_date_tmp = art_date_tmp.split(",")
            # art_date = art_date_tmp[1][1:]
            # art_date = datetime.strptime(art_date, '%d %b %Y')
            art_date_tmp = response.xpath(self.portal['ART_DATE']).extract()[count]
            art_date = datetime.strptime(art_date_tmp, '%d/%m/%Y %H:%M')
            # art_date = datetime.strftime(art_date)
            # art_date = datetime.strptime(art_date, '%Y-%m-%d %H:%M:%S')
        elif self.portal['NAME'] == "Tribun":
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            art_date = response.xpath(
                self.portal['ART_DATE']).extract()[count]
            art_date = art_date.replace("Februari", "Pebruari")
            art_date = datetime.strptime(art_date, self.portal['DATE_FORMAT'])
            # art_date = art_date.replace(hour=0, minute=0, second=0) ##
        elif self.portal['NAME'] in CONFIG['TRIBUN_2']:
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            art_date = response.xpath(
                self.portal['ART_DATE']).extract()[count]
            art_date = datetime.strptime(art_date, self.portal['DATE_FORMAT'])
        elif self.portal['NAME'] == "VIVA":
            art_date = response.xpath(self.portal['ART_DATE']).extract()
            if ("jam" in art_date[0]) or ("menit" in art_date[0]):
                return 1
            date_now = datetime.now()
            date_now = date_now.replace(tzinfo=timezone.utc).astimezone(tz=self.tz)
            art_date = art_date[0].split(" ")[0]
            art_date = date_now - timedelta(days=int(art_date)+1)
        elif self.portal['NAME'] == "Merdeka":
            art_date = response.xpath(
                self.portal['ART_DATE']).extract()[count]
            art_date = art_date.replace("Februari", "Pebruari")
            art_date = datetime.strptime(art_date, '%A, %d %B %Y %H:%M:%S')
        elif self.portal['NAME'] == "Pikiran Rakyat":
            art_date = response.xpath(self.portal['ART_DATE']).extract()[count]
            dates = art_date.split(" ")
            dates[2] = str.rstrip(dates[2][:-1])
            art_date = dates[0] + " " + dates[1] + " " + dates[2]
            art_date = art_date.replace("Februari", "Pebruari")
            art_date = datetime.strptime(art_date, '%d %B %Y')
           
        elif self.portal['NAME'] == "Jakarta Post":
            date = response.xpath(self.portal['DATE']).extract_first()
            date = date[5:]
            art_date = datetime.strptime(date, '%B %d, %Y')
        elif self.portal['NAME'] == 'Berita Jakarta':
            art_date = datetime.strptime(
                self.data_json['datePublished'][0:10], '%Y-%m-%d')
        elif self.portal['NAME'] == 'Kumparan':
            art_date = datetime.strptime(
                response.xpath(self.portal['DATE']).re('\"datePublished\":\"([^"\n\r]*)\"')[-1], self.portal['DATE_FORMAT'])
        elif self.portal['NAME'] == 'Suara':
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            date = response.xpath(self.portal['DATE']).extract_first()
            print(str(date))
            art_date = datetime.strptime(date, self.portal['DATE_FORMAT'])
        elif self.portal['NAME'] == 'CNN':
            art_date = response.xpath('//div[@class="box feed"]/section/@date').extract_first()
            print('art date before', art_date)
            print('type art date before', type(art_date))
            art_date = datetime.strptime(art_date, "%Y/%m/%d")
            print('art date after format', art_date)
        if self.portal['NAME'] in ["Merdeka", "Tribun", "Pikiran Rakyat"]:
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            filter_date = datetime.strptime(str(self.date), '%Y-%m-%d')
        elif self.portal['NAME'] in CONFIG['TRIBUN_2']:
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            filter_date = datetime.strptime(str(self.date), '%Y-%m-%d')
        elif self.portal['NAME'] == 'CNN':
            # print('masuk cnn filter date')
            # print('self date', self.date)
            # print('art_date' , art_date)
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            filter_date = datetime.strptime(str(self.date), '%Y/%m/%d')
        elif self.portal['NAME'] == 'Media Indonesia':
            filter_date = datetime.combine(self.date, datetime.min.time())
        else:
            filter_date = datetime.strptime(self.date, '%Y-%m-%d')

        # print('DEBUG art_date:', art_date, type(art_date))
        # print('DEBUG filter_date:', filter_date, type(filter_date))
        print('ARTICLE DATE: {}'.format(art_date))
        print('FILTER DATE: {}'.format(filter_date))

        if art_date.date() == filter_date.date():
            return 1
        elif art_date.date() > filter_date.date():
            return 2
        else:
            return 0

    def get_category_from_article_list(self, response, count):
        art_cat = response.xpath(self.portal['CATEGORY'])[count].extract()
        return art_cat

    def parse_link_next_page(self, response):
        link_next_page = ''

        if self.portal["NAME"] in ["Okezone", "Sindo"]:
            link_next_page = response.xpath(self.portal['LINK_NEXT_PAGE']).extract_first()

        return link_next_page
    
    def parse_cnn_next_page(self):
        print('masuk fungsi next page cnn')
        path = self.portal['START'] % self.date
        print('path', path)
        page_number = self.cnn_attr['page']
        base_path = path[:35]
        link_date = path[-16:]
        next_page_link = base_path + "/2/" + str(page_number) + link_date
        print('new_page' , next_page_link)
        return next_page_link

    # def parse_pikiran_rakyat(self, response):
    #     json_response = json.loads(response.body_as_unicode())
    #     articles = json_response['data']
    #     for article in articles:
    #         filter_date = self.filter_by_date(article, 0)
    #         if filter_date == 2:
    #             continue
    #         elif filter_date == 0:
    #             return

    #         category_slug = article['category']['slug']
    #         date_ = article['published_at'].split(" ")[0]
    #         date_ = date_.replace("-", "/")
    #         url = "https://www.pikiran-rakyat.com/{}/{}/{}".format(
    #             category_slug, date_, article['slug'])
    #         yield Request(url, callback=self.parse_article, headers={'User-Agent': CONFIG['USER_AGENT']})

    #     next_page = json_response['meta']['current_page'] + 1
    #     yield Request(self.portal['START'] % next_page, self.parse_pikiran_rakyat, headers={'User-Agent': CONFIG['USER_AGENT']})

    def parse_medcom(self, response):
        date_tmp = datetime.strptime(str(self.date), '%Y-%m-%d')
        day = date_tmp.strftime("%d")
        month = date_tmp.strftime("%m")
        year = date_tmp.strftime("%Y")
        hrefs = response.xpath(self.portal['SUB_START']).extract()
        for href in hrefs:
            href = href+'/'+year+'/'+month+'/'+day
            print("HREF :", href)
            yield Request(href, callback=self.parse, headers={'User-Agent': CONFIG['USER_AGENT']})

# start_date = date(2025, 3, 5)
# end_date = date(2025, 3, 10)
# delta = timedelta(days=1)
# portal = "Kompas"

# while start_date <= end_date:
#     path = "/mnt/s/continuum/NEWS/testing/"+portal.lower()+"/"+str(start_date)
#     if not os.path.exists(path):
#         os.makedirs(path)
#     process = CrawlerProcess({
#         'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
#         # 'FEED_FORMAT': 'json',
#         # 'FEED_URI': path+"/"+str(start_date)+'.json'
#         'FEED_FORMAT': 'jsonlines',
#         # 'FEED_URI': path + "/" + str(start_date) '.jsonl',
#         'FEED_URI': path + "/" + str(start_date),
#     })
#     process.crawl(PortalSpider, date=start_date, portal=portal)
#     start_date += delta
#     process.start()

import argparse
from datetime import datetime
from scrapy.crawler import CrawlerProcess
import os

parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True)
parser.add_argument("--portal", required=True)
args = parser.parse_args()

run_date = datetime.strptime(args.date, "%Y-%m-%d").date()
portal = args.portal

path = f"/mnt/d/continuum/{portal.lower()}/{run_date}"
os.makedirs(path, exist_ok=True)
feed_uri = f"{path}/{run_date}"

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEEDS': {
        feed_uri: {
            'format': 'jsonlines',
            'encoding': 'utf-8'
        }
    },
    'FEED_EXPORT_ENCODING': 'utf-8',
})

process.crawl(PortalSpider, date=run_date, portal=portal)
process.start()
