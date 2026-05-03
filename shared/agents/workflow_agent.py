from shared.agents.architecture_agent import run_all_diagrams
from shared.agents.design_document_agent import generate_solution_design
from shared.agents.github_agent import (
    add_pr_comment,
    build_peer_review_comment,
    commit_changes,
    create_branch,
    create_pr,
    push_branch,
)
from shared.agents.jira_agent import extract_domain, get_issue
from shared.agents.peer_review_agent import generate_peer_review, get_peer_review_path
from shared.agents.publish_agent import publish
from shared.agents.github_agent import push_branch
import subprocess


def resolve_domain(issue_key):
    issue = get_issue(issue_key)
    domain = extract_domain(issue.fields.summary)
    return issue, domain


def generate_design_package(issue_key, domain=None):
    issue, resolved_domain = resolve_issue_and_domain(issue_key, domain)

    run_all_diagrams(resolved_domain)
    generate_solution_design(resolved_domain, issue.key)
    generate_peer_review(resolved_domain, issue.key)

    return {
        "issue": issue,
        "domain": resolved_domain,
        "message": f"Generated solution design package and peer review for {issue.key} / {resolved_domain}.",
    }


def run_peer_review(issue_key, domain=None):
    issue, resolved_domain = resolve_issue_and_domain(issue_key, domain)
    generate_peer_review(resolved_domain, issue.key)

    return {
        "issue": issue,
        "domain": resolved_domain,
        "message": f"Generated peer review for {issue.key} / {resolved_domain}.",
    }


def create_solution_design_pr(issue_key, domain=None):
    issue, resolved_domain = resolve_issue_and_domain(issue_key, domain)
    branch_name = f"{resolved_domain.lower()}-solution-design-{issue.key.lower()}"

    create_branch(branch_name)
    commit_changes(f"{issue.key}: AI generated solution design package")
    push_branch(branch_name)

    pr_url = create_pr(
        f"{issue.key} - {resolved_domain} Solution Design",
        (
            "AI generated solution design with C1-C4 diagrams and peer review.\n\n"
            "Responsible architect owns resolution of peer review and human reviewer comments before publication."
        ),
        branch_name,
    )
    comment_url = add_pr_comment(
        pr_url,
        build_peer_review_comment(get_peer_review_path(resolved_domain, issue.key)),
    )

    return {
        "issue": issue,
        "domain": resolved_domain,
        "pr_url": pr_url,
        "comment_url": comment_url,
        "message": f"Created PR: {pr_url}\nAdded peer review comment: {comment_url}",
    }


def publish_solution_design(issue_key, domain=None):
    issue, resolved_domain = resolve_issue_and_domain(issue_key, domain)
    publish(issue, resolved_domain)

    return {
        "issue": issue,
        "domain": resolved_domain,
        "message": f"Published solution design and diagrams for {issue.key} / {resolved_domain}.",
    }


def commit_responsible_architect_fix(issue_key, domain=None):
    issue, resolved_domain = resolve_issue_and_domain(issue_key, domain)
    paths = [
        f"{resolved_domain}/docs/solution_design.md",
        f"{resolved_domain}/reviews/peer_review_{issue.key.upper()}.md",
        f"{resolved_domain}/diagrams/C1.mmd",
        f"{resolved_domain}/diagrams/C1.svg",
        f"{resolved_domain}/diagrams/C2.mmd",
        f"{resolved_domain}/diagrams/C2.svg",
        f"{resolved_domain}/diagrams/C3.mmd",
        f"{resolved_domain}/diagrams/C3.svg",
        f"{resolved_domain}/diagrams/C4.mmd",
        f"{resolved_domain}/diagrams/C4.svg",
    ]

    existing_paths = [path for path in paths if path_exists(path)]

    if not existing_paths:
        raise FileNotFoundError("No solution design or review artifacts found to commit")

    subprocess.run(["git", "add", *existing_paths], check=True)

    has_changes = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True,
    ).returncode != 0

    if not has_changes:
        return {
            "issue": issue,
            "domain": resolved_domain,
            "message": "No responsible architect changes found to commit.",
        }

    subprocess.run(
        ["git", "commit", "-m", f"{issue.key}: resolve responsible architect review comments"],
        check=True,
    )
    push_branch(current_branch())

    return {
        "issue": issue,
        "domain": resolved_domain,
        "message": f"Committed and pushed responsible architect fixes for {issue.key} / {resolved_domain}.",
    }


def resolve_issue_and_domain(issue_key, domain=None):
    issue = get_issue(issue_key)
    resolved_domain = domain or extract_domain(issue.fields.summary)
    return issue, resolved_domain


def path_exists(path):
    from pathlib import Path

    return Path(path).exists()


def current_branch():
    return subprocess.run(
        ["git", "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
