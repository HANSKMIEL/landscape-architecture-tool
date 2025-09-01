#!/usr/bin/env python3
"""
Gunicorn configuration for production deployment
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after serving this many requests
max_requests = 1000
max_requests_jitter = 50

# Preload app for better memory usage
preload_app = True

# Process naming
proc_name = "landscape-architecture-api"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if certificates are provided)
keyfile = os.environ.get("SSL_KEYFILE")
certfile = os.environ.get("SSL_CERTFILE")


def when_ready(server):
    """Called when the server is ready to serve requests"""
    server.log.info("Landscape Architecture API server is ready to serve requests")


def worker_exit(server, worker):
    """Called when a worker exits"""
    server.log.info(f"Worker {worker.pid} exited")


def pre_fork(server, worker):
    """Called before each worker is forked"""


def post_fork(server, worker):
    """Called after each worker is forked"""
    server.log.info(f"Worker {worker.pid} spawned")
