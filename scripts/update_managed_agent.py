"""
update_managed_agent.py

Sincroniza el Managed Agent de GDSnet con el estado del repo:
  - Para cada SKILL.md en skills/, sube una version nueva (si la skill ya existe en
    el workspace) o crea una skill nueva (si no existe), matcheando por display_title.
  - Reemplaza el system prompt del agente con el contenido actual de
    agent/system_prompt.md.
  - Reemplaza el array de skills del agente para que apunte a las 12 skills del repo,
    todas referenciadas como version='latest'.

Preserva: model, tools, mcp_servers, name, description, metadata.

Uso:
    ANTHROPIC_API_KEY=sk-ant-... python scripts/update_managed_agent.py [--dry-run]

--dry-run lista el plan sin hacer ningun POST/PATCH.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_ID = "agent_011CaXriThLi9RRbcMBHaCrC"
SYSTEM_PROMPT_PATH = REPO_ROOT / "agent" / "system_prompt.md"


def discover_repo_skills(root: Path) -> list[tuple[str, Path]]:
    """Devuelve [(skill_name, skill_dir), ...] para cada SKILL.md en skills/."""
    out: list[tuple[str, Path]] = []
    for md in (root / "skills").rglob("SKILL.md"):
        skill_dir = md.parent
        out.append((skill_dir.name, skill_dir))
    out.sort(key=lambda x: x[0])
    return out


def display_title_for(skill_name: str) -> str:
    """coto -> 'Coto', extracting-products -> 'Extracting Products'."""
    return skill_name.replace("-", " ").title()


def list_workspace_custom_skills(client: anthropic.Anthropic) -> dict[str, str]:
    """display_title -> skill_id, solo skills custom (no las built-in de Anthropic)."""
    out: dict[str, str] = {}
    for s in client.beta.skills.list():
        if getattr(s, "source", None) != "anthropic":
            out[s.display_title] = s.id
    return out


def build_skill_files(skill_dir: Path) -> list[tuple[str, bytes, str]]:
    """Empaqueta todos los archivos del directorio en el formato que espera la API:
    (filename-con-prefijo-de-directorio, content, content_type).
    SKILL.md va al root; los demas archivos preservan su nombre."""
    files: list[tuple[str, bytes, str]] = []
    for f in sorted(skill_dir.iterdir()):
        if not f.is_file():
            continue
        arcname = f"{skill_dir.name}/{f.name}"
        if f.suffix == ".md":
            ctype = "text/markdown"
        elif f.suffix == ".json":
            ctype = "application/json"
        elif f.suffix in (".yaml", ".yml"):
            ctype = "application/yaml"
        else:
            ctype = "application/octet-stream"
        files.append((arcname, f.read_bytes(), ctype))
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Listar el plan sin ejecutar")
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Cambiar el modelo del agente (ej: claude-haiku-4-5). "
            "Si se omite, se preserva el modelo actual."
        ),
    )
    args = parser.parse_args()

    if not (SYSTEM_PROMPT_PATH.exists()):
        print(f"ERROR: no existe {SYSTEM_PROMPT_PATH}", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()

    # 1. Descubrir skills locales
    repo_skills = discover_repo_skills(REPO_ROOT)
    print(f"Skills en el repo: {len(repo_skills)}")
    for name, path in repo_skills:
        rel = path.relative_to(REPO_ROOT).as_posix()
        print(f"  - {name:42s}  ({rel}/SKILL.md)")
    print()

    # 2. Listar skills del workspace
    print("Listando skills del workspace...")
    existing = list_workspace_custom_skills(client)
    print(f"Custom skills en el workspace: {len(existing)}")
    print()

    # 3. Estado actual del agente
    agent = client.beta.agents.retrieve(agent_id=AGENT_ID)
    print(f"Agente actual:")
    print(f"  id:      {agent.id}")
    print(f"  name:    {agent.name}")
    if args.model and args.model != agent.model.id:
        print(f"  model:   {agent.model.id} -> {args.model} (CAMBIO)")
    else:
        print(f"  model:   {agent.model.id} (speed={agent.model.speed}) — se preserva")
    print(f"  version: {agent.version}")
    print(f"  skills:  {len(agent.skills or [])} attached")
    print()

    # 4. Plan
    operations: list[tuple[str, str, Path, str | None, str]] = []
    for skill_name, skill_dir in repo_skills:
        title = display_title_for(skill_name)
        existing_id = existing.get(title)
        op = "VERSION" if existing_id else "CREATE"
        operations.append((op, skill_name, skill_dir, existing_id, title))

    print("Plan:")
    for op, name, _path, eid, title in operations:
        if op == "VERSION":
            print(f"  VERSION  {title:42s}  (existing {eid})")
        else:
            print(f"  CREATE   {title:42s}  (NEW)")
    print()

    new_system = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    print(f"System prompt nuevo: {len(new_system)} chars (actual: {len(agent.system or '')})")
    print()

    if args.dry_run:
        print("--- DRY RUN — no se hicieron cambios ---")
        return 0

    # 5. Ejecutar
    print("=== EJECUTANDO ===")
    print()
    skill_refs: list[dict] = []
    for op, name, skill_dir, eid, title in operations:
        files = build_skill_files(skill_dir)
        if op == "VERSION":
            print(f"  Versioning {title}... ", end="", flush=True)
            v = client.beta.skills.versions.create(skill_id=eid, files=files)
            print(f"OK (version {v.version})")
            skill_refs.append({"type": "custom", "skill_id": eid, "version": "latest"})
        else:
            print(f"  Creating  {title}... ", end="", flush=True)
            s = client.beta.skills.create(display_title=title, files=files)
            print(f"OK (skill_id={s.id})")
            skill_refs.append({"type": "custom", "skill_id": s.id, "version": "latest"})

    print()
    print(f"Updating agent {AGENT_ID} (current version={agent.version})...")
    update_kwargs: dict = {
        "agent_id": AGENT_ID,
        "version": agent.version,
        "system": new_system,
        "skills": skill_refs,
    }
    if args.model and args.model != agent.model.id:
        update_kwargs["model"] = {"id": args.model}
    updated = client.beta.agents.update(**update_kwargs)
    print(
        f"OK — agent ahora en version {updated.version}, "
        f"con {len(updated.skills or [])} skills, model={updated.model.id}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
