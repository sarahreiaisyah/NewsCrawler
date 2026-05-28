from datetime import datetime, timedelta

from airflow import DAG

from dags_builder.generic_dag_builder import build
from coder.json import encode
from sink.gcs import GCSSink
from processor.base import BaseProcessor

from dags.news_crawler.source.news_crawler import NewCrawlerSource

def create_dag(dag_name, news_source, start_date, schedule_interval, published_date, use_proxy):
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': start_date,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
    file_prefix = "news-crawling/%s/{{ ds }}/%s_{{ ds }}" % (news_source, news_source)

    meta = None
    if use_proxy:
        meta = {
            "proxy": "{{ var.value.news_crawler_proxy_secret }}"
        }

    source = NewCrawlerSource(news_source, published_date, meta=meta)
    proc = BaseProcessor()
    sink = GCSSink(gcp_conn_id="gcp_datalyst_production", 
        gcp_project="{{ var.value.gcp_datalyst_project }}",
        gcs_bucket="{{ var.value.gcs_datalyst_bucket }}", 
        file_path=file_prefix, 
        encode_func=encode)

    dag = DAG(dag_name, default_args=default_args, schedule_interval=schedule_interval, catchup=True)
    build(dag, source=source, sink=sink, processor=proc)

    return dag

new_sources = [
    {"name": "detik"},
    {"name": "antaranews"},
    {"name": "beritajakarta"},
    {"name": "beritasatu"},
    {"name": "bisnis", "use_proxy":True},
    {"name": "cnn", "use_proxy":True},
    {"name": "inilah"},
    {"name": "jakartapost"},
    {"name": "kompas"},
    {"name": "kontan"},
    {"name": "liputan6"},
    {"name": "mediaindonesia"},
    {"name": "merdeka"},
    {"name": "metrotvnews"},
    {"name": "okezone"},
    {"name": "pikiran-rakyat"},
    {"name": "republika", "use_proxy":False},
    {"name": "sindo"},
    {"name": "suara"},
    {"name": "suaramerdeka"},
    {"name": "tempo", "use_proxy":True},
    {"name": "tribun", "use_proxy":True},
    {"name": "viva"},
    {"name": "cnbc", "use_proxy":True},
    {"name": "jawapos"},
    {"name": "inews"},
    {"name": "jpnn"},
    {"name": "medcom"},
    {"name": "wartaekonomi", "use_proxy":True},
    {"name": "voi"},
    {"name": "indozone"},
    {"name": "idntimes"},
    {"name": "rmolsumsel", "use_proxy":False},
    {"name": "grid"},
    {"name": "tribunaceh", "use_proxy":True},
    {"name": "tribunambon", "use_proxy":True},
    {"name": "tribunbali", "use_proxy":True},
    {"name": "tribunbangka", "use_proxy":True},
    {"name": "tribunbanjarmasin", "use_proxy":True},
    {"name": "tribunbanten", "use_proxy":True},
    {"name": "tribunbatam", "use_proxy":True},
    {"name": "tribunjabar", "use_proxy":True},
    {"name": "tribunjambi", "use_proxy":True},
    {"name": "tribunjateng", "use_proxy":True},
    {"name": "tribunjatim", "use_proxy":True},
    {"name": "tribunkaltara", "use_proxy":True},
    {"name": "tribunkaltim", "use_proxy":True},
    {"name": "tribunkupang", "use_proxy":True},
    {"name": "tribunlampung", "use_proxy":True},
    {"name": "tribunmakassar", "use_proxy":True},
    {"name": "tribunmanado", "use_proxy":True},
    {"name": "tribunpalu", "use_proxy":True},
    {"name": "tribunpapua", "use_proxy":True},
    {"name": "tribunpekanbaru", "use_proxy":True},
    {"name": "tribunpontianak", "use_proxy":True},
    {"name": "tribunsumsel", "use_proxy":True},
    {"name": "tribunternate", "use_proxy":True},
    {"name": "tribunbengkulu", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunpadang", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunmedan", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunjakarta", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunlombok", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunkalteng", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribungorontalo", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunsulbar", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunsultra", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunpapuabarat", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
    {"name": "tribunsorong", "use_proxy":True, "start_date": datetime(2024, 4, 1)},
]

for n in new_sources:
    news_name = n["name"]
    start_date = n["start_date"] if "start_date" in n else datetime(2021, 10, 20)
    schedule_interval = n["schedule_interval"] if "schedule_interval" in n else "30 17 * * *" 
    dag_name = "news_crawler" + '_' + news_name 
    published_date = "tomorrow_ds"
    use_proxy = "use_proxy" in n and n["use_proxy"]

    globals()[dag_name] = create_dag(dag_name, news_name, start_date, schedule_interval, published_date, use_proxy)
