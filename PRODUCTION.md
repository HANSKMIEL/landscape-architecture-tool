# Production Deployment Guide

This guide covers deploying the Landscape Architecture Management System in a production environment.

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd landscape-architecture-tool
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   export SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Deploy with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

### Manual Deployment

Run the automated deployment script:
```bash
chmod +x deploy-production.sh
./deploy-production.sh
```

## Architecture

The production setup includes:

- **Gunicorn WSGI Server**: Production-grade Python application server
- **Nginx Reverse Proxy**: Load balancing, SSL termination, static file serving
- **PostgreSQL Database**: Production database with proper user management
- **Redis**: Caching and rate limiting backend
- **SSL/TLS**: HTTPS encryption with security headers

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `DATABASE_URL` | Database connection string | SQLite (dev) / PostgreSQL (prod) |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5174` |
| `LOG_LEVEL` | Logging level | `WARNING` |

### Security Configuration

The application includes several security features:

1. **Rate Limiting**: API endpoints are rate-limited to prevent abuse
2. **Security Headers**: XSS protection, content type sniffing prevention
3. **CORS**: Configurable cross-origin resource sharing
4. **Session Security**: Secure session cookies with proper flags
5. **HTTPS Enforcement**: SSL/TLS encryption for data in transit

### Database Configuration

**Development (SQLite):**
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///landscape_architecture.db'
```

**Production (PostgreSQL):**
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/landscape_architecture_prod'
```

## SSL/TLS Setup

### Using Let's Encrypt (Recommended)

1. **Install Certbot:**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Obtain certificates:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Auto-renewal:**
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Manual SSL Certificate

Update `nginx.conf` with your certificate paths:
```nginx
ssl_certificate /path/to/your/certificate.crt;
ssl_certificate_key /path/to/your/private.key;
```

## Monitoring and Logging

### Application Logs

Logs are written to stdout/stderr and can be viewed with:
```bash
# Systemd service logs
sudo journalctl -u landscape-architecture -f

# Docker logs
docker-compose logs -f backend
```

### Health Checks

The application provides a health check endpoint:
```bash
curl https://your-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00.000000",
  "version": "2.0.0",
  "database_status": "connected",
  "environment": "production"
}
```

### Nginx Status

Monitor Nginx status:
```bash
sudo systemctl status nginx
sudo nginx -t  # Test configuration
```

## Performance Optimization

### Gunicorn Configuration

The `gunicorn.conf.py` file includes optimized settings:
- Worker processes: `CPU_COUNT * 2 + 1`
- Worker class: `sync` (suitable for most workloads)
- Timeout: `30` seconds
- Max requests per worker: `1000`

### Database Optimization

1. **Connection Pooling**: SQLAlchemy handles connection pooling
2. **Query Optimization**: Use indexes for frequently queried fields
3. **Database Maintenance**: Regular VACUUM and ANALYZE operations

### Caching

Redis is configured for:
- Rate limiting storage
- Session storage (if configured)
- Application caching (future enhancement)

## Backup Strategy

### Database Backup

**PostgreSQL:**
```bash
# Create backup
pg_dump landscape_architecture_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql landscape_architecture_prod < backup_file.sql
```

**SQLite (development):**
```bash
# Create backup
cp landscape_architecture.db backup_$(date +%Y%m%d_%H%M%S).db
```

### Application Files

Backup important files:
- Configuration files
- SSL certificates
- Upload directories (if any)
- Log files

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use multiple Gunicorn instances behind Nginx
2. **Database**: Consider read replicas for heavy read workloads
3. **Redis Cluster**: Scale Redis for high availability

### Vertical Scaling

1. **Increase Workers**: Adjust `workers` in `gunicorn.conf.py`
2. **Database Resources**: Increase PostgreSQL memory and CPU
3. **System Resources**: Monitor and increase server resources

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**: Check if Gunicorn is running
   ```bash
   sudo systemctl status landscape-architecture
   ```

2. **Database Connection Errors**: Verify PostgreSQL is running and accessible
   ```bash
   sudo systemctl status postgresql
   psql -h localhost -U landscape_user -d landscape_architecture_prod
   ```

3. **SSL Certificate Issues**: Check certificate validity
   ```bash
   sudo certbot certificates
   openssl x509 -in /path/to/cert.pem -text -noout
   ```

### Log Analysis

Check application logs for errors:
```bash
# Application logs
sudo journalctl -u landscape-architecture --since "1 hour ago"

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Security Hardening

### System Level

1. **Firewall Configuration:**
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

2. **System Updates:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

3. **User Permissions**: Run application as non-root user

### Application Level

1. **Secret Key**: Use strong, unique secret key in production
2. **Database Credentials**: Use strong passwords and limited privileges
3. **CORS**: Restrict origins to only necessary domains
4. **Rate Limiting**: Adjust limits based on expected traffic

## Maintenance

### Regular Tasks

1. **System Updates**: Monthly OS and package updates
2. **Certificate Renewal**: Automated with Let's Encrypt
3. **Database Maintenance**: Weekly VACUUM and ANALYZE
4. **Log Rotation**: Configure logrotate for application logs
5. **Backup Verification**: Test restore procedures monthly

### Monitoring

Set up monitoring for:
- Application uptime and response time
- Database performance
- Server resources (CPU, memory, disk)
- SSL certificate expiration
- Error rates and logs

## Support

For production support:
- Check logs first (application and system)
- Verify all services are running
- Test connectivity to external dependencies
- Review recent changes or deployments