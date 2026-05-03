import requests
import re
import sys
from pathlib import Path

# ==============================
# CONFIG
# ==============================
MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

if len(sys.argv) != 2:
    raise SystemExit("Usage: python shared/scripts/generate_c1.py <domain>")

DOMAIN = sys.argv[1]
DOMAIN_DIR = Path(DOMAIN)
INPUT_CONTEXT = DOMAIN_DIR / "docs" / "context.md"
OUTPUT_MMD = DOMAIN_DIR / "diagrams" / "C1.mmd"

if not INPUT_CONTEXT.exists():
    raise SystemExit(f"Context file not found: {INPUT_CONTEXT}")

OUTPUT_MMD.parent.mkdir(parents=True, exist_ok=True)


# ==============================
# LOAD CONTEXT
# ==============================
with open(INPUT_CONTEXT, "r", encoding="utf-8") as f:
    context = f.read()


# ==============================
# PROMPT (STRICT FORMAT)
# ==============================
prompt = f"""
You are a senior banking architect.

Generate ONLY a valid Mermaid C1 Context Diagram for the {DOMAIN} domain.

STRICT RULES:
- Output ONLY Mermaid code
- Start with: graph TD
- Each relationship MUST be on a new line
- Do NOT use special characters like (), /, :
- Use simple names (e.g., MobileApp, CoreBanking)
- Do NOT include explanations
- Do NOT include ``` or markdown

Include:
- Customer
- MobileApp and WebApp
- OnboardingSystem
- KYCProvider
- AMLSystem
- CoreBanking

<context>
{context}
</context>
"""


# ==============================
# CALL OLLAMA
# ==============================
response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
)

raw_output = response.json()["response"]


# ==============================
# CLEAN OUTPUT
# ==============================

# Extract from "graph TD"
match = re.search(r"(graph TD[\s\S]*)", raw_output)

if match:
    mermaid = match.group(1)
else:
    print("⚠️ Could not find 'graph TD' — using raw output")
    mermaid = raw_output

# Remove unwanted characters
mermaid = mermaid.replace(";", "\n")

# Split lines
lines = mermaid.split("\n")

clean_lines = []

for line in lines:
    line = line.strip()

    # Keep only valid lines
    if "-->" in line:
        # Remove invalid characters
        line = re.sub(r"[()/]", "", line)

        # Fix spacing issues
        line = line.replace("  ", " ")

        clean_lines.append(line)

# Rebuild clean Mermaid
final_mermaid = "graph TD\n"

for line in clean_lines:
    final_mermaid += "    " + line + "\n"


# ==============================
# SAVE FILE
# ==============================
with open(OUTPUT_MMD, "w", encoding="utf-8") as f:
    f.write(final_mermaid)

print("\n✅ Mermaid diagram generated successfully!\n")
print(final_mermaid)
print(f"\n📁 Saved to: {OUTPUT_MMD}\n")
