import subprocess
import requests
from shared.config.config import GITHUB_BASE_BRANCH, GITHUB_REPO, GITHUB_TOKEN

def get_headers():
    if not GITHUB_TOKEN:
        raise EnvironmentError("GITHUB_TOKEN is not set")

    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def create_branch(branch_name):
    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    if current_branch == branch_name:
        print(f"Already on branch {branch_name}")
        return

    branch_exists = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True,
    ).returncode == 0

    if branch_exists:
        subprocess.run(["git", "checkout", branch_name], check=True)
    else:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

def commit_changes(message):
    subprocess.run(["git", "add", "."], check=True)
    has_changes = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True,
    ).returncode != 0

    if not has_changes:
        print("No staged changes to commit")
        return

    subprocess.run(["git", "commit", "-m", message], check=True)

def push_branch(branch_name):
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

def create_pr(title, body, branch_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls"
    payload = {
        "title": title,
        "body": body,
        "base": GITHUB_BASE_BRANCH,
        "head": branch_name,
    }

    response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
    response.raise_for_status()

    pr_url = response.json()["html_url"]
    print(f"✅ PR created: {pr_url}")
    return pr_url

def add_pr_comment(pr_url, body):
    pr_number = pr_url.rstrip("/").split("/")[-1]
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{pr_number}/comments"
    payload = {"body": body}

    response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
    response.raise_for_status()

    comment_url = response.json()["html_url"]
    print(f"✅ PR comment added: {comment_url}")
    return comment_url

def build_peer_review_comment(review_path):
    with open(review_path, "r", encoding="utf-8") as review_file:
        review = review_file.read()

    return (
        "## AI Peer Review Findings\n\n"
        "The responsible architect owns resolution of the findings below. "
        "Human reviewers should validate the updates before approval.\n\n"
        f"{review}"
    )
