from shared.agents.jira_agent import attach_file
from shared.agents.confluence_agent import upload_file
from shared.config.config import CONFLUENCE_PAGE_MAP

def publish(issue, domain, file_path):
    print("Publishing...")

    # Jira
    attach_file(issue, file_path)

    # Confluence
    page_id = CONFLUENCE_PAGE_MAP.get(domain)

    if not page_id:
        raise Exception("No Confluence page mapping")

    upload_file(file_path, page_id)

    print("🎉 Publish complete")