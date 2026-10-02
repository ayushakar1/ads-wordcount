# Distributed Word Count

A small distributed word-count application using:

- **RPyC** for client-server communication
- **Redis** for caching word-count results
- **Docker Compose** to run the client, server, and cache

## Run

From the project directory:

```bash
docker compose up --build
```

The client connects to the server and queries `alice.txt`, showing cache-miss and cache-hit results. Stop the services with:

```bash
docker compose down
```

## Project structure

- `client/client.py` — sends word-count requests
- `server/server.py` — counts words and stores results in Redis
- `data/alice.txt` — sample input file
- `docker-compose.yml` — service configuration
- `Dockerfile` — Python runtime image

