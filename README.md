# Homelab Data Platform

## Overview

This repository documents my self-hosted learning environment
for developing practical data engineering skills.

The project focuses on infrastructure, data ingestion,
storage, transformation, orchestration, monitoring,
data quality, and analytics.

### Technology Stack

- Infrastructure: Proxmox VE and Proxmox Backup Server
- Programming: Python and SQL
- Streaming: Apache Kafka
- Processing: Apache Spark
- Orchestration: Apache Airflow
- Object Storage: MinIO (S3-compatible)
- Databases: PostgreSQL and MariaDB
- Network: Bind3 and Nginx
- Monitoring: Uptime Kuma and Proxmox datacenter manager
- Version Control: Git and GitHub
- Planned Analytics: Apache Superset

### Repository Structure

- `docs/` — Architecture, setup, operations, and troubleshooting
- `diagrams/` — Sanitized architecture and data-flow diagrams
- `infrastructure/` — Safe, reusable configuration examples
- `scripts/` — Health checks and operational utilities
- `projects/weather-etl/` — First end-to-end ETL project

### Planned Projects

1. Weather ETL pipeline
2. Pipeline orchestration and data-quality checks
3. Pipeline observability dashboard
4. Streaming data engineering project

### Security

This public repository intentionally excludes credentials,
private keys, tokens, and sensitive infrastructure details.
Configuration examples will be sanitized before publication.

### Status

Infrastructure foundation fully established.
Weather ETL (first project) planned next
analytics dashboard planned after first pipeline.
