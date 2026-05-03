from shared.agents.jira_agent import get_issue
from shared.agents.architecture_agent import get_output_path
from shared.agents.publish_agent import publish

issue_key = input("Enter Jira Ticket: ")
domain = input("Enter domain: ")

issue = get_issue(issue_key)
file_path = get_output_path(domain)

publish(issue, domain, file_path)