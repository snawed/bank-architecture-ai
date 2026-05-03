from shared.agents.jira_agent import get_issue, extract_domain
from shared.agents.architecture_agent import run_all_diagrams
from shared.agents.design_document_agent import generate_solution_design
from shared.agents.peer_review_agent import generate_peer_review
from shared.agents.github_agent import *

issue_key = input("Enter Jira Ticket: ")

issue = get_issue(issue_key)
domain = extract_domain(issue.fields.summary)

print("Domain:", domain)

# Run AI
run_all_diagrams(domain)
generate_solution_design(domain, issue.key)
generate_peer_review(domain, issue.key)

# GitHub flow
branch_name = f"{domain.lower()}-solution-design-{issue_key}"

create_branch(branch_name)
commit_changes(f"{issue_key}: AI generated solution design")
push_branch(branch_name)

create_pr(
    f"{issue_key} - {domain} Solution Design",
    (
        "AI generated solution design with C1-C4 diagrams and peer review.\n\n"
        "Responsible architect owns resolution of peer review and human reviewer comments before publication."
    ),
    branch_name
)

print("✅ PR created. Review in GitHub.")
