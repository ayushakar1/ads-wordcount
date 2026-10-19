# Word count service - ADS lab

A client asks how often a keyword occurs in a text stored on the server. The server counts it and
caches the result in Redis, which also keeps track of the most requested keywords (hot keywords).

## Files

```
wordcount/server.py      RPyC server: loads the texts, counts, uses the cache
wordcount/cache.py       Redis: cached counts and hot keywords
wordcount/client.py      client, one request per connection, measures the latency
bench/loadgen.py         sends requests at fixed rates, one CSV file per run
bench/plot.py            figures for the report
bench/per_text.py        latency of cache hits and misses per text, for one run
scripts/fetch_data.py  downloads the movie scripts (IMSDb) into data/
tests/test_basic.py      tests
```

## Setup

```
docker compose up -d --build
    ```

Without Python on the host, download the scripts with
`docker run --rm -v "${PWD}:/w" -w /w python:3.12-slim python scripts/fetch_data.py`.

## Using it

```
docker exec client python -m wordcount.client matrix neo
docker exec client python -m wordcount.client hot 5
docker compose logs -f server1
```

## Experiments

Results are written to `results/` on the host. The plot script prints the values that are in the
figures: every point is the median of the runs, the bars go from the lowest to the highest run.

5 rates with 3 runs each:

```
docker exec client python -m bench.loadgen --label phase2 --rates 50 100 150 200 250 --repeat 3
docker exec client python -m bench.plot latency results/phase2 --out results/figures/phase2
docker exec client python -m bench.per_text results/phase2/rate50_1.csv
```
