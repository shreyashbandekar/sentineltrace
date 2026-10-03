# 🛡️ SentinelTrace

### Windows Endpoint State Monitoring & Integrity Auditing

SentinelTrace is a defensive Windows endpoint auditing tool designed to establish a trusted system baseline, capture endpoint state, detect changes, investigate those changes, and generate structured audit reports.

It was built as a cybersecurity learning and portfolio project focused on **endpoint visibility, system integrity, change detection, and security auditing**.

---

## Overview

When a Windows system is handed over for maintenance, troubleshooting, upgrades, or other service work, it can be useful to understand what changed between the **before-service** and **after-service** states.

SentinelTrace provides a structured way to:

1. Establish a trusted baseline.
2. Capture the current endpoint state.
3. Compare later system states against the baseline.
4. Identify added, removed, and modified items.
5. Investigate detected changes.
6. Verify baseline integrity.
7. Generate JSON and human-readable audit reports.

```text
                 ┌──────────────────────┐
                 │     Windows Host     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   System Collector   │
                 └──────────┬───────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
     Accounts          Services          Software
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
       Network          Security           Startup
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
                   Scheduled Tasks
                            │
                            ▼
                        Drivers
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Baseline / Snapshot  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Change Detection   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Investigation Engine │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     Audit Reports    │
                 └──────────────────────┘
```

---

## Current Features

SentinelTrace currently collects and audits the following Windows endpoint information:

### System Information

- Timestamp
- Computer name
- Current username
- Operating system
- OS release
- OS version
- System architecture
- Python version

### Local Accounts

- Local users
- Enabled/disabled state
- Local administrators

### Windows Services

- Service name
- Display name
- Current state
- Start mode
- Service account
- Executable path

### Installed Software

Registry-based software inventory from:

- HKLM 64-bit
- HKLM 32-bit
- HKCU

### Network Configuration

- Network adapters
- IP configuration
- TCP connections
- Process IDs associated with connections

### Security Configuration

- Microsoft Defender status
- Windows Firewall status
- UAC configuration
- Remote Desktop configuration
- WinRM configuration
- Remote Assistance configuration

### Startup Configuration

- Registry startup entries
- Startup folders
- Boot/logon scheduled tasks

### Scheduled Tasks

- Task name
- Task path
- State
- Author
- Description
- Principal
- Run level
- Logon type
- Actions
- Triggers
- Runtime information

Volatile runtime values such as last-run and next-run timestamps are handled separately during comparison.

### Drivers

- Driver inventory
- Driver name
- Display name
- State
- Start mode
- Start account
- Driver path

---

# Baseline & Snapshot System

## Baseline

The baseline represents the trusted reference state of the Windows endpoint.

A baseline is created using:

```powershell
python main.py baseline
```

The baseline is stored under:

```text
baseline/
├── baseline.json
└── baseline.sha256
```

The SHA-256 hash allows SentinelTrace to verify that the baseline has not been modified unexpectedly.

### Baseline Principle

The baseline should be created when the system is considered to be in a trusted state.

Once created, it should not be manually modified.

---

## Snapshot

A snapshot represents a later captured state of the endpoint.

Snapshots allow SentinelTrace to preserve endpoint state at different points in time.

Snapshots are stored under:

```text
snapshots/
```

The snapshot data can later be compared with the trusted baseline to identify changes.

---

# Change Detection

SentinelTrace compares endpoint state across multiple categories.

The comparison engine identifies:

- Added items
- Removed items
- Modified items
- Unchanged items

The comparison covers areas including:

- Users
- Administrators
- Services
- Installed software
- Network configuration
- Security configuration
- Startup entries
- Scheduled tasks
- Drivers

Example:

```text
Added:      2
Removed:    2
Modified:   14
Unchanged:  1132
```

The exact results depend on the state of the Windows system at the time of comparison.

### Volatile Data Handling

Some Windows values naturally change during normal operation.

For example, scheduled tasks can have changing:

- Last run time
- Next run time
- Last task result

These runtime values are handled separately so that normal task execution does not automatically appear as a structural modification.

---

# Investigation Engine

The investigation engine converts detected changes into structured findings.

Each finding contains information such as:

- Timestamp
- Section
- Change type
- Item identifier
- Change details

Example:

```text
Finding
├── Timestamp
├── Section
├── Change Type
├── Item ID
└── Details
```

