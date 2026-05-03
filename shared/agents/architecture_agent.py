import subprocess
import os

def get_base_dir():
    # Goes from shared/agents → project root
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

def run_c1(domain):
    run_diagram(domain, "C1")

def run_c2(domain):
    run_diagram(domain, "C2")

def run_c3(domain):
    run_diagram(domain, "C3")

def run_c4(domain):
    run_diagram(domain, "C4")

def run_all_diagrams(domain):
    for diagram_level in ["C1", "C2", "C3", "C4"]:
        run_diagram(domain, diagram_level)

def run_diagram(domain, diagram_level):
    base_dir = get_base_dir()
    script_path = os.path.join(base_dir, "shared", "scripts", "run_diagram.sh")

    print(f"Running AI for {domain} {diagram_level}...")
    subprocess.run([script_path, domain, diagram_level], check=True)

def get_output_path(domain, artifact_name="C1.svg"):
    base_dir = get_base_dir()
    path = os.path.join(base_dir, domain, "diagrams", artifact_name)
    return os.path.abspath(path)

def get_diagram_paths(domain):
    return [get_output_path(domain, f"{level}.svg") for level in ["C1", "C2", "C3", "C4"]]
