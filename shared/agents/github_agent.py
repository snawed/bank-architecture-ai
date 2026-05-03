import subprocess
import requests
from shared.config.config import GITHUB_BASE_BRANCH, GITHUB_REPO, GITHUB_TOKEN

def create_branch(branch_name):
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)

def commit_changes(message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)

def push_branch(branch_name):
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

def create_pr(title, body, branch_name):
    if not GITHUB_TOKEN:
        raise EnvironmentError("GITHUB_TOKEN is not set")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "title": title,
        "body": body,
        "base": GITHUB_BASE_BRANCH,
        "head": branch_name,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    pr_url = response.json()["html_url"]
    print(f"✅ PR created: {pr_url}")
    return pr_url