This makes the comparison output easier to review and understand.

SentinelTrace does **not** automatically classify every detected change as malicious.

A change may be:

- Expected
- Caused by Windows updates
- Caused by software updates
- Caused by normal system activity
- Caused by maintenance
- Unexpected and requiring investigation

The tool records the observable change so that it can be investigated in context.

---

# Baseline Integrity

SentinelTrace uses SHA-256 hashing to protect the integrity of the trusted baseline.

The baseline hash is stored separately:

```text
baseline/baseline.sha256
```

Integrity verification can be performed using:

```powershell
python main.py verify
```

The integrity module provides functionality for:

- Canonical JSON representation
- SHA-256 calculation
- File hashing
- File hash verification

This helps detect unexpected modification of the baseline file.

---
### Evidence Integrity

Every generated snapshot is accompanied by a SHA-256 hash file.

SentinelTrace can independently verify snapshot evidence to detect unexpected modification or corruption after collection.

```text
Snapshot JSON
     │
     ├── SHA-256 hash
     │
     ▼
Evidence Integrity Verification
     │
     ├── Hash matches → Verified
     └── Hash differs → FAILED

```
### Report Integrity

Every generated JSON audit report is accompanied by a SHA-256 hash file.

SentinelTrace can independently verify report integrity to detect unexpected modification or corruption after the report is generated.

```text
Report JSON
     │
     ├── SHA-256 hash
     │
     ▼
Report Integrity Verification
     │
     ├── Hash matches → Verified
     └── Hash differs → FAILED
```

# Audit Reports

SentinelTrace generates structured audit reports.

Reports are stored under:

```text
reports/
```

Two report formats are supported:

### JSON

Machine-readable output suitable for:

- Automation
- Future integrations
- Programmatic analysis
- Security tooling

### Text

Human-readable output designed for quick review.

Example:

```text
========================================
       SENTINELTRACE AUDIT REPORT
========================================

System Information
------------------
Computer: WINDOWS-ENDPOINT
Operating System: Windows
Architecture: AMD64

Changes Detected
----------------
Added: 2
Removed: 2
Modified: 14
Unchanged: 1132

Investigation Findings
----------------------
Total Findings: 17
```

Generated reports are intentionally excluded from Git because they represent machine-specific runtime data.

---

# Command-Line Interface

SentinelTrace provides both direct CLI commands and an interactive menu.

## Direct Commands

### Create Baseline

```powershell
python main.py baseline
```

Creates the trusted endpoint baseline and its SHA-256 integrity hash.

### Run Full Audit

```powershell
python main.py audit
```

Collects the current endpoint state.

### Compare Against Baseline

```powershell
python main.py compare
```

Compares the current endpoint state with the trusted baseline and generates change findings and reports.

### Verify Baseline

```powershell
python main.py verify
```

Verifies the integrity of the stored baseline.

### Verify Evidence Integrity

```powershell
python main.py verify-evidence
```
Verifies the integrity of generated snapshot evidence using its SHA-256 hash.

### Verify Report Integrity

```powershell
python main.py verify-report
```

Verifies the integrity of generated audit reports using their SHA-256 hash.

### View Status

```powershell
python main.py status
```

Displays the current SentinelTrace audit status.

---

# Interactive CLI

Running:

```powershell
python main.py
```

opens the interactive menu.

```text
========================================
          SENTINELTRACE
========================================

1. Compare Changes
2. What Are the Changes?
3. Run Full Audit
4. Create Snapshot
5. Create Baseline
6. Verify Baseline Integrity
7. Verify Evidence Integrity
8. Verify Report Integrity
9. View Audit Status
10. View Latest Report
11. Exit
```

The interactive interface provides a simple way to operate the audit system without remembering individual commands.

---

# Testing

SentinelTrace includes an automated test suite covering the core auditing components.

Current result:

```text
36 passed
```

Test coverage includes:

- Account collection
- Baseline creation
- Baseline integrity
- CLI commands
- Endpoint collection
- Change comparison
- Driver collection
- File integrity
- Investigation engine
- Network collection
- Report generation
- Security configuration
- Service collection
- Software inventory
- Startup collection
- System information
- Scheduled task collection

Run the test suite with:

```powershell
python -m pytest
```

The test suite currently contains **36 passing tests**.

