from datetime import datetime, timedelta

from airflow import DAG

from dags_builder.generic_dag_builder import build
from coder.json import encode
from sink.gcs import GCSSink
from processor.base import BaseProcessor

from dags.news_crawler.source.news_crawler_topic import NewCrawlerTopic

def create_dag(dag_name, news_source, start_date, schedule_interval, published_date, use_proxy, topic):
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': start_date,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
    file_prefix = "news-crawling/%s/{{ ds }}/%s_%s_{{ ds }}" % (news_source, news_source, topic.replace(" ", ""))

    meta = None
    if use_proxy:
        meta = {
            "proxy": "{{ var.value.news_crawler_proxy_secret }}"
        }

    source = NewCrawlerTopic(news_source, published_date, topic, meta=meta)
    proc = BaseProcessor()
    sink = GCSSink(gcp_conn_id="gcp_datalyst_production", 
        gcp_project="{{ var.value.gcp_datalyst_project }}",
        gcs_bucket="{{ var.value.gcs_datalyst_bucket }}", 
        file_path=file_prefix, 
        encode_func=encode)

    dag = DAG(dag_name, default_args=default_args, schedule_interval=schedule_interval, catchup=True)
    build(dag, source=source, sink=sink, processor=proc)

    return dag

default_start_date = datetime(2021, 6, 1)
default_schedule_interval = "30 17 * * *" 

new_sources = [
    {"name": "kumparan", "topic": "banjir jakarta"}
]

for n in new_sources:
    news_name = n["name"]
    start_date = n["start_date"] if "start_date" in n else default_start_date
    schedule_interval = n["schedule_interval"] if "schedule_interval" in n else default_schedule_interval
    dag_name = "news_crawler_topic" + '_' + news_name 
    published_date = "tomorrow_ds"
    use_proxy = "use_proxy" in n and n["use_proxy"]
    topic = n["topic"]

    globals()[dag_name] = create_dag(dag_name, news_name, start_date, schedule_interval, published_date, use_proxy, topic)
