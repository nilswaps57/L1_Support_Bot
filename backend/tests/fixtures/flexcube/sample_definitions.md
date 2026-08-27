---
document_title: FLEXCUBE Definitions User Manual
release_identifier: SYNTH-FC-REL14-QA
fixture_kind: synthetic
source_pattern: Oracle FLEXCUBE definitions manual
---

<!-- source-page: 1 -->
# FLEXCUBE Definitions User Manual

**Release:** SYNTH-FC-REL14-QA  
**Purpose:** Synthetic training material for structure-aware ingestion and grounded support search.

This document uses compact definitions and operational steps. Values are intentionally synthetic and do not reproduce the source manual.

<!-- source-page: 2 -->
## BA431 - Customer Profile Definition

Task Code: BA431

Screen Name: Customer Profile Definition

Menu Path: Main Menu > Customer Management > Customer Profile

Prerequisites: ST001, ST002

Modes: New, Inquiry, Modify

Fields: Customer ID, Customer Name, Customer Type, Short Name

### Field descriptions

| Field | Description | Required | Example |
| --- | --- | --- | --- |
| Customer ID | Unique identifier assigned to the customer profile. | Yes | CUST-1042 |
| Customer Name | Full name displayed in customer searches and notices. | Yes | Northwind Retail |
| Customer Type | Classifies the profile for servicing rules. | Yes | Corporate |
| Short Name | Compact label used in lists and lookup results. | No | NWR |

### Procedure: Create a customer profile

1. Step 1: Open Customer Profile Definition from the stated menu path.
2. Step 2: Choose New mode and enter the required customer fields.
3. Step 3: Save the profile and confirm the generated Customer ID.

> **Note:** A profile cannot be saved until Customer ID, Customer Name, and Customer Type are present.

Related screens: Customer Search, Customer Address

<!-- source-page: 3 -->
## BA435 - Account Maintenance Definition

Task Code: BA435

Screen Name: Account Maintenance Definition

Menu Path: Main Menu > Account Services > Account Maintenance

Prerequisites: BA431

Modes: Inquiry, Modify, Authorize

Fields: Account Number, Customer ID, Product Code, Account Status

### Field descriptions

| Field | Description | Required | Example |
| --- | --- | --- | --- |
| Account Number | Identifier of the account selected for maintenance. | Yes | AC-77821 |
| Customer ID | Links the account to its owning customer profile. | Yes | CUST-1042 |
| Product Code | Identifies the account product and its rules. | Yes | SAV-01 |
| Account Status | Shows whether the account can accept servicing changes. | Yes | Active |

> **Warning:** Modify mode changes take effect only after an authorized user approves the record.

Related screens: Customer Profile Definition, Account Authorization

<!-- source-page: 4 -->
## BA436 - Service Request Definition

Task Code: BA436

Screen Name: Service Request Definition

Menu Path: Main Menu > Servicing > Service Request

Prerequisites: BA435

Modes: Inquiry, Create, Close

Fields: Request Number, Account Number, Request Type, Request Status

### Field descriptions

| Field | Description | Required | Example |
| --- | --- | --- | --- |
| Request Number | Reference generated for the service request. | Yes | SR-22019 |
| Account Number | Account for which the request is submitted. | Yes | AC-77821 |
| Request Type | Classifies the customer service action. | Yes | Statement Copy |
| Request Status | Tracks the request through completion. | Yes | Open |

> **Note:** Close mode is available only when the request has no pending approval.

Related screens: Account Maintenance Definition, Request History

<!-- source-page: 5 -->
## Retrieval landmarks

Use the task code, screen name, menu path, and source-page metadata together when producing a citation. A response about account changes should cite BA435, while a response about service requests should cite BA436.
