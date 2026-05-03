import re
import sys
from pathlib import Path

import requests

MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

DIAGRAM_PROMPTS = {
    "C1": {
        "name": "C1 System Context Diagram",
        "instructions": """
Show the system in scope, primary users, channels, and external systems.
Include actors, external systems, and the main domain system.
Keep this at system context level.
""",
    },
    "C2": {
        "name": "C2 Container Diagram",
        "instructions": """
Show the major deployable or runtime containers inside the domain system.
Include applications, APIs, services, databases, queues, and external integrations.
Include protocols or interaction labels where useful.
""",
    },
    "C3": {
        "name": "C3 Component Diagram",
        "instructions": """
Show the main components inside the most important domain container.
Include responsibilities, dependencies, internal services, adapters, validators, and repositories where useful.
""",
    },
    "C4": {
        "name": "C4 Code / Detailed Design Diagram",
        "instructions": """
Show the lowest useful level of detail for the solution.
Use modules, classes, packages, handlers, clients, repositories, or deployment-level elements where useful.
Keep it readable and avoid implementation noise.
""",
    },
}


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python shared/scripts/generate_diagram.py <domain> <C1|C2|C3|C4>")

    domain = sys.argv[1]
    diagram_level = sys.argv[2].upper()

    if diagram_level not in DIAGRAM_PROMPTS:
        raise SystemExit(f"Unsupported diagram level: {diagram_level}")

    domain_dir = Path(domain)
    input_context = domain_dir / "docs" / "context.md"
    output_mmd = domain_dir / "diagrams" / f"{diagram_level}.mmd"

    if not input_context.exists():
        raise SystemExit(f"Context file not found: {input_context}")

    output_mmd.parent.mkdir(parents=True, exist_ok=True)

    context = input_context.read_text(encoding="utf-8")
    prompt_config = DIAGRAM_PROMPTS[diagram_level]

    prompt = f"""
You are a senior banking architect.

Generate ONLY a valid Mermaid {prompt_config["name"]} for the {domain} domain.

STRICT RULES:
- Output ONLY Mermaid code
- Start with: graph TD
- Each relationship MUST be on a new line
- Use simple node ids without spaces
- Use labels in square brackets only when useful
- Do NOT use markdown fences
- Do NOT include explanations
- Do NOT use semicolons

Architecture guidance:
{prompt_config["instructions"]}

<context>
{context}
</context>
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()

    raw_output = response.json()["response"]
    final_mermaid = clean_mermaid(raw_output, domain, diagram_level)

    output_mmd.write_text(final_mermaid, encoding="utf-8")

    print(f"\n✅ {diagram_level} Mermaid diagram generated successfully!\n")
    print(final_mermaid)
    print(f"\n📁 Saved to: {output_mmd}\n")


def clean_mermaid(raw_output, domain, diagram_level):
    match = re.search(r"(graph TD[\s\S]*)", raw_output)
    mermaid = match.group(1) if match else raw_output
    mermaid = mermaid.replace(";", "\n").replace("```mermaid", "").replace("```", "")

    clean_lines = ["graph TD"]

    for line in mermaid.splitlines():
        line = line.strip()

        if not line or line == "graph TD":
            continue

        if "-->" not in line:
            continue

        line = normalize_mermaid_edge(line)
        line = re.sub(r"\s+", " ", line)
        clean_lines.append(f"    {line}")

    if len(clean_lines) == 1:
        return fallback_diagram(domain, diagram_level)

    return "\n".join(clean_lines) + "\n"


def normalize_mermaid_edge(line):
    line = line.replace("/", " ")
    line = re.sub(r"[()]", "", line)
    line = line.replace("&", "and")
    line = re.sub(r"-+>>", "-->", line)
    line = re.sub(r"-{3,}", "-->", line)

    # Fix common model output: A-->|Label|>B should be A -->|Label| B.
    line = re.sub(r"\|>\s*", "| ", line)

    # Fix common model output: A[Label]|-->B should be A[Label]-->B.
    line = line.replace("]|-->", "]-->")

    # Mermaid is happier when a label-closing pipe is followed by whitespace.
    line = re.sub(r"(\|)([A-Za-z_][A-Za-z0-9_]*(?:\[|$))", r"\1 \2", line)

    return line


def fallback_diagram(domain, diagram_level):
    fallback_edges = {
        "C1": [
            "Customer[Customer] --> MobileApp[Mobile App]",
            "Customer --> WebApp[Web App]",
            f"MobileApp --> DomainSystem[{domain} System]",
            "WebApp --> DomainSystem",
            "DomainSystem --> IdentityProvider[Identity Provider]",
            "DomainSystem --> CoreBanking[Core Banking System]",
            "DomainSystem --> NotificationService[Notification Service]",
        ],
        "C2": [
            "MobileApp[Mobile App] --> ApiGateway[API Gateway]",
            "WebApp[Web App] --> ApiGateway",
            "ApiGateway --> DomainApi[Domain API]",
            "DomainApi --> WorkflowService[Workflow Service]",
            "WorkflowService --> DomainDatabase[(Domain Database)]",
            "WorkflowService --> MessageQueue[Message Queue]",
            "WorkflowService --> ExternalIntegration[External Integration Adapter]",
            "ExternalIntegration --> CoreBanking[Core Banking System]",
        ],
        "C3": [
            "DomainApi[Domain API] --> Controller[Request Controller]",
            "Controller --> ApplicationService[Application Service]",
            "ApplicationService --> Validator[Business Validator]",
            "ApplicationService --> WorkflowEngine[Workflow Engine]",
            "WorkflowEngine --> Repository[Repository]",
            "WorkflowEngine --> IntegrationClient[Integration Client]",
            "Repository --> DomainDatabase[(Domain Database)]",
            "IntegrationClient --> ExternalSystems[External Systems]",
        ],
        "C4": [
            "ApplicationService[ApplicationService] --> DomainModel[DomainModel]",
            "ApplicationService --> PolicyEngine[PolicyEngine]",
            "PolicyEngine --> BusinessRules[BusinessRules]",
            "ApplicationService --> RepositoryInterface[RepositoryInterface]",
            "RepositoryInterface --> SqlRepository[SqlRepository]",
            "ApplicationService --> IntegrationPort[IntegrationPort]",
            "IntegrationPort --> ExternalClient[ExternalClient]",
        ],
    }

    lines = ["graph TD"]
    lines.extend(f"    {edge}" for edge in fallback_edges[diagram_level])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