Some tests perform real Windows endpoint collection, so execution time can be significantly longer than pure unit tests.

---

# Project Structure

```text
sentineltrace/
│
├── audit/
│   ├── __init__.py
│   ├── accounts.py
│   ├── baseline.py
│   ├── collector.py
│   ├── compare.py
│   ├── drivers.py
│   ├── integrity.py
│   ├── investigation.py
│   ├── network.py
│   ├── report.py
│   ├── security.py
│   ├── services.py
│   ├── software.py
│   ├── startup.py
│   ├── system_info.py
│   └── tasks.py
│
├── cli/
│   ├── __init__.py
│   ├── commands.py
│   ├── display.py
│   └── menu.py
│
├── tests/
│   ├── __init__.py
│   ├── test_accounts.py
│   ├── test_baseline_integrity.py
│   ├── test_cli_commands.py
│   ├── test_collector.py
│   ├── test_compare.py
│   ├── test_drivers.py
│   ├── test_integrity.py
│   ├── test_investigation.py
│   ├── test_network.py
│   ├── test_report.py
│   ├── test_security.py
│   ├── test_services.py
│   ├── test_software.py
│   ├── test_startup.py
│   ├── test_system_info.py
│   └── test_tasks.py
│
├── baseline/
├── snapshots/
├── reports/
├── logs/
│
├── main.py
├── README.md
└── .gitignore
```

### Runtime Directories

The following directories contain generated machine-specific data:

```text
baseline/
snapshots/
reports/
logs/
```

These runtime artifacts are excluded from Git through `.gitignore`.

---

# Module Responsibilities

| Module | Responsibility |
|---|---|
| `system_info.py` | Collects Windows system information |
| `accounts.py` | Collects local users and administrators |
| `services.py` | Collects Windows service information |
| `software.py` | Collects installed software |
| `network.py` | Collects network adapters and TCP connections |
| `security.py` | Collects Windows security configuration |
| `startup.py` | Collects startup entries and boot/logon tasks |
| `tasks.py` | Collects scheduled task information |
| `drivers.py` | Collects Windows driver information |
| `collector.py` | Coordinates endpoint collection |
| `baseline.py` | Creates and manages the trusted baseline |
| `compare.py` | Compares endpoint states |
| `investigation.py` | Converts changes into structured findings |
| `integrity.py` | Provides SHA-256 integrity functions |
| `report.py` | Generates human-readable audit reports |
| `commands.py` | Implements CLI operations |
| `display.py` | Handles CLI presentation |
| `menu.py` | Provides the interactive CLI menu |

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.14.7 | Core programming language |
| PowerShell | Windows system data collection |
| Windows Registry | Software and startup inventory |
| SHA-256 | Baseline integrity verification |
| pytest | Automated testing |
| Git | Version control |
| GitHub | Source-code hosting |

---

# Requirements

SentinelTrace is designed for **Windows**.

### Required

- Windows 10/11
- Python 3.14+
- PowerShell
- Git

### Recommended

Run SentinelTrace from an elevated PowerShell or VS Code terminal when required data collection depends on administrator privileges.

Some Windows information may be unavailable without sufficient permissions.

---

# Installation

Clone the repository:

