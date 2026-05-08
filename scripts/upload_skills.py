"""
upload_skills.py

Re-sube selectivamente las skills que cambiaron al workspace de Anthropic, sin
tocar las que no cambian (a diferencia de update_managed_agent.py que versiona
las 12).

Cada skill nombrada se versiona con `client.beta.skills.versions.create`. El
agente referencia las skills como `version: 'latest'`, por lo que las nuevas
versiones se aplican automáticamente sin modificar el agente.

Uso:
    ANTHROPIC_API_KEY=sk-ant-... python scripts/upload_skills.py \
        --skills extracting-products,handling-closed-brand-categories,flagging-for-review,building-sku-description \
        --update-system

    --skills name1,name2     Lista CSV de skill names (subdirectorios de skills/core/ o skills/chains/).
    --update-system          También reemplaza agent.system con agent/system_prompt.md.
    --dry-run                Listar el plan sin hacer ningún POST/PATCH.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_ID = "agent_011CaXriThLi9RRbcMBHaCrC"
SYSTEM_PROMPT_PATH = REPO_ROOT / "agent" / "system_prompt.md"


def find_skill_dir(skill_name: str) -> Path | None:
    for base in (REPO_ROOT / "skills" / "core", REPO_ROOT / "skills" / "chains"):
        candidate = base / skill_name
        if (candidate / "SKILL.md").exists():
            return candidate
    return None


def display_title_for(skill_name: str) -> str:
    return skill_name.replace("-", " ").title()


def list_workspace_custom_skills(client: anthropic.Anthropic) -> dict[str, str]:
    out: dict[str, str] = {}
    for s in client.beta.skills.list():
        if getattr(s, "source", None) != "anthropic":
            out[s.display_title] = s.id
    return out


def build_skill_files(skill_dir: Path) -> list[tuple[str, bytes, str]]:
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
    parser.add_argument("--skills", required=True, help="CSV de skill names a versionar")
    parser.add_argument("--update-system", action="store_true", help="Reemplazar agent.system con agent/system_prompt.md")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    skill_names = [s.strip() for s in args.skills.split(",") if s.strip()]
    if not skill_names:
        print("ERROR: --skills vacío", file=sys.stderr)
        return 1

    # Resolver paths
    resolved: list[tuple[str, Path, str]] = []
    for name in skill_names:
        skill_dir = find_skill_dir(name)
        if skill_dir is None:
            print(f"ERROR: no encontré skills/core/{name}/SKILL.md ni skills/chains/{name}/SKILL.md", file=sys.stderr)
            return 1
        title = display_title_for(name)
        resolved.append((name, skill_dir, title))

    if args.update_system and not SYSTEM_PROMPT_PATH.exists():
        print(f"ERROR: no existe {SYSTEM_PROMPT_PATH}", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()

    print(f"Listando skills del workspace...")
    existing = list_workspace_custom_skills(client)
    print(f"Custom skills en el workspace: {len(existing)}")
    print()

    # VERSION si la skill ya existe en el workspace, CREATE si es nueva
    plan: list[tuple[str, str, Path, str, str | None]] = []
    for name, skill_dir, title in resolved:
        eid = existing.get(title)
        op = "VERSION" if eid else "CREATE"
        plan.append((op, name, skill_dir, title, eid))

    print("Plan:")
    for op, _name, _path, title, eid in plan:
        if op == "VERSION":
            print(f"  VERSION  {title:42s}  (skill_id={eid})")
        else:
            print(f"  CREATE   {title:42s}  (NEW)")
    if args.update_system:
        new_system = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        print(f"  SYSTEM   reemplazar agent.system ({len(new_system)} chars)")
        if any(op == "CREATE" for op, *_ in plan):
            print(f"           + agregar las nuevas al array agent.skills")
    print()

    if args.dry_run:
        print("--- DRY RUN — no se hicieron cambios ---")
        return 0

    print("=== EJECUTANDO ===")
    print()

    created_refs: list[dict] = []
    for op, name, skill_dir, title, eid in plan:
        files = build_skill_files(skill_dir)
        if op == "VERSION":
            print(f"  Versioning {title}... ", end="", flush=True)
            v = client.beta.skills.versions.create(skill_id=eid, files=files)
            print(f"OK (version {v.version})")
        else:
            print(f"  Creating  {title}... ", end="", flush=True)
            s = client.beta.skills.create(display_title=title, files=files)
            print(f"OK (skill_id={s.id})")
            created_refs.append({"type": "custom", "skill_id": s.id, "version": "latest"})

    needs_agent_update = args.update_system or created_refs
    if needs_agent_update:
        print()
        agent = client.beta.agents.retrieve(agent_id=AGENT_ID)
        # Preservar refs existentes + agregar las recién creadas
        skill_refs = [
            {"type": "custom", "skill_id": s.skill_id, "version": s.version}
            for s in (agent.skills or [])
        ]
        skill_refs.extend(created_refs)
        kwargs: dict = {"agent_id": AGENT_ID, "version": agent.version, "skills": skill_refs}
        if args.update_system:
            new_system = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
            kwargs["system"] = new_system
            print(f"Updating agent.system ({len(new_system)} chars) + {len(skill_refs)} skill refs ({len(created_refs)} new)...")
        else:
            print(f"Updating agent.skills (+{len(created_refs)} new)...")
        updated = client.beta.agents.update(**kwargs)
        print(f"OK — agent ahora en version {updated.version} con {len(updated.skills or [])} skills")

    return 0


if __name__ == "__main__":
    sys.exit(main())
