This is the commands to run cloudflare

cloudflared tunnel login
cloudflared tunnel create fixture-api
cloudflared tunnel route dns fixture-api api.yourdomain.com
cloudflared tunnel run --url http://localhost:8000 fixture-api

or we can run on docker:

services:
  api:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped

  tunnel:
    image: cloudflare/cloudflared:latest
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=<your-tunnel-token>
    restart: unless-stopped