```powershell
git clone https://github.com/ShreyashBandekar/sentineltrace.git
cd sentineltrace
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

Expected environment:

```text
Python 3.14.7
```

Run the application:

```powershell
python main.py
```

---

# Typical Audit Workflow

A typical SentinelTrace workflow can be performed in four stages.

## 1. Establish the Baseline

Run SentinelTrace on the trusted system state:

```powershell
python main.py baseline
```

This creates the baseline and its integrity hash.

---

## 2. Perform the Service or Maintenance Activity

The system can then undergo normal maintenance, troubleshooting, software installation, updates, or other authorized activity.

SentinelTrace does not need to capture private user activity to perform the audit.

---

## 3. Run the Audit

After the activity:

```powershell
python main.py audit
```

This captures the current endpoint state.

---

## 4. Compare the System

Run:

```powershell
python main.py compare
```

SentinelTrace then reports:

- Added items
- Removed items
- Modified items
- Unchanged items
- Investigation findings

This provides a structured before/after view of the endpoint.

---

# Security & Privacy

SentinelTrace is designed as a **defensive endpoint auditing tool**.

It does not intentionally implement:

- Password capture
- Credential harvesting
- Token capture
- Keystroke logging
- Private message capture
- Audio recording
- Hidden screen capture
- Covert surveillance
- Stealth persistence
- Administrator-bypass mechanisms
- Admin-resistant disabling
- Credential theft

The objective is to record **observable endpoint configuration and state**, not private user activity.

---

# Important Interpretation Note

A detected change does **not** automatically mean that a security compromise occurred.

Windows systems naturally change over time.

Examples include:

- Windows Updates
- Driver updates
- Application updates
- Software installations
- Software removals
- Service state changes
- Scheduled task execution
- Network changes
- Security configuration changes
- User-initiated configuration changes

SentinelTrace therefore provides **evidence for investigation**, rather than automatically declaring a change malicious.

For example, a newly installed service may be completely legitimate, while an unexpected service installation may require further investigation.

Context is important.

---

# Roadmap

## Phase 1 — Foundation

- [x] Project structure
- [x] System information collection
- [x] Local account collection
- [x] Service collection
- [x] Software inventory
- [x] Network collection
- [x] Security configuration collection
- [x] Startup collection
- [x] Scheduled task collection
- [x] Driver collection

## Phase 2 — Baseline & Integrity

- [x] Baseline generation
- [x] Baseline SHA-256 hash
- [x] Baseline verification
- [x] Snapshot support

## Phase 3 — Change Detection

- [x] Added item detection
- [x] Removed item detection
- [x] Modified item detection
- [x] Unchanged item detection
- [x] Volatile scheduled-task handling

## Phase 4 — Investigation

- [x] Structured findings
- [x] Finding timestamps
- [x] Change classification
- [x] Investigation details

## Phase 5 — Reporting

- [x] JSON reports
- [x] Human-readable reports
- [x] Latest report viewing

## Phase 6 — CLI

- [x] Direct CLI commands
- [x] Interactive menu
- [x] Status command
- [x] Baseline integrity verification
- [x] Evidence integrity verification
- [x] Report integrity verification
- [x] Report viewing

## Phase 7 — Testing

- [x] Automated test suite
- [x] 50/50 tests passing
- [x] Windows integration coverage
- [x] GitHub Actions CI

## Phase 8 — Future Security Features

Planned future improvements may include:

- [ ] Process inventory
- [ ] Windows Event Log analysis
- [ ] More detailed persistence detection
- [ ] File integrity monitoring
- [ ] Sigma-based detection rules
- [ ] Improved investigation workflows
- [ ] Automated GitHub Actions testing
- [ ] Additional report formats

---

# Project Status

| Component | Status |
|---|---|
| Endpoint collection | Complete |
| Baseline generation | Complete |
| Snapshot system | Complete |
| Change detection | Complete |
| Investigation engine | Complete |
| Baseline integrity | Complete |
| JSON reports | Complete |
| Text reports | Complete |
| Interactive CLI | Complete |
| Automated tests | 36/36 passing |
| Git repository | Initialized |
| Advanced detection | Planned |
| CI automation | Planned |

---

# Learning Objectives

SentinelTrace was developed to strengthen practical understanding of:

- Windows endpoint security
- Security auditing
- Endpoint state collection
- System integrity monitoring
- Baseline security concepts
- Change detection
- Digital investigation workflows
- Windows services
- Windows scheduled tasks
- Windows startup mechanisms
- Network visibility
- Security configuration auditing
- Python automation
- CLI application design
- Automated testing
- Git and GitHub workflows

The project is intended to demonstrate how endpoint telemetry can be collected and compared systematically rather than relying only on manual inspection.

---

# Author

**Shreyash Bandekar**

Computer Science & Engineering student focused on:

- Cybersecurity
- Security Operations
- Network Security
- Web Development
- Defensive Security Engineering

---

# License

This project is intended for educational, research, and defensive security purposes.

A formal open-source license can be added before public distribution.

---

# Project Vision

SentinelTrace aims to evolve into a practical Windows endpoint auditing and investigation platform.

The long-term goal is to provide a transparent workflow for understanding:

```text
What was the system like?
          ↓
What changed?
          ↓
When did it change?
          ↓
Where did it change?
          ↓
What evidence supports the change?
          ↓
What should be investigated further?
```

The core principle is simple:

> **Observe first. Compare carefully. Investigate with evidence.**
