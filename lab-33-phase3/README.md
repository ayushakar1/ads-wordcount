# Word count service - ADS lab

A client asks how often a keyword occurs in a text stored on the server. The server counts it and
caches the result in Redis, which also keeps track of the most requested keywords (hot keywords).
Three servers run behind a load balancer (least connections or least response time).

## Files

```
wordcount/server.py      RPyC server: loads the texts, counts, uses the cache
wordcount/cache.py       Redis: cached counts and hot keywords
wordcount/client.py      client, one request per connection, measures the latency
balancer/proxy.py        load balancer, forwards the bytes of every connection to a server
balancer/algorithms.py   least connections and least response time
bench/loadgen.py         sends requests at fixed rates, one CSV file per run
bench/plot.py            figures for the report
bench/per_text.py        latency of cache hits and misses per text, for one run
scripts/fetch_data.py  downloads the movie scripts (IMSDb) into data/
tests/test_basic.py      tests
```

## Setup

```
python scripts/fetch_data.py
docker compose up -d --build
docker exec client python -m pytest tests
```

Without Python on the host, download the scripts with
`docker run --rm -v "${PWD}:/w" -w /w python:3.12-slim python scripts/fetch_data.py`.

## Using it

```
docker exec client python -m wordcount.client matrix neo
docker exec client python -m wordcount.client hot 5
docker compose logs -f lb
docker compose logs -f server1
```

The load balancing algorithm is set in `.env` (`LB_ALGORITHM`: `least_connections` or
`least_response_time`). After changing it: `docker compose up -d lb`.

## Experiments

Results are written to `results/` on the host. The plot script prints the values that are in the
figures: every point is the median of the runs, the bars go from the lowest to the highest run.


Phase 3, the same requests through the load balancer, once per algorithm (`LB_ALGORITHM` in `.env`):

```
docker exec client python -m bench.loadgen --label phase3-lc --rates 50 100 150 200 250 --repeat 3
docker exec client python -m bench.loadgen --label phase3-lrt --rates 50 100 150 200 250 --repeat 3
docker exec client python -m bench.plot latency results/phase2 results/phase3-lc results/phase3-lrt --labels "1 server" "3 servers, LC" "3 servers, LRT" --out results/figures/phase3
```


remove data scripts, change data to data
rewrite the lodgen and bench working

why did it use 50 most common orruring and not a sample working sample set

whta is the i counter part in the run function, does the assignmnet really requie this part and have points for this??
