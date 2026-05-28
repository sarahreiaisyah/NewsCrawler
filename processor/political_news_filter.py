import pandas as pd
import os
import re
import nltk 
import logging

from jinja2 import Environment
from datetime import datetime

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

from lib.sentiment_analyzer import SentimentAnalyzer
from processor.base import BaseProcessor
from util.string_util import clean_text
from util.path import path_resource

class PoliticalNewsProcessor(BaseProcessor):

    def __init__(self, project_name, project_topic, subject_file_path, 
        *args, **kwargs):
        super(PoliticalNewsProcessor, self).__init__(*args, **kwargs)
        self.subject_file_path = subject_file_path
        self.project_name = project_name
        self.project_topic = project_topic

    def process(self, df, context, *args, **kwargs):
        if df is None or df.shape[0] == 0:
            self.data_count = 0
            return None

        # load keywords
        keywords = self.get_keywords(self.subject_file_path, self.project_topic)
        print('KEYWORDS: {}'.format(keywords))

        # title and content preprocessing
        df_final = df.copy()
        df_final['title'] = df_final.title.apply(self.clean_text)
        df_final['content'] = df_final.content.apply(self.clean_text, ["?",",","."])
        #df_final['content'] = df_final.content.apply(self.clean_content)
        df_final['subject_base'] = df_final.apply(self.filter_news, args=[keywords], axis=1)

        # filter news
        print('=== TABLE PREVIEW ==')
        print(df_final)
        df_final = df_final[df_final.subject_base.notnull()]
        df_final = df_final.drop_duplicates(subset='link', keep='last')
        print('=== TABLE AFTER FILTER ==')
        print(df_final)
        if df_final is None or df_final.shape[0] == 0:
            self.data_count = 0
            return None
        df_final['project_topic'] = self.project_topic
        sa = SentimentAnalyzer(self.project_name, self.project_topic, keywords, 'basic')
        df_final = df_final.apply(self.get_sentiment, args=[sa, keywords], axis=1)
        df_final['associated_figures'] = df_final.apply(self.get_figure_associated, args=[self.subject_file_path, self.project_topic], axis=1)
        df_final = df_final.explode('associated_figures').reset_index().iloc[:,1:]
        self.data_count = df_final.shape[0]

        return df_final

    def get_keywords(self, path, project_topic):
        data = pd.read_csv(path, sep=";")
        data = data[data.subject == project_topic]
        keywords = []
        for _, row in data.iterrows():
            key = re.sub(r"[\[\]\"]", "", row['keywords'])
            key = key.replace(", ",",")
            key = key.split(",")
            keywords += key
        return keywords

    def clean_text(self, text, kept_symbols_list=None):
        result = text.lower()
        kept_symbols = ''

        if kept_symbols_list is not None:
            for symbol in kept_symbols_list:
                kept_symbols = '{0}\{1}'.format(kept_symbols, symbol)

        result = ' '.join(re.sub("(@[A-Za-z0-9{0}]+)|([^0-9A-Za-z{0} \t])|(\w+:\/\/\S+)".format(kept_symbols)," ",result).split())
        return result

    def whole_keywords_in_text(self, keywords, text):
        for keyword in keywords:
            if not self.is_empty_string(keyword):
                keyword = keyword.strip()
                if re.search(r'\b' + keyword + r'\b', text):
                    return True
        return False

    def are_keywords_in_text(self, keywords, text):
        for keyword in keywords:
            if not self.is_empty_string(keyword):
                keyword = keyword.strip()
                keyword = keyword.split(" ")
                if all(word in text for word in keyword):
                    return True
        return False

    def is_empty_string(self, string):
        if string == '' or string == ' ' or string is None:
            return True
        else:
            return False

    def filter_news(self, df, keywords):
        title = df['title']
        content = df['content']
        tags = df['tags']
        tags = self.clean_text(tags, kept_symbols_list=[','])
        tags = tags.split(',')
        if(self.whole_keywords_in_text(keywords, title) == True):
            return 'title'

        for tag in tags:
            if (self.whole_keywords_in_text(keywords, tag)) == True:
                return 'tags'
                
        if (self.whole_keywords_in_text(keywords, content) == True):
            return 'content'

        return None

    def get_figure_associated(self, df, path, project_topic):
        content = df['content']

        data = pd.read_csv(path, sep=";")
        data = data[data.subject != project_topic]
        associated_figures = []
        for _, row in data.iterrows():
            keys = re.sub(r"[\[\]\"]", "", row['keywords'])
            keys = keys.replace(", ",",")
            keys = keys.split(",")
            if self.whole_keywords_in_text(keys, content) == True:
                associated_figures.append(row['subject'])

        return associated_figures

    def get_sentiment(self, df, sa, keywords):
        subject_base = df['subject_base']
        title = df['title']
        content = df['content']
        if subject_base == 'title':
            sentiment_source = "title"
            sentiment = sa.calculate_sentiment_general(title, keywords)
            if(sentiment == 0):
                sentiment_source = "content"
                sentiment = sa.calculate_sentiment_general(content, keywords)
        else:
            sentiment_source = "content"
            sentiment = sa.calculate_sentiment_general(content, keywords)

        sentiment_status = sa.get_sentiment_class(sentiment)

        result = pd.Series([df.title, df.date, df.content, df.media, df.author, df.tags, df.link, df.subject_base, df.project_topic,
                           sentiment_source, sentiment_status, sentiment],
                           index=['title', 'date', 'content', 'media', 'author', 'tags', 'link', 'subject_base', 'project_topic',
                           'sentiment_base', 'sentiment_status', 'sentiment_score'])

        print(result)
        return result
        
    # function for clean content from sentences that are not related to the content itself
    def clean_content(self, content):
        content_keyword = ["lihat juga", "baca juga", "baca", "lihat", "simak video"]
        content_split = content.split(".")
        result = ""
        for sentence in content_split:
            if self.whole_keywords_in_text(content_keyword, sentence) == False:
                sentence = sentence.strip()
                if result:
                    result = result + sentence + ". "
                else:
                    result = sentence + ". "
        return result