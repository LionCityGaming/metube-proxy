# MeTube Proxy

A lightweight HTTP API proxy for MeTube that exposes download statistics in a format compatible with Homepage dashboard widgets.

## Features

- Health check endpoint
- Statistics endpoint returning download queue and completion stats
- Configurable cache timeout (default: 5 minutes)
- Lightweight Flask-based API
- Docker container ready

## Environment Variables

- `METUBE_URL` - Base URL for MeTube instance (default: `http://metube:8081`)
- `CACHE_TIMEOUT` - Cache duration in seconds (default: `300` / 5 minutes)

## Endpoints

### GET /health
Returns `OK` with status 200 if the service is running.

### GET /stats
Returns MeTube statistics in JSON format:

```json
{
    "active_downloads": 2,
    "completed_downloads": 147,
    "pending_downloads": 5,
    "total_downloads": 154,
    "yt_dlp_version": "2024.12.23",
    "metube_version": "2026.01.11"
}
```

Where:
- `active_downloads`: Number of downloads currently in progress
- `completed_downloads`: Number of completed downloads
- `pending_downloads`: Number of downloads waiting to start
- `total_downloads`: Total number of downloads (active + completed + pending)
- `yt_dlp_version`: Version of yt-dlp being used
- `metube_version`: Version of MeTube

## Docker Usage

```bash
docker run -d \
  --name metube-proxy \
  -p 8082:5000 \
  -e METUBE_URL=http://metube:8081 \
  -e CACHE_TIMEOUT=300 \
  ghcr.io/lioncitygaming/metube-proxy:latest
```

## Docker Compose

```yaml
services:
  metube-proxy:
    image: ghcr.io/lioncitygaming/metube-proxy:latest
    container_name: metube-proxy
    ports:
      - "8082:5000"
    environment:
      - METUBE_URL=http://metube:8081
      - CACHE_TIMEOUT=300
    restart: unless-stopped
```

## Homepage Widget Configuration

Add this to your Homepage `services.yaml`:

```yaml
- MeTube:
    icon: metube.png
    href: http://your-server:8081
    description: Video Downloader
    widget:
        type: customapi
        url: http://your-server:8082/stats
        refreshInterval: 300000  # 5 minutes
        mappings:
            - field: active_downloads
              label: Active
              format: number
            - field: completed_downloads
              label: Completed
              format: number
            - field: pending_downloads
              label: Pending
              format: number
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
export METUBE_URL=http://localhost:8081
python app.py
```

## Notes

- Requires MeTube to be accessible via HTTP
- The API is read-only and does not modify any MeTube settings
- Statistics are cached for the configured timeout period
- MeTube must have its API enabled (default configuration)

## License

MIT
