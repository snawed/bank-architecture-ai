import os

try:
    from shared.config.local_config import (
        LOCAL_GITHUB_TOKEN,
        LOCAL_JIRA_API_TOKEN,
    )
except ImportError:
    LOCAL_GITHUB_TOKEN = None
    LOCAL_JIRA_API_TOKEN = None

JIRA_URL = "https://snawed.atlassian.net"
CONFLUENCE_URL = "https://snawed.atlassian.net/wiki"
JIRA_EMAIL = "s_nawed@yahoo.com"
JIRA_API_TOKEN = LOCAL_JIRA_API_TOKEN or os.getenv("JIRA_API_TOKEN")
# GITHUB
GITHUB_TOKEN = LOCAL_GITHUB_TOKEN or os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "snawed/bank-architecture-ai"

CONFLUENCE_PAGE_MAP = {
    "CustomerOnboarding": "98611",
    "Payments": "PAGE_ID",
    "Cards": "PAGE_ID"
}

# GITHUB
GITHUB_BASE_BRANCH = "main"
