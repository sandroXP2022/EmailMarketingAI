# EmailMarketingAI

**A simple tool for harvesting contact emails from web pages and sending AI-generated emails.**

This repository contains two main scripts:

* `collect.py` — search websites, scrape pages and extract email addresses.
* `email_sender.py` — generate email content using the Mistral AI API and send messages to addresses stored in a CSV file.

> [!WARNING] 
> Use this tool responsibly. 
> Respect `robots.txt`, website Terms of Service, privacy laws (e.g., GDPR), and anti-spam regulations. Only contact recipients when you have legal grounds or consent.

---

## Table of Contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [License](#license)


---

## Requirements

* Python 3.11
* Mistral API Key (free)
---

## Installation

**1.** Clone the repository



**2.** Create and activate a virtual environment (recommended):

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---
## Configuration 

Create a `.env` file in the project root with the following variables:

```env
# SMTP settings
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
EMAIL_SENDER=you@example.com
EMAIL_PASSWORD=supersecretpassword

# Mistral API
MISTRAL_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

**Do not commit** your `.env` to public repositories.

---

## Usage

### collect.py --- Web Scrapper and Email Collector

**1.** Search the web and save results to `websites.txt`:

```bash
python collect.py --search 10 --query "site:example.com contact OR email"
```

* `--search [N]` where `N` limits the number of search results (default 10).
* `--query` specifies the search query. If omitted you should provide a sensible default.

**2.** Extract emails from the `websites.txt` file and append valid rows to `emails.csv`:

```bash
python collect.py --extract
```

**3.** List the contents of `emails.csv`:

```bash
python collect.py --list
```

### email\_sender.py — Email AI Generator

1. Preview generated email content without sending (interactive prompt):

```bash
python email_sender.py --preview
# Follow the prompt to describe the email content
```

2. Generate and send emails to the addresses listed in `emails.csv`:

```bash
python email_sender.py
# You will be prompted for the email content and subject
```

> [!TIP]
> Email body generation uses `context.txt` (if present) plus interactive user input and calls the Mistral API endpoint.



