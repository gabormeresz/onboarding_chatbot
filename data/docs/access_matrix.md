# System Access Matrix

This document defines the default and conditional system access rights for employees based on their role within the organization. It aims to ensure **security, least-privilege access**, and **auditability**, while enabling employees to perform their duties effectively.

---

## Default Access by Role

### Software Engineer

**Default Access**

- Corporate Email: ✅ Yes
- Microsoft Teams: ✅ Yes
- Company Intranet / Wiki (e.g. Confluence, SharePoint): ✅ Yes
- Single Sign-On (SSO): ✅ Yes

**Conditional / On-Request Access**

- Git Repository (GitHub / GitLab / Azure DevOps): 🔒 Upon request
- Jira / Issue Tracking System: 🔒 Upon request
- CI/CD Pipelines: 🔒 Upon request
- Cloud Development Environments (Dev / Test): 🔒 Upon request

**Restricted Access**

- Production Systems: ❌ No
- Customer Data (PII): ❌ No
- Financial Systems: ❌ No

---

### Data Scientist

**Default Access**

- Corporate Email: ✅ Yes
- Microsoft Teams: ✅ Yes
- Company Intranet / Wiki: ✅ Yes
- Jira / Issue Tracking System: ✅ Yes

**Conditional / On-Request Access**

- Git Repository (read/write based on project): 🔒 Upon request
- Analytics Platform (Databricks, BigQuery, Snowflake, etc.): 🔒 Upon request
- Experiment Tracking (MLflow, Weights & Biases): 🔒 Upon request
- Non-production Data Sources (anonymized): 🔒 Upon request

**Restricted Access**

- Production Systems: ❌ No
- Raw Customer PII: ❌ No
- Billing / Finance Systems: ❌ No

---

### Manager

**Default Access**

- Corporate Email: ✅ Yes
- Microsoft Teams: ✅ Yes
- Jira / Project Management Tools: ✅ Yes
- HR Reporting Tools (read-only): ✅ Yes
- Company Intranet / Wiki: ✅ Yes

**Conditional / On-Request Access**

- Team Performance Dashboards: 🔒 Upon request
- Budget / Cost Reporting Tools: 🔒 Upon request
- Read-only Access to Analytics Platforms: 🔒 Upon request

**Restricted Access**

- Source Code Repositories (write): ❌ No
- Production Systems: ❌ No

---

### IT Administrator

**Default Access**

- Corporate Email: ✅ Yes
- Microsoft Teams: ✅ Yes
- IT Support Portal: ✅ Yes
- Identity & Access Management (IAM): ✅ Yes

**Elevated Access**

- Git Repository Administration: ✅ Yes
- Jira Administration: ✅ Yes
- Production Systems (limited scope): ⚠️ Yes, role-based
- Cloud Infrastructure Management: ⚠️ Yes, role-based

> ⚠️ Elevated access is logged, monitored, and subject to periodic review.

---

## Access Request Rules

- All **non-default access** must be requested via the **IT Support Portal**.
- Requests must include:
  - Business justification
  - Project or system name
  - Requested access level (read / write / admin)
  - Access duration (temporary or permanent)

---

## Approval Requirements

Manager approval is required for:

- Git repository access
- Jira access (non-default roles)
- Analytics platforms
- Cloud development environments

Additional approval is required for:

- Cross-team or cross-department access
- Temporary elevated permissions

---

## Production System Access Policy

Access to **production systems** is strictly controlled and granted only when all conditions are met:

- Valid business justification
- Completion of mandatory security training
- Approval from:
  - Direct Manager
  - IT Security Team
- Time-bound access (default: 30 days)
- Mandatory logging and monitoring enabled

---

## Access Review & Revocation

- Access rights are reviewed:

  - Quarterly for elevated roles
  - Upon role change or project completion
  - Upon employee offboarding

- IT reserves the right to revoke access immediately in case of:
  - Security incidents
  - Policy violations
  - Inactive usage

---

## Principles

- **Least Privilege**: Users receive only the access necessary to perform their role
- **Separation of Duties**: No single role should have end-to-end control of critical systems
- **Auditability**: All access changes are logged and reviewable

---

_Last updated: 2025-12-16_  
_Owner: IT Security & Compliance Team_
