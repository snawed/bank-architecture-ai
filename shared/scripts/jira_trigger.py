from shared.agents.jira_agent import get_issue, extract_domain
from shared.agents.architecture_agent import run_c1
from shared.agents.github_agent import *

issue_key = input("Enter Jira Ticket: ")

issue = get_issue(issue_key)
domain = extract_domain(issue.fields.summary)

print("Domain:", domain)

# Run AI
run_c1(domain)

# GitHub flow
branch_name = f"{domain.lower()}-c1-{issue_key}"

create_branch(branch_name)
commit_changes(f"{issue_key}: AI generated C1 diagram")
push_branch(branch_name)

create_pr(
    f"{issue_key} - {domain} C1",
    "AI generated architecture diagram",
    branch_name
)

print("✅ PR created. Review in GitHub.")