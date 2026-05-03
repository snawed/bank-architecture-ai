import requests
import re
from requests.auth import HTTPBasicAuth

# ==============================
# CONFIG
# ==============================
MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

INPUT_CONTEXT = "CustomerOnboarding/docs/context.md"
OUTPUT_MMD = "CustomerOnboarding/diagrams/C1.mmd"


# ==============================
# LOAD CONTEXT
# ==============================
with open(INPUT_CONTEXT, "r") as f:
    context = f.read()


# ==============================
# PROMPT (STRICT FORMAT)
# ==============================
prompt = f"""
You are a senior banking architect.

Generate ONLY a valid Mermaid C1 Context Diagram.

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
with open(OUTPUT_MMD, "w") as f:
    f.write(final_mermaid)

print("\n✅ Mermaid diagram generated successfully!\n")
print(final_mermaid)
print(f"\n📁 Saved to: {OUTPUT_MMD}\n")

