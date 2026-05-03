import subprocess
from shared.config.config import GITHUB_BASE_BRANCH

def create_branch(branch_name):
    subprocess.run(["git", "checkout", "-b", branch_name])

def commit_changes(message):
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", message])

def push_branch(branch_name):
    subprocess.run(["git", "push", "-u", "origin", branch_name])

def create_pr(title, body, branch_name):
    subprocess.run([
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--base", GITHUB_BASE_BRANCH,
        "--head", branch_name
    ])