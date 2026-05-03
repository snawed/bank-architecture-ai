from shared.agents.workflow_agent import (
    create_solution_design_pr,
    generate_design_package,
    resolve_domain,
)

issue_key = input("Enter Jira Ticket: ")

issue, domain = resolve_domain(issue_key)

print("Domain:", domain)

generate_design_package(issue.key, domain)
create_solution_design_pr(issue.key, domain)

print("✅ PR created. Review in GitHub.")
