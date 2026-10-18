# NewsCrawler

**NewsCrawler** is a Python-based news web scraping and data collection project designed to crawl news articles from Indonesian online news portals. It extracts article information such as titles, authors, publication dates, categories, tags, and article contents for downstream data processing and analysis.

The project supports multiple news sources through configurable extraction rules and integrates with Apache Airflow for scheduled crawling workflows and Google Cloud Storage (GCS) for data storage.

## Features
- **Multi-source news crawling** — Collects articles from various Indonesian national and regional news portals.
- **Article metadata extraction** — Extracts titles, authors, publication dates, categories, tags, and article contents where available.
- **Configurable scraping rules** — Uses XPath expressions and source-specific configurations to handle different website structures.
- **Scheduled crawling** — Uses Apache Airflow DAGs to automate news collection.
- **Topic-based crawling** — Supports crawling news articles based on a specified topic.
- **Pagination handling** — Supports navigating article index pages to collect multiple articles.
- **Content cleaning** — Includes source-specific exclusion rules to filter unwanted text and related-article content.
- **Cloud storage integration** — Supports storing collected data in Google Cloud Storage.

## Supported News Sources
The source configuration includes the following news portals, among others:

| Category | News Sources |
|---|---|
| National news | Antara News, CNN Indonesia, Detik, Kompas, Tempo, Tribunnews |
| Business and finance | Bisnis.com, CNBC Indonesia, Kontan, Warta Ekonomi |
| General news | BeritaSatu, Liputan6, Merdeka, Okezone, Republika, Suara |
| Regional news | Berita Jakarta and multiple regional Tribunnews portals |
| Other sources | IDN Times, Kumparan, Medcom, iNews, Jakarta Post, VIVA |

The available sources and their extraction rules are defined in the project configuration. Actual crawling success depends on website availability, page structure, and access restrictions.

## How It Works
The project uses a source-processing-storage workflow.

1. **Source selection** — Selects a news portal and, optionally, a topic and publication date.
2. **Article discovery** — Retrieves article URLs from news index pages.
3. **Content extraction** — Extracts article metadata and text using source-specific XPath rules.
4. **Processing** — Passes collected records through a processing component.
5. **Data storage** — Encodes the collected data as JSON and writes it to Google Cloud Storage.
6. **Scheduling** — Apache Airflow DAGs orchestrate and schedule the crawling pipeline.

## Project Structure
The following is a conceptual overview of the main components referenced in the project:

```text
NewsCrawler/
├── config.py
├── all.py
├── all_topic.py
├── dags/
│   └── news_crawler/
│       └── source/
├── dags_builder/
├── processor/
├── sink/
└── coder/
```

The exact repository structure may contain additional modules and configuration files.

| Component | Purpose |
|---|---|
| `config.py` | Defines source-specific URLs, XPath selectors, date formats, and extraction rules. |
| `all.py` | Defines Airflow DAGs for crawling news from configured sources. |
| `all_topic.py` | Defines an Airflow DAG for topic-based news crawling. |
| `dags/` | Contains DAG-related and news source modules. |
| `dags_builder/` | Provides the generic DAG construction functionality. |
| `processor/` | Contains data processing components. |
| `sink/` | Handles data output, including Google Cloud Storage integration. |
| `coder/` | Provides data encoding functionality. |

## Technologies Used

- **Python** — Core programming language.
- **Apache Airflow** — Workflow orchestration and scheduled execution.
- **XPath** — HTML element selection and article data extraction.
- **Google Cloud Storage** — Cloud-based storage for crawled data.
- **JSON** — Data encoding and output format.

## Configuration

News sources are configured using source-specific settings, including:

- `NAME` — Display name of the news source.
- `START` — Starting URL or endpoint for crawling.
- `ARTICLES` — XPath expression for discovering article URLs.
- `NEXT_PAGES` — XPath expression for locating pagination links.
- `TITLE` — XPath expression for extracting article titles.
- `AUTHOR` — XPath expression for extracting author information.
- `DATE` and `DATE_FORMAT` — Publication date extraction and formatting.
- `TAG` — XPath expression for extracting article tags.
- `CATEGORY` — XPath expression for extracting article categories.
- `CONTENTS` — XPath expression for extracting article text.

Some sources also define additional rules for excluding irrelevant content, handling forms, or configuring requests.

## Running the Project

NewsCrawler uses Apache Airflow DAGs and shared project modules. Running the complete pipeline therefore requires the appropriate project environment and dependencies.

### 1. Clone the repository

```bash
git clone https://github.com/sarahreiaisyah/NewsCrawler.git
cd NewsCrawler
```

### 2. Set up the environment

Prepare a Python environment with the dependencies required by the project, including Apache Airflow and the modules used by the crawling, processing, encoding, and storage components.

Install dependencies using the repository's dependency file if one is provided.

### 3. Configure the environment

Before running the pipeline, configure the required Airflow connections and variables.

The current DAG definitions reference the following settings:

- `gcp_datalyst_production` — Google Cloud connection ID.
- `gcp_datalyst_project` — Google Cloud project variable.
- `gcs_datalyst_bucket` — Google Cloud Storage bucket variable.
- `news_crawler_proxy_secret` — Proxy configuration variable when proxy usage is enabled.

These settings must be configured in the target Airflow environment as needed.

### 4. Configure news sources

Select the desired news sources in the relevant DAG configuration and adjust their crawling parameters as necessary.

For topic-based crawling, specify the news source and topic in the source configuration.

### 5. Run through Apache Airflow

Deploy the DAG files to the appropriate Airflow DAG directory, configure the required connections and variables, and enable the relevant DAGs in the Airflow interface.

The DAG definitions include scheduled execution, retry settings, and catch-up behavior. Actual execution depends on the Airflow environment and the availability of the required services.

## Output

The GCS sink constructs output paths using the news source and Airflow execution date.

A typical output path follows this pattern:

```text
news-crawling/<source>/<execution-date>/<source>_<execution-date>
```

For topic-based crawling, the output path also includes the topic:

```text
news-crawling/<source>/<execution-date>/<source>_<topic>_<execution-date>
```

The collected records are encoded as JSON before being passed to the storage component.

## Use Cases

NewsCrawler can support several downstream applications, including:

- News trend analysis and monitoring.
- Natural language processing (NLP).
- Topic modeling and document classification.
- News aggregation and indexing.
- Data collection for research and academic projects.
- Time-series analysis of news publication activity.

## Limitations

- Website HTML structures and XPath selectors may change over time.
- Some news portals may restrict automated requests or require proxy access.
- Available article metadata varies between sources.
- Some sources may require source-specific request parameters or form submissions.
- Successful execution depends on external website availability and the configured infrastructure.

## Disclaimer

This project is intended for educational, research, and data analysis purposes. Users are responsible for complying with applicable laws, website terms of service, robots.txt directives, copyright requirements, and rate limits when collecting news data.

## Repository

GitHub: [sarahreiaisyah/NewsCrawler](https://github.com/sarahreiaisyah/NewsCrawler)
