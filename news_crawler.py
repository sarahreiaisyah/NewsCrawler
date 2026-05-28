import os
import tempfile
import pandas as pd

from uuid import uuid4
from jinja2 import Environment
from scrapy.crawler import CrawlerProcess

from source.base import BaseSource

from ..lib.crawler import PortalSpider

class NewCrawlerSource(BaseSource):

    def __init__(self, news_source, published_date, meta=None, *args, **kwargs):
        super(NewCrawlerSource, self).__init__(*args, **kwargs)
        
        self.news_source = news_source
        self.published_date = published_date
        self.meta = meta

    def get(self, context, *args, **kwargs):
        today = context[self.published_date]
        self.render_param(context=context)
        temp_folder = tempfile.mkdtemp()
        filename = str(uuid4())
        file_path = os.path.join(temp_folder, filename)
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'FEED_FORMAT': 'jsonlines',
            'FEED_URI': file_path
        })

        process.crawl(PortalSpider, date=today, portal=self.news_source, meta=self.meta)
        process.start()
        
        df = pd.read_json(file_path, lines=True)
        self.data_count += df.shape[0]

        if(os.path.exists(file_path)):
            os.remove(file_path)
        
        return df
    
    def render_param(self, context):
        env = Environment()
        if self.meta is not None:
            for k,v in self.meta.items():
                self.meta[k] = env.from_string(v).render(**context)