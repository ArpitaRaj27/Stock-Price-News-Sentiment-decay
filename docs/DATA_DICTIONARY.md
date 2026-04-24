# Data Dictionary

Schema for every table produced by the pipeline. Useful for reviewers, your future self, and anyone reproducing your work.

## `data/processed/prices.parquet`

One row per (ticker, trading day).

| Column      | Type       | Description                              |
|-------------|------------|------------------------------------------|
| date        | datetime64 | Trading date (no timezone)               |
| ticker      | string     | Stock symbol (e.g. AAPL)                 |
| adj_close   | float64    | Adjusted close price (USD)               |
| return      | float64    | Daily simple return = (P_t − P_{t-1})/P_{t-1} |

## `data/processed/news_raw.parquet`

One row per article.

| Column        | Type       | Description                              |
|---------------|------------|------------------------------------------|
| ticker        | string     | Associated stock symbol                  |
| datetime      | datetime64 | Article publication timestamp            |
| date          | datetime64 | Date portion (used for joining to prices)|
| headline      | string     | Article headline                         |
| source        | string     | Publisher name (e.g. "Reuters")          |
| source_tier   | string     | tier_1 / tier_2 / tier_3 / unknown       |
| url           | string     | Article URL (real mode only)             |

## `data/processed/news_scored.parquet`

`news_raw` + sentiment columns:

| Column         | Type    | Description                              |
|----------------|---------|------------------------------------------|
| sent_positive  | float64 | FinBERT P(positive)                      |
| sent_negative  | float64 | FinBERT P(negative)                      |
| sent_neutral   | float64 | FinBERT P(neutral)                       |
| sent_compound  | float64 | sent_positive − sent_negative ∈ [-1, 1]  |

## `data/processed/events.parquet`

One row per identified event.

| Column         | Type       | Description                              |
|----------------|------------|------------------------------------------|
| ticker         | string     | Stock symbol                             |
| date           | datetime64 | Event date                               |
| sector         | string     | GICS-style sector                        |
| direction      | string     | "positive" or "negative"                 |
| event_type     | string     | "sentiment" / "volume" / "both"          |
| max_abs_sent   | float64    | Strongest signed sentiment that day      |
| mean_sent      | float64    | Mean compound sentiment that day         |
| n_articles     | int64      | Article count that day                   |
| dominant_tier  | string     | Most common source tier among articles   |

## `data/processed/cars.parquet`

One row per (event, τ) pair. Long format.

| Column        | Type       | Description                              |
|---------------|------------|------------------------------------------|
| tau           | int64      | Trading days relative to event (-5 to +10) |
| date          | datetime64 | Calendar date corresponding to τ         |
| AR            | float64    | Abnormal return that day                 |
| CAR           | float64    | Cumulative AR from τ=0 to current τ      |
| ticker        | string     | Event ticker                             |
| event_date    | datetime64 | Event date (for joining)                 |
| sector        | string     | Event sector                             |
| direction     | string     | "positive" / "negative"                  |
| event_type    | string     | sentiment/volume/both                    |
| source_tier   | string     | Dominant tier of triggering articles     |
| sentiment     | float64    | Sentiment score that triggered event     |
