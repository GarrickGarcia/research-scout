# Amazon S3 Files — Mounting S3 Buckets as Native File Systems

**Date:** 2026-04-07
**Source:** https://www.allthingsdistributed.com/2026/04/s3-files-and-the-changing-face-of-s3.html
**Verdict:** watch
**Category:** infrastructure
**Relevance Score:** 3

## What is it?

Amazon S3 Files is a new AWS feature that integrates Amazon Elastic File System (EFS) into S3, allowing any existing S3 bucket or prefix to be mounted and accessed as a standard NFS network-attached file system — without any data migration or code changes. Applications mount the bucket like a local directory; reads, writes, and deletes work through standard POSIX file operations, and changes sync back to S3 automatically (roughly every 60 seconds as a "stage and commit" cycle, borrowing the metaphor from Git).

Under the hood, S3 Files maintains a synchronized EFS namespace that mirrors S3 object metadata. Files under 128 KB are eagerly pulled into the file layer; larger files are lazy-loaded from S3 on first access. For high-throughput sequential reads, a "read bypass" mode issues parallel GET requests directly to S3, achieving ~3 GB/s per client. The system supports NFS v4.1 and v4.2, POSIX permissions, file locking, read-after-write consistency, and up to 25,000 concurrent connections across EC2, ECS, EKS, Lambda, and Fargate. S3 remains authoritative: if file-side and object-side writes conflict, the object version wins and the file-side content moves to a `lost+found` directory with a CloudWatch metric.

S3 Files is the third leg of a strategic pivot AWS is making — alongside S3 Tables (Apache Iceberg-backed structured data) and S3 Vectors (native vector index storage) — to transform S3 from a raw object store into a multi-primitive durable data platform where the same data can be reached via objects, tables, vectors, or files depending on what the workload demands.

## Why it matters (or doesn't)

The architectural insight here is genuinely interesting: rather than collapsing file and object semantics into a lowest-common-denominator hybrid (which AWS tried and abandoned after months of "passionate and occasionally desolate discussions"), the team built an explicit, honest sync boundary between the two worlds. That "explicit boundary as a feature" design philosophy is worth internalizing for any storage-adjacent pipeline design work — including the kind of multi-stage data flows that show up in AI agent workflows and ETL pipelines.

For Garrick's actual stack, however, the direct applicability is limited. Abonmarche runs on Azure — PostgreSQL on Azure (CostEstDB), Azure Functions, SharePoint, Teams, Power Automate — with no described AWS footprint. S3 Files is entirely AWS-native and offers no cross-cloud capability. The closest Azure analog is Azure Data Lake Storage Gen2, which already supports hierarchical namespace and NFS 3.0 mount access for similar "file + object on the same data" use cases. The pattern S3 Files introduces isn't new to Azure customers — it's new to S3 customers who previously had no native answer beyond third-party FUSE hacks.

The agentic AI angle is conceptually relevant: the article makes a strong case that AI coding agents naturally reach for filesystem APIs (grep, cat, sed, etc.) rather than object storage SDKs, and that removing the copy-to-local-disk step meaningfully speeds up agent iteration loops. If Garrick ever evaluates AWS as a runtime for Claude-based agents operating over large datasets, this would be a first-class consideration.

## Technical details

- **Protocols:** NFS v4.1 and v4.2; Linux/Mac mount compatible; EFS does **not** support Windows instances natively
- **Latency:** ~1ms for actively cached data in the EFS layer; large sequential reads bypass NFS and go directly to S3
- **Sync cadence:** File → S3 commits approximately every 60 seconds (batched PUTs); S3 → file view propagates "typically within seconds, sometimes up to a minute"
- **Scale:** Up to 25,000 concurrent connections; aggregate read throughput in the terabits-per-second range across clients
- **Conflict resolution:** S3 is always authoritative; file-side conflicts land in `lost+found` with CloudWatch visibility
- **Pricing:** You pay normal S3 storage rates for the underlying data + EFS charges for the hot file-layer slice + S3 request costs for sync operations. Community commentary notes EFS costs can escalate quickly for non-trivial workloads — this is a "light-to-moderate" access pattern feature, not a cost-efficient high-churn replacement for dedicated EFS
- **Known limitations at launch:** Directory renames are expensive (requires copying + deleting every object under a prefix); no explicit commit control (60-second window is fixed); object keys that are invalid POSIX filenames won't appear in the filesystem view; Glacier tiers require an S3 API restore first
- **Maturity:** Generally available as of April 7, 2026; ~9-month customer beta preceded GA

## Recommendation

No action needed now. Abonmarche's stack is Azure-native and S3 Files is AWS-only with no cross-cloud bridge. The feature doesn't change the calculus for CostEstDB, ArcGIS workflows, or the Claude/Power Automate integrations in flight.

Watch for two things over the next few months:

1. **Azure response:** Microsoft may accelerate ADLS Gen2 improvements or announce a similar "object + file unified view" feature for Azure Blob Storage that would be directly applicable to Abonmarche's environment.
2. **Agent data-access patterns:** The article's core argument — that AI agents work best with filesystem semantics and that removing the copy-to-local step is high-leverage — is worth keeping in mind when architecting any cloud-resident agentic workflow. If a future Claude agent needs to chew through large municipal datasets (LiDAR, imagery, crash report archives) stored in cloud object storage, the access-pattern design lesson from S3 Files applies regardless of which cloud it runs on.
