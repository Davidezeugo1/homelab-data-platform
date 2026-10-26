# Homelab Data Platform Architecture

## 1. Purpose

The Homelab Data Platform is a self-hosted environment for learning,
testing, and documenting practical data engineering workflows.

The platform is designed to support data ingestion, distributed
processing, workflow orchestration, object storage, relational
databases, monitoring, and eventually end-to-end analytics projects.

## 2. Architecture Overview

The environment is organized into five layers.

### Infrastructure and Virtualization

- **Proxmox VE:** Hosts and manages the virtual machines and containers
  that run the platform's services.
- **Proxmox Backup Server (PBS):** Provides a dedicated environment for
  backing up supported Proxmox workloads.
- **Proxmox Datacenter Manager (PDM):** Provides a centralized view
  for managing connected infrastructure.

### Networking and Service Access

- **BIND DNS:** Resolves internal service names.
- **Nginx:** Acts as a reverse proxy for supported web applications.
- **Internal DNS names:** Provide convenient access to services without
  requiring users to remember each application's address and port.

These services are intended for private homelab access. Public
documentation does not include internal IP addresses or credentials.

### Data Platform

- **Apache Kafka:** Provides distributed event streaming.
- **Apache Spark:** Provides distributed data processing.
- **Apache Airflow:** Orchestrates data workflows.
- **MinIO:** Provides S3-compatible object storage for data lake
  experiments.
- **PostgreSQL:** Provides relational storage for supported workloads.
- **MariaDB:** Provides an additional relational database environment.
- **Kafka UI:** Provides a web interface for inspecting the Kafka cluster.
- **pgAdmin and phpMyAdmin:** Provide web-based database administration.

### Monitoring and Operations

- **Uptime Kuma:** Checks the availability of selected infrastructure
  endpoints and application services.
- **Proxmox Backup Server:** Supports backup and recovery operations.
- **Operational documentation:** Records setup decisions, validation
  steps, and troubleshooting procedures.

Availability checks are useful signals, but they do not by themselves
prove that a service is processing data correctly.

### Analytics and Portfolio Projects

- **Weather ETL:** Planned first end-to-end data engineering project.
- **Apache Superset:** Planned analytics and dashboard layer.
- **Streaming pipeline:** Planned follow-up project using Kafka.

These project components are planned and should not be interpreted as
completed pipelines.

## 3. Deployed Services

The following services have been deployed in the homelab:

| Capability | Technology | Current role |
|---|---|---|
| Virtualization | Proxmox VE | Runs the platform workloads |
| Backup | Proxmox Backup Server | Dedicated backup environment |
| Infrastructure management | Proxmox Datacenter Manager | Centralized infrastructure view |
| Internal DNS | BIND | Resolves internal service names |
| Reverse proxy | Nginx | Routes requests to web applications |
| Event streaming | Apache Kafka | KRaft-based Kafka cluster |
| Distributed processing | Apache Spark | Master and worker deployment |
| Workflow orchestration | Apache Airflow | Workflow scheduling and execution |
| Object storage | MinIO | S3-compatible storage |
| Relational storage | PostgreSQL, MariaDB | Database services |
| Availability monitoring | Uptime Kuma | Monitors selected endpoints and services |

## 4. Planned Weather ETL Data Flow

The first portfolio pipeline is planned to follow this flow:

1. **Ingest:** Retrieve weather data from a suitable public data source.
2. **Store raw data:** Preserve the original response in object storage.
3. **Transform:** Use Python and SQL, adding Spark where it provides
   meaningful value.
4. **Validate:** Check required fields, data types, missing values,
   duplicate records, and reasonable ranges.
5. **Load:** Store cleaned, structured data in a relational database
   or an appropriate analytics-ready storage layer.
6. **Orchestrate:** Use Airflow to schedule and coordinate the workflow.
7. **Visualize:** Use Apache Superset to build dashboards from the
   resulting dataset.
8. **Monitor:** Add operational checks and useful failure information.

This is the intended design, not a claim that the complete pipeline
has already been implemented.

## 5. Design Principles

- **Incremental delivery:** Build and validate one capability at a time.
- **Reproducibility:** Document setup and execution steps.
- **Data quality:** Validate data instead of assuming ingestion succeeded.
- **Observability:** Distinguish service availability from pipeline health.
- **Security:** Keep secrets and sensitive infrastructure details out
  of the public repository.
- **Practical trade-offs:** Use distributed tools when they solve a
  real problem, rather than adding complexity without a clear purpose.

## 6. Current Status and Next Steps

### Completed foundation

- Self-hosted virtualization and backup environments.
- Internal DNS and reverse-proxy access for supported services.
- Kafka KRaft cluster and user interface.
- Spark master and worker deployment.
- Airflow deployment.
- MinIO and relational database services.
- Initial infrastructure and application availability monitoring.
- Public GitHub repository.

### Planned work

1. Implement the weather ingestion and storage steps.
2. Add transformations and automated data-quality checks.
3. Orchestrate the workflow with Airflow.
4. Add repeatable execution instructions and tests.
5. Build analytics and dashboards.
6. Document pipeline monitoring, failures, and recovery.

The project status will be updated as each capability is implemented
and validated.
