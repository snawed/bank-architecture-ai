import requests
from requests.auth import HTTPBasicAuth
from shared.config.config import CONFLUENCE_URL, JIRA_EMAIL, JIRA_API_TOKEN

def upload_file(file_path, page_id):
    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}/child/attachment"

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    headers = {
        "X-Atlassian-Token": "no-check"
    }

    with open(file_path, 'rb') as f:
        files = {'file': f}

        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            files=files
        )

    if response.status_code in [200, 201]:
        print("✅ Uploaded to Confluence")
    else:
        print("❌ Upload failed:", response.text)