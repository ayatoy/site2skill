import os
import shutil
import argparse
import logging
import sys
from typing import Optional

if sys.version_info >= (3, 9):
    from importlib.resources import files as importlib_files
else:
    from importlib_resources import files as importlib_files

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_skill_structure(
    skill_name: str,
    source_dir: Optional[str],
    output_base: str = ".claude/skills",
    skill_description: Optional[str] = None,
    full_sync: bool = False,
    replace_skill_md: bool = False,
    target_agent: Optional[str] = None,
) -> None:
    """
    Generate the Skill structure following SKILL.md + references/ pattern.
    Structure:
      <skill-name>/
        SKILL.md         # Entry point, usage instructions
        references/      # Documentation files
        scripts/         # (Optional) Executable code
    """
    skill_dir = os.path.join(output_base, skill_name)

    # Define subdirectories
    references_dir = os.path.join(skill_dir, "references")
    docs_dir = os.path.join(skill_dir, "docs")  # legacy fallback directory
    scripts_dir = os.path.join(skill_dir, "scripts")

    # Create directories
    if os.path.exists(skill_dir):
        logger.warning(f"Skill directory {skill_dir} already exists.")
    else:
        os.makedirs(skill_dir)

    if full_sync:
        if os.path.exists(references_dir):
            shutil.rmtree(references_dir)
        if os.path.exists(docs_dir):
            shutil.rmtree(docs_dir)
    os.makedirs(references_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    # Create SKILL.md
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    if replace_skill_md or not os.path.exists(skill_md_path):
        description = skill_description or f"{skill_name.upper()} documentation assistant"
        frontmatter_lines = [
            "---",
            f"name: {skill_name}",
            f"description: {description}",
        ]
        if target_agent:
            frontmatter_lines.append("metadata:")
            frontmatter_lines.append(f"  target_agent: {target_agent}")
        frontmatter_lines.append("---")
        frontmatter = "\n".join(frontmatter_lines)
        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(f"""{frontmatter}

# {skill_name.upper()} Skill

This skill provides access to {skill_name.upper()} documentation.

## Documentation

All documentation files are in the `references/` directory as Markdown files.
For legacy skills, documentation may live in `docs/`.

## Search Tool

```bash
# Run the search script (use python or python3)
python scripts/search_docs.py "<query>"
```

Options:
- `--json` - Output as JSON
- `--max-results N` - Limit results (default: 10)

## Query Building

`"<query>"` is the user's question or topic to search for in the documentation. Before passing a user’s inquiry directly into `"<query>"`, extract all key topics from the inquiry, represent each topic in the user's native language together with its English translation (side by side), join the resulting terms with spaces, and pass that result into `"<query>"`.

## Usage

1. Search or read files in `references/` for relevant information (fallback to `docs/` for legacy)
2. Each file has frontmatter with `source_url` and `fetched_at`
3. Always cite the source URL in responses
4. Note the fetch date - documentation may have changed

## Response Format

```
[Answer based on documentation]

**Source:** [source_url]
**Fetched:** [fetched_at]
```
""")
        logger.info(f"Created {skill_md_path}")

    # Copy scripts using importlib.resources
    dest_search_script = os.path.join(scripts_dir, "search_docs.py")
    dest_readme = os.path.join(scripts_dir, "README.md")

    try:
        templates = importlib_files("site2skill").joinpath("templates")

        search_script_resource = templates.joinpath("search_docs.py")
        with open(dest_search_script, "w", encoding="utf-8") as f:
            f.write(search_script_resource.read_text(encoding="utf-8"))
        os.chmod(dest_search_script, 0o755)
        logger.info("Installed search_docs.py")

        readme_resource = templates.joinpath("scripts_README.md")
        with open(dest_readme, "w", encoding="utf-8") as f:
            f.write(readme_resource.read_text(encoding="utf-8"))
        logger.info("Installed scripts/README.md")
    except Exception as e:
        logger.warning(f"Failed to copy templates: {e}")

    # Copy Markdown files (preserve source structure)
    if source_dir and os.path.exists(source_dir):
        logger.info(f"Copying files from {source_dir}...")
        file_count = 0

        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".md"):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, source_dir)
                    dst_path = os.path.join(references_dir, rel_path)

                    # Security check: Ensure dst_path is strictly within references_dir
                    abs_dst_path = os.path.abspath(dst_path)
                    abs_references_dir = os.path.abspath(references_dir)

                    if os.path.commonpath([abs_dst_path, abs_references_dir]) != abs_references_dir:
                        logger.warning(f"Skipping potential path traversal file: {rel_path}")
                        continue

                    parent_dir = os.path.dirname(dst_path)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    file_count += 1

        logger.info(f"Copied {file_count} files to references/")
    else:
        logger.warning(f"Source directory {source_dir} not found or empty.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Skill Structure.")
    parser.add_argument("skill_name", help="Name of the skill (e.g., payjp)")
    parser.add_argument(
        "skill_description",
        nargs="?",
        help=(
            "Optional description to replace the default "
            f"'{'{'}skill_name.upper(){'}'} documentation assistant'"
        ),
    )
    parser.add_argument("--source", "-s", help="Source directory containing Markdown files")
    parser.add_argument("--output", "-o", default=".claude/skills", help="Base output directory")
    parser.add_argument(
        "--full-sync",
        action="store_true",
        help="Replace references/ (and legacy docs/) contents before copying.",
    )
    parser.add_argument(
        "--replace-skill-md",
        action="store_true",
        help="Overwrite SKILL.md even if it already exists.",
    )
    parser.add_argument(
        "--target-agent",
        default=None,
        help="Optional target agent metadata to embed in SKILL.md.",
    )

    args = parser.parse_args()

    generate_skill_structure(
        args.skill_name,
        args.source,
        args.output,
        args.skill_description,
        args.full_sync,
        args.replace_skill_md,
        args.target_agent,
    )
