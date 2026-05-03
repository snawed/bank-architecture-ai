from pathlib import Path

from shared.agents.jira_agent import attach_file
from shared.agents.confluence_agent import (
    render_solution_design_storage,
    update_page_content,
    upload_file,
)
from shared.config.config import CONFLUENCE_PAGE_MAP

def publish(issue, domain, file_path=None):
    print("Publishing...")

    page_id = CONFLUENCE_PAGE_MAP.get(domain)

    if not page_id:
        raise Exception("No Confluence page mapping")

    artifacts = get_publish_artifacts(domain, file_path)

    for artifact in artifacts:
        attach_file(issue, artifact)
        upload_file(artifact, page_id)

    solution_design_path = get_solution_design_path(domain)
    diagram_names = [
        Path(path).name
        for path in get_diagram_paths(domain)
        if Path(path).exists()
    ]

    if Path(solution_design_path).exists():
        storage_body = render_solution_design_storage(
            domain,
            solution_design_path,
            diagram_names,
        )
        update_page_content(
            page_id,
            f"{domain} Solution Design",
            storage_body,
        )

    print("🎉 Publish complete")

def get_publish_artifacts(domain, file_path=None):
    artifacts = []

    if file_path:
        artifacts.append(file_path)

    artifacts.extend(get_diagram_paths(domain))
    artifacts.append(get_solution_design_path(domain))

    deduped_artifacts = []
    seen = set()

    for artifact in artifacts:
        artifact_path = str(Path(artifact))

        if artifact_path in seen:
            continue

        seen.add(artifact_path)

        if Path(artifact_path).exists():
            deduped_artifacts.append(artifact_path)

    return deduped_artifacts

def get_diagram_paths(domain):
    return [
        f"{domain}/diagrams/{diagram_level}.svg"
        for diagram_level in ["C1", "C2", "C3", "C4"]
    ]

def get_solution_design_path(domain):
    return f"{domain}/docs/solution_design.md"
