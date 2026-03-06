# Deployment Guide

## LexiScan Auto - Production Deployment

This guide covers deploying LexiScan Auto in various environments.

---

## Prerequisites

- Docker 20.10+ and Docker Compose 1.29+
- OR Python 3.10+ with pip
- 4GB+ RAM
- 10GB+ disk space

---

## Option 1: Docker Deployment (Recommended)

### Quick Start

```bash
# Clone repository
cd d:\Projects\lexiscan-auto

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f lexiscan-api

# Verify health
curl http://localhost:8000/health
```

### Configuration

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
  - ENVIRONMENT=production   # development, production
```

### Scaling

```bash
# Scale to multiple instances
docker-compose up -d --scale lexiscan-api=3

# Use nginx for load balancing
```

### Monitoring

```bash
# View logs
docker-compose logs -f

# Check resource usage
docker stats lexiscan-auto

# Inspect container
docker exec -it lexiscan-auto bash
```

### Stopping

```bash
# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove volumes (caution: deletes data)
docker-compose down -v
```

---

## Option 2: Manual Deployment

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Download Spacy model
python -m spacy download en_core_web_sm
```

### 2. Install Tesseract OCR

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

**Mac:**
```bash
brew install tesseract poppler
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit configuration
nano .env
```

### 4. Start API Server

```bash
# Development mode (with auto-reload)
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode (with workers)
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Option 3: Production Deployment with Gunicorn

### Install Gunicorn

```bash
pip install gunicorn
```

### Start with Gunicorn

```bash
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### Systemd Service (Linux)

Create `/etc/systemd/system/lexiscan.service`:

```ini
[Unit]
Description=LexiScan Auto API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/lexiscan-auto
Environment="PATH=/opt/lexiscan-auto/venv/bin"
ExecStart=/opt/lexiscan-auto/venv/bin/gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lexiscan
sudo systemctl start lexiscan
sudo systemctl status lexiscan
```

---

## Nginx Reverse Proxy

### Install Nginx

```bash
sudo apt-get install nginx
```

### Configure

Create `/etc/nginx/sites-available/lexiscan`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/lexiscan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `TESSERACT_PATH` | Tesseract executable path | Auto-detect |
| `MAX_UPLOAD_SIZE` | Max file size (bytes) | `10485760` (10MB) |

---

## Health Checks

### API Health

```bash
curl http://localhost:8000/health
```

### Docker Health

```bash
docker inspect --format='{{.State.Health.Status}}' lexiscan-auto
```

---

## Monitoring & Logging

### Log Files

- API logs: `logs/api.log`
- Access logs: `logs/access.log`
- Error logs: `logs/error.log`

### Log Rotation

Create `/etc/logrotate.d/lexiscan`:

```
/opt/lexiscan-auto/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload lexiscan
    endscript
}
```

### Monitoring Tools

Consider integrating:
- **Prometheus** for metrics
- **Grafana** for dashboards
- **Sentry** for error tracking
- **ELK Stack** for log aggregation

---

## Performance Tuning

### API Workers

Adjust based on CPU cores:

```bash
# Formula: (2 x CPU cores) + 1
workers = (2 * 4) + 1 = 9
```

### Memory

- Baseline model: ~500MB per worker
- Spacy model: ~1GB per worker
- Bi-LSTM model: ~2GB per worker

### Caching

Consider adding Redis for:
- Frequently accessed entities
- Model predictions
- Validation results

---

## Security Best Practices

1. **API Authentication**
   - Add JWT tokens
   - Implement API keys
   - Rate limiting

2. **File Upload Validation**
   - Virus scanning
   - File type verification
   - Size limits

3. **Network Security**
   - Use HTTPS only
   - Firewall configuration
   - VPN for internal access

4. **Data Privacy**
   - Encrypt sensitive data
   - Secure log storage
   - GDPR compliance

---

## Backup & Recovery

### Data Backup

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/ models/ logs/

# Upload to cloud storage
aws s3 cp backup-*.tar.gz s3://your-bucket/backups/
```

### Database Backup (if added)

```bash
# PostgreSQL example
pg_dump lexiscan_db > backup.sql
```

---

## Troubleshooting

### API Not Starting

```bash
# Check logs
docker-compose logs lexiscan-api

# Check port availability
netstat -tulpn | grep 8000

# Verify dependencies
pip list | grep fastapi
```

### OCR Errors

```bash
# Verify Tesseract installation
tesseract --version

# Check Tesseract path
which tesseract

# Test OCR
tesseract test.png output
```

### Memory Issues

```bash
# Check memory usage
free -h

# Reduce workers
# Edit docker-compose.yml or gunicorn config
```

### Slow Performance

- Enable GPU for Bi-LSTM
- Use baseline model for speed
- Implement caching
- Scale horizontally

---

## Updating

### Docker

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Manual

```bash
# Pull changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart lexiscan
```

---

## Support

For deployment issues:
1. Check logs in `logs/` directory
2. Review error messages
3. Consult API documentation
4. Check system resources

---

## Production Checklist

- [ ] SSL/TLS configured
- [ ] Authentication enabled
- [ ] Rate limiting implemented
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Backup strategy in place
- [ ] Health checks working
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
