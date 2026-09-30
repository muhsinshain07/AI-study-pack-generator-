"""Helper functions: file reading, JSON parsing, Markdown export."""
import json

from pypdf import PdfReader


def extract_text(source, name=None):
    """Extract text from a PDF/TXT/MD file (path string or uploaded file object)."""
    name = (name or getattr(source, "name", None) or str(source)).lower()
    if name.endswith(".pdf"):
        reader = PdfReader(source)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if isinstance(source, str):
        with open(source, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return source.read().decode("utf-8", errors="ignore")


def parse_json(raw):
    """Pull the JSON object out of the model's reply."""
    raw = raw.strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("The model did not return valid JSON. Please try again.")
    return json.loads(raw[start : end + 1])


def to_markdown(pack):
    """Convert a study pack dict into a downloadable Markdown document."""
    out = [f"# {pack.get('title', 'Study Pack')}", "", "## Summary", pack.get("summary", ""), ""]
    out.append("## Key Concepts")
    for c in pack.get("key_concepts", []):
        out.append(f"- **{c['term']}**: {c['definition']}")
    out += ["", "## Flashcards"]
    for i, f in enumerate(pack.get("flashcards", []), 1):
        out.append(f"{i}. **Q:** {f['q']}  \n   **A:** {f['a']}")
    out += ["", "## Practice Quiz"]
    for i, q in enumerate(pack.get("quiz", []), 1):
        out.append(f"**{i}. {q['question']}**")
        for j, opt in enumerate(q["options"]):
            out.append(f"   - {'ABCD'[j]}. {opt}")
        out.append(f"   - *Answer: {'ABCD'[q['answer_index']]}* — {q['explanation']}")
        out.append("")
    out.append("## Study Plan")
    for d in pack.get("study_plan", []):
        out.append(f"### {d['day']}: {d['focus']}")
        out += [f"- {t}" for t in d.get("tasks", [])]
    return "\n".join(out)
