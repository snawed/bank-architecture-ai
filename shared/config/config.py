import os

JIRA_URL = "https://snawed.atlassian.net"
CONFLUENCE_URL = "https://snawed.atlassian.net/wiki"
JIRA_EMAIL = "s_nawed@yahoo.com"
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
# GITHUB
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "snawed/bank-architecture-ai"

CONFLUENCE_PAGE_MAP = {
    "CustomerOnboarding": "98611",
    "Payments": "PAGE_ID",
    "Cards": "PAGE_ID"
}

# GITHUB
GITHUB_BASE_BRANCH = "main"