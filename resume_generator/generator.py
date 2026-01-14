import json
from pathlib import Path
import subprocess
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "resume_template.tex.j2"
PROFILE_FILE = r"E:\Desktop\webAutomation\utlis\profile.json"
OUTPUT_FILE = "output/resume.tex"

def compile_with_pdflatex(tex_path: Path):
    if not tex_path.exists():
        raise FileNotFoundError(f"{tex_path} not found")

    for _ in range(2):  # run twice
        subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_path.name
            ],
            cwd=tex_path.parent,  # 🔥 VERY IMPORTANT
            check=True
        )

    print(f"✅ PDF generated: {tex_path.with_suffix('.pdf')}")

# ---------------- LOAD DATA ----------------
with open(PROFILE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# ---------------- JINJA ENV ----------------
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=False,
    variable_start_string=r"\VAR{",
    variable_end_string="}",
    block_start_string=r"\BLOCK{",
    block_end_string="}",
    comment_start_string=r"\#{",
    comment_end_string="}",
)

template = env.get_template(TEMPLATE_FILE)
rendered = template.render(**data)

# ---------------- WRITE TEX ----------------
Path("output").mkdir(exist_ok=True)
tex_path = Path(OUTPUT_FILE)
tex_path.write_text(rendered, encoding="utf-8")

print("✅ Resume rendered correctly")

# ---------------- COMPILE PDF ----------------
compile_with_pdflatex(tex_path)
