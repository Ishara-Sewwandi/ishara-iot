# Configure Let's Encrypt on Your VPS Traefik

## Problem
Your Traefik is using a self-signed certificate ("TRAEFIK DEFAULT CERT") instead of Let's Encrypt.
This causes the Raspberry Pi to reject the connection with `NotValidForName` error.

## Solution
Add Let's Encrypt configuration to your VPS Traefik setup.

### On Your VPS at `/home/koi/Documents/GitHub/koi-fish-friend`

#### Option 1: docker-compose.yml Configuration

Add these labels to your Traefik service:

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      # Let's Encrypt configuration
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=your-email@example.com"  # CHANGE THIS
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"  # Persistent certificate storage
    restart: unless-stopped

  livekit:
    image: livekit/livekit-server:latest
    command: --config /etc/livekit.yaml
    volumes:
      - ./livekit.yaml:/etc/livekit.yaml
    labels:
      - "traefik.enable=true"
      # HTTP -> HTTPS redirect
      - "traefik.http.routers.livekit-http.rule=Host(\`livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me\`)"
      - "traefik.http.routers.livekit-http.entrypoints=web"
      - "traefik.http.routers.livekit-http.middlewares=redirect-to-https"
      - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"
      # HTTPS configuration with Let's Encrypt
      - "traefik.http.routers.livekit.rule=Host(\`livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me\`)"
      - "traefik.http.routers.livekit.entrypoints=websecure"
      - "traefik.http.routers.livekit.tls=true"
      - "traefik.http.routers.livekit.tls.certresolver=letsencrypt"  # This triggers Let's Encrypt
      - "traefik.http.services.livekit.loadbalancer.server.port=7880"
    restart: unless-stopped
```

#### Important Steps:

1. **Update email**: Change `your-email@example.com` to your real email for Let's Encrypt notifications

2. **Create letsencrypt directory** on VPS:
```bash
cd /home/koi/Documents/GitHub/koi-fish-friend
mkdir -p letsencrypt
chmod 600 letsencrypt
```

3. **Restart Traefik** on VPS:
```bash
docker-compose down
docker-compose up -d
```

4. **Monitor logs** to see Let's Encrypt certificate being issued:
```bash
docker-compose logs -f traefik
```

Look for messages like:
- "Obtaining certificate from Let's Encrypt"
- "Certificate obtained successfully"

5. **Verify certificate** (from anywhere):
```bash
echo | openssl s_client -connect livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me:443 -servername livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me 2>/dev/null | openssl x509 -text | grep "Issuer:"
```

You should see: `Issuer: C=US, O=Let's Encrypt, CN=...`

### After Let's Encrypt is Working

On your **Raspberry Pi**, remove the self-signed certificate and test:

```bash
sudo rm /usr/local/share/ca-certificates/traefik-default.crt
sudo update-ca-certificates --fresh
sudo systemctl restart livekit-publisher.service
sudo journalctl -u livekit-publisher.service -f
```

You should see: `✅ Connected to LiveKit room: boat-navigation`

## Alternative: Use IP Address Directly

If Let's Encrypt fails, you can use your VPS IP directly with `ws://` (unencrypted):

1. Update `.env` on Raspberry Pi:
```bash
LIVEKIT_URL=ws://187.77.189.5:7880
```

2. Configure LiveKit to accept unencrypted connections (in `livekit.yaml` on VPS):
```yaml
port: 7880
bind_addresses:
  - 0.0.0.0
```

**⚠️ Warning**: This sends video unencrypted over the internet. Only use for testing.

## Troubleshooting

### Let's Encrypt Rate Limits
If you hit rate limits, use staging environment for testing:
```yaml
- "--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
```

### Port 80 Must Be Open
Let's Encrypt TLS challenge requires port 80 to be accessible from the internet.
Check your VPS firewall:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Check Traefik Dashboard
Access at `http://187.77.189.5:8080` to see:
- Routers configuration
- Certificates status
- Services health
