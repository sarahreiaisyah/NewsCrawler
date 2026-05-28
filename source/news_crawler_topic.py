import pandas as pd
import re
import pytz
import requests
import json

from uuid import uuid4
from jinja2 import Environment
from datetime import datetime

from source.base import BaseSource

class NewCrawlerTopic(BaseSource):

    def __init__(self, news_source, published_date, topic, meta=None, *args, **kwargs):
        super(NewCrawlerTopic, self).__init__(*args, **kwargs)
        
        self.news_source = news_source
        self.published_date = published_date
        self.topic = topic
        self.meta = meta
        self.BODY = [{
            "operationName":"SearchAllStoriesV2",
            "variables":{"query":topic,"cursor":"1","size":100,"cursorType":"PAGE","sortType":"PUBLISHED_AT_DESC"},
            "query":"query SearchAllStoriesV2($query: String!, $cursor: String, $cursorType: CursorType!, $size: Int!, $sortType: StorySortType) {\n  SearchAllStoriesV2(query: $query, cursor: $cursor, cursorType: $cursorType, size: $size, sortType: $sortType) {\n    ...StoryCursor\n    __typename\n  }\n}\n\nfragment StoryCursor on StoryCursor {\n  edges {\n    ...Story\n    __typename\n  }\n  cursorInfo {\n    ...CursorInfo\n    __typename\n  }\n  __typename\n}\n\nfragment Story on Story {\n  __typename\n  id\n  authorID\n  title\n  createdAt\n  updatedAt\n  deletedAt\n  publishedAt\n  source\n  isAgeRestrictedContent\n  slug\n  status\n  leadText\n  publisherID\n  publishedRevisionID\n  draftRevisionID\n  metaDescription\n  metaKeyword\n  customTrackerImpressionURL\n  customTrackerScript\n  sponsorID\n  location {\n    Name\n    Lat\n    Lon\n    Country\n    AdmAreaLvl1\n    AdmAreaLvl2\n    AdmAreaLvl3\n    AdmAreaLvl4\n    __typename\n  }\n  internalCreatorID\n  lastUpdatedBy\n  isCleanView\n  isStickyStory\n  isShowOnWeb\n  isShowOnApp\n  isDisableComment\n  isDisableLike\n  isSnackable\n  isPrivate\n  sponsor {\n    ...Sponsor\n    __typename\n  }\n  author {\n    ...SimpleUser\n    __typename\n  }\n  publisher {\n    ...Publisher\n    __typename\n  }\n  editors {\n    ...SimpleUser\n    __typename\n  }\n  reporters {\n    ...SimpleUser\n    __typename\n  }\n  headline {\n    ...Headline\n    __typename\n  }\n  storyAddOns {\n    ...StoryAddOn\n    __typename\n  }\n  contentPublish {\n    ...Document\n    __typename\n  }\n  leadMedia {\n    ...Media\n    __typename\n  }\n  topics {\n    ...Topic\n    __typename\n  }\n  channel {\n    ...CompactChannel\n    __typename\n  }\n  statistic {\n    ...StoryStatistic\n    __typename\n  }\n  collection {\n    ...CompactCollection\n    __typename\n  }\n  readEligibility\n  productInfo {\n    ...Product\n    __typename\n  }\n  contentTeaser {\n    ...Document\n    __typename\n  }\n  internalTags\n  readTimeInMinutes\n}\n\nfragment StoryStatistic on StoryStatistic {\n  storyID\n  commentCount\n  likeCount\n  __typename\n}\n\nfragment CompactChannel on Channel {\n  id\n  name\n  slug\n  is_visible\n  __typename\n}\n\nfragment Media on Media {\n  id\n  title\n  description\n  publicID\n  externalURL\n  awsS3Key\n  height\n  width\n  locationName\n  locationLat\n  locationLon\n  mediaType\n  mediaSourceID\n  photographer\n  eventDate\n  internalTags\n  __typename\n}\n\nfragment Topic on Topic {\n  __typename\n  id\n  name\n  slug\n  description\n  coverMedia {\n    ...Media\n    __typename\n  }\n  metaName\n  metaKeywordsV2\n  metaDescription\n}\n\nfragment Sponsor on Sponsor {\n  id\n  name\n  description\n  url\n  media {\n    ...Media\n    __typename\n  }\n  __typename\n}\n\nfragment SimpleUser on User {\n  __typename\n  id\n  name\n  username\n  aboutMe\n  isVerified\n  profilePictureMedia {\n    ...Media\n    __typename\n  }\n  coverPictureMedia {\n    ...Media\n    __typename\n  }\n  status\n  metaKeyword\n  metaTitle\n  metaDescription\n}\n\nfragment Publisher on Publisher {\n  ...SimplePublisher\n  coverMedia {\n    ...Media\n    __typename\n  }\n  publisherGroupID\n  twitterURL\n  instagramURL\n  facebookURL\n  isPremium\n  domains\n  website\n  email\n  organisation {\n    ...Organisation\n    __typename\n  }\n  owners {\n    __typename\n    id\n    name\n  }\n  createdAt\n  metaTitle\n  metaKeywords\n  metaDescription\n  enableGeneralPushNotificationForMember\n  enableSegmentedPushNotificationForMember\n  __typename\n}\n\nfragment SimplePublisher on Publisher {\n  __typename\n  id\n  name\n  slug\n  description\n  isVerified\n  isPremium\n  avatarMedia {\n    ...Media\n    __typename\n  }\n  instagramURL\n  twitterURL\n  facebookURL\n  website\n  isCorporateSubscriber\n}\n\nfragment Organisation on Organisation {\n  id\n  name\n  phone1\n  address\n  email\n  companyName\n  editorialInChief\n  editorialCompositions {\n    ...EditorialComposition\n    __typename\n  }\n  __typename\n}\n\nfragment EditorialComposition on EditorialComposition {\n  id\n  organisationID\n  position\n  names\n  order\n  __typename\n}\n\nfragment Headline on Headline {\n  storyID\n  desktopMedia {\n    ...Media\n    __typename\n  }\n  mobileMedia {\n    ...Media\n    __typename\n  }\n  startTime\n  endTime\n  __typename\n}\n\nfragment StoryAddOn on StoryAddOn {\n  object {\n    __typename\n    ... on Polling {\n      ...Polling\n      __typename\n    }\n    ... on Gallery {\n      ...Gallery\n      __typename\n    }\n    ... on KumparanDerma {\n      ...KumparanDerma\n      __typename\n    }\n    ... on Form {\n      ...Form\n      __typename\n    }\n    ... on Recipe {\n      ...Recipe\n      __typename\n    }\n  }\n  addOnType\n  __typename\n}\n\nfragment Polling on Polling {\n  __typename\n  id\n  name\n  description\n  mediaID\n  startsAt\n  endsAt\n  questions {\n    ...Question\n    __typename\n  }\n}\n\nfragment Question on Question {\n  id\n  pollingID\n  detail\n  position\n  choices {\n    ...Choice\n    __typename\n  }\n  __typename\n}\n\nfragment Choice on Choice {\n  id\n  questionID\n  detail\n  mediaID\n  position\n  stats\n  __typename\n}\n\nfragment Gallery on Gallery {\n  name\n  description\n  __typename\n  id\n  createdAt\n  updatedAt\n  galleryMedias {\n    ...GalleryMedia\n    __typename\n  }\n}\n\nfragment GalleryMedia on GalleryMedia {\n  mediaID\n  description\n  caption\n  media {\n    ...Media\n    __typename\n  }\n  __typename\n}\n\nfragment KumparanDerma on KumparanDerma {\n  id\n  __typename\n}\n\nfragment Form on Form {\n  __typename\n  id\n  title\n  description\n  generateStatus\n  lastGenerated\n  createdBy {\n    ...SimpleUser\n    __typename\n  }\n  createdAt\n  updatedAt\n  endDate\n  pages {\n    ...FormPage\n    __typename\n  }\n  respondent\n  coverMedia {\n    ...Media\n    __typename\n  }\n  accentColor\n  backgroundColor\n  completedResponseTitle\n  completedResponse\n  formResponseConfirmationMail {\n    ...FormResponseConfirmationMail\n    __typename\n  }\n}\n\nfragment FormPage on FormPage {\n  page\n  questions {\n    ...FormQuestion\n    __typename\n  }\n  __typename\n}\n\nfragment FormQuestion on FormQuestion {\n  id\n  formId\n  type\n  description\n  title\n  isRequired\n  createdAt\n  updatedAt\n  addOns {\n    ...QuestionAddOns\n    __typename\n  }\n  __typename\n}\n\nfragment QuestionAddOns on QuestionAddOns {\n  colcount\n  choicesOrder\n  hasOther\n  otherText\n  optionsCaption\n  hasNone\n  hasSelectAll\n  valueTrue\n  valueFalse\n  labelTrue\n  labelFalse\n  rows\n  placeholder\n  choices\n  fileType\n  __typename\n}\n\nfragment FormResponseConfirmationMail on FormResponseConfirmationMail {\n  title\n  header\n  body\n  hyperlinkURL\n  hyperlinkTitle\n  __typename\n}\n\nfragment Recipe on Recipe {\n  id\n  name\n  description\n  mediaID\n  media {\n    ...Media\n    __typename\n  }\n  portionSize\n  ingredients\n  instructions {\n    step\n    instruction\n    __typename\n  }\n  cookingTime\n  calories\n  createdAt\n  createdBy {\n    ...SimpleUser\n    __typename\n  }\n  updatedAt\n  updatedBy {\n    ...SimpleUser\n    __typename\n  }\n  __typename\n}\n\nfragment Document on Document {\n  id\n  document\n  type\n  __typename\n}\n\nfragment Product on Product {\n  id\n  sku\n  objectID\n  objectType\n  object {\n    ... on Story {\n      id\n      slug\n      title\n      leadText\n      author {\n        id\n        username\n        __typename\n      }\n      publisher {\n        id\n        slug\n        __typename\n      }\n      leadMedia {\n        id\n        externalURL\n        __typename\n      }\n      __typename\n    }\n    ... on Collection {\n      id\n      slug\n      title\n      description\n      coverMedia {\n        id\n        externalURL\n        __typename\n      }\n      __typename\n    }\n    ... on SubscriptionPackage {\n      ...SimpleSubscriptionPackage\n      __typename\n    }\n    __typename\n  }\n  normalPrice {\n    ...Money\n    __typename\n  }\n  price {\n    ...Money\n    __typename\n  }\n  taxCategory {\n    ...TaxCategory\n    __typename\n  }\n  __typename\n}\n\nfragment TaxCategory on TaxCategory {\n  id\n  name\n  rateInPercentage\n  isInclusive\n  __typename\n}\n\nfragment Money on Money {\n  currencyCode\n  units\n  cents\n  __typename\n}\n\nfragment SimpleSubscriptionPackage on SubscriptionPackage {\n  id\n  name\n  subscriptionDescription: description\n  isActive\n  isRecurring\n  period\n  periodType\n  gracePeriodInSeconds\n  platform\n  __typename\n}\n\nfragment CompactCollection on Collection {\n  __typename\n  id\n  title\n  isPinned\n  slug\n  createdAt\n  readEligibility\n  updatedAt\n  lastStoryAddedAt\n  description\n  coverMedia {\n    ...Media\n    __typename\n  }\n  readEligibility\n  productInfo {\n    ...Product\n    __typename\n  }\n  storiesCount\n  videoDescriptionLink\n  premiumInfo {\n    setPremiumAt\n    __typename\n  }\n  kumparanPlusInfo {\n    createdAt\n    __typename\n  }\n  topics {\n    ...Topic\n    __typename\n  }\n}\n\nfragment CursorInfo on CursorInfo {\n  size\n  count\n  countPage\n  hasMore\n  cursor\n  cursorType\n  nextCursor\n  __typename\n}\n"
        }]
        self.EPOCH = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.UTC)

    def get(self, context, *args, **kwargs):
        today = context[self.published_date]
        print('TODAY: {}'.format(today))
        self.render_param(context=context)

        # Get HTML Response
        r = requests.post('https://graphql-v4.kumparan.com/query', data=json.dumps(self.BODY))
        raw = r.json()[0]['data']['SearchAllStoriesV2']['edges']

        # Get All News Data
        result = {}
        for idx, article in enumerate(raw):
            temp_dict = dict.fromkeys(['author','content','date','link','media','tags','title'])
            temp_doc = json.loads(article['contentPublish']['document'])
            temp_dict['author'] = article['author']['name']
            temp_dict['content'] = self.get_content(temp_doc)
            temp_dict['date'] = datetime.strptime(article['createdAt'], '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=pytz.UTC)
            temp_dict['link'] = self.get_link(article)
            temp_dict['media'] = 'Kumparan'
            temp_dict['tags'] = self.get_tags(article)
            temp_dict['title'] = article['title'].strip()
            result[idx] = temp_dict

        # Result Dictionary to Dataframe
        result_df = pd.DataFrame.from_dict(result, orient='index')

        # Filter Today's Date
        df = result_df.copy()
        df['localized_date'] = df.date.apply(lambda x: datetime.strftime(x.astimezone('Asia/Jakarta'), '%Y-%m-%d'))
        df = df.loc[df.localized_date == today]

        # Convert Date to Millis
        df['date'] = df.date.apply(lambda x: self.unix_time_millis(x))

        # Remove Columns Localized Date from Dataframe
        df = df.drop('localized_date', 1)
        print(df)

        self.data_count += df.shape[0]
        
        return df
    
    def render_param(self, context):
        env = Environment()
        if self.meta is not None:
            for k,v in self.meta.items():
                self.meta[k] = env.from_string(v).render(**context)
            
    def get_content(self, doc):
        content = []
        for node in doc['document']['nodes']:
            for node1 in node['nodes']:
                if node1['object'] == 'text':
                    for text in node1['leaves']:
                        content.append(text['text'])
                elif node1['object'] == 'inline':
                    for inline_node in node1['nodes']:
                        if inline_node['object'] == 'text':
                            for text in inline_node['leaves']:
                                content.append(text['text'])

        content = ' '.join(stc.strip() for stc in content)
        content = re.sub(r'\s([,?.!"](?:\s|$))', r'\1', re.sub("\s\s+" , " ", content))
        return content

    def get_link(self, article):
        slug = article['slug']
        if article['publisher'] == None:
            pub_slug = article['author']['username']
        else:
            pub_slug = article['publisher']['slug']
        return 'kumparan.com'+ '/' + pub_slug + '/' + slug

    def get_tags(self, article):
        topics = article['topics']
        tags = []
        for topic in topics:
            tags.append(topic['name'])
        return ', '.join([tag.strip() for tag in tags])

    def unix_time_millis(self, dt):
        return int((dt - self.EPOCH).total_seconds() * 1000)