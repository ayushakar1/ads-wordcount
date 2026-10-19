# Word count service - ADS lab

A client asks how often a keyword occurs in a text stored on the server. The server counts it and
caches the result in Redis, which also keeps track of the most requested keywords (hot keywords).
Three servers run behind a load balancer (least connections or least response time) that checks
the health of the servers.

## Files

```
wordcount/server.py      RPyC server: loads the texts, counts, uses the cache
wordcount/cache.py       Redis: cached counts and hot keywords
wordcount/client.py      client, one request per connection, measures the latency
balancer/proxy.py        load balancer, forwards the bytes of every connection to a server
balancer/algorithms.py   least connections and least response time
balancer/health.py       health checks
bench/loadgen.py         sends requests at fixed rates, one CSV file per run
bench/plot.py            figures for the report
bench/per_text.py        latency of cache hits and misses per text, for one run
scripts/fetch_data.py  downloads the movie scripts (IMSDb) into data/
tests/test_basic.py      tests
```

## Setup

```
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

To check whether each server is reachable from the load balancer:

```
for server in server1 server2 server3; do
  docker compose exec lb python -c \
    "import socket; s=socket.create_connection(('$server', 18861), 1); s.close(); print('$server: healthy')" \
    || echo "$server: unhealthy"
done
```

The load balancer settings are in `.env`:

- `LB_ALGORITHM`: `least_connections` or `least_response_time`
- `HEALTH_CHECKS`: `on`, or `off` (then it behaves like the load balancer of Phase 3)

After changing them: `docker compose up -d lb`.

## Experiments

Results are written to `results/` on the host. The plot script prints the values that are in the
figures: every point is the median of the runs, the bars go from the lowest to the highest run.


Phase 4: a 60 s run at 100 requests/s. In a second terminal stop server2 when the load generator
prints `20 s` and start it again at `40 s`:

```
docker exec client python -m bench.loadgen --label failover-lc --rates 100 --requests 6000 --progress
docker stop server2
docker ps -a
docker start server2
docker exec client python -m bench.plot timeline results/failover-lc/rate100_1.csv --stop 20 --start 40 --out results/figures/failover-lc
```

Do this four times: least connections and least response time, with `HEALTH_CHECKS=off` and `on`.
