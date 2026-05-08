"""
test_agent_with_image.py

Smoke test del Managed Agent con una imagen de catalogo.

Flujo:
  1. Upload de la imagen via Files API
  2. Crea una sesion contra el agente con la imagen mounteada en /workspace/page.jpg
  3. Manda un kickoff message indicando cadena/folder
  4. Streamea los eventos en vivo (text, tool calls, status)
  5. Captura el output del agente y lo guarda en scripts/output/<timestamp>.md

Uso:
    ANTHROPIC_API_KEY=sk-ant-... python scripts/test_agent_with_image.py <ruta-imagen> [opciones]

    --cadena COTO            Nombre de la cadena (default: COTO)
    --folder "..."           Nombre del folder (default: extraido del nombre del archivo)
    --vigencia "..."         Vigencia del folder (opcional)
    --keep-session           No archivar la sesion al terminar
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_ID = "agent_011CaXriThLi9RRbcMBHaCrC"
ENVIRONMENT_ID = "env_018oUWhZLLodCBvLD7Gu7jaY"
OUTPUT_DIR = REPO_ROOT / "scripts" / "output"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path, help="Ruta a la imagen del catalogo")
    parser.add_argument("--cadena", default="COTO")
    parser.add_argument("--folder", default=None, help="Nombre del folder (default: nombre del archivo)")
    parser.add_argument("--vigencia", default=None, help="Vigencia del folder (ej: '10-13 enero 2026')")
    parser.add_argument("--keep-session", action="store_true")
    args = parser.parse_args()

    if not args.image.exists():
        print(f"ERROR: no existe {args.image}", file=sys.stderr)
        return 1

    folder_name = args.folder or args.image.stem
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_stem = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{args.image.stem}"

    client = anthropic.Anthropic()

    # 1. Upload
    print(f"[1/5] Uploading {args.image.name} ({args.image.stat().st_size:,} bytes)...")
    with args.image.open("rb") as f:
        uploaded = client.beta.files.upload(file=f, purpose="agent")
    print(f"      file_id = {uploaded.id}")

    # 2. Create session
    mount_path = f"/workspace/{args.image.name}"
    print(f"[2/5] Creating session against {AGENT_ID}, mount={mount_path}...")
    session = client.beta.sessions.create(
        agent={"type": "agent", "id": AGENT_ID},
        environment_id=ENVIRONMENT_ID,
        title=f"Smoke test post-v3 — {args.image.name}",
        resources=[{
            "type": "file",
            "file_id": uploaded.id,
            "mount_path": mount_path,
        }],
    )
    print(f"      session_id = {session.id}  (status: {session.status})")

    # 3. Stream-first, then send
    print(f"[3/5] Opening event stream...")
    stream = client.beta.sessions.events.stream(session_id=session.id)

    # 4. Kickoff message
    kickoff_lines = [
        f"Procesa la pagina del catalogo que esta en {mount_path}.",
        f"Cadena: {args.cadena}",
        f"Folder: {folder_name}",
    ]
    if args.vigencia:
        kickoff_lines.append(f"Vigencia: {args.vigencia}")
    kickoff_lines.append(
        "Devolveme el JSON con todos los productos visibles, segun el schema canonico de las skills."
    )
    kickoff = "\n".join(kickoff_lines)

    print(f"[4/5] Enviando kickoff...")
    print(f"--- kickoff ---\n{kickoff}\n---------------")
    client.beta.sessions.events.send(
        session_id=session.id,
        events=[{
            "type": "user.message",
            "content": [{"type": "text", "text": kickoff}],
        }],
    )

    # 5. Consume events
    print(f"[5/5] Streameando eventos (Ctrl+C para abortar)...\n")
    agent_text_chunks: list[str] = []
    tool_use_count = 0
    thinking_count = 0
    started_at = time.monotonic()

    for event in stream:
        etype = event.type

        if etype == "agent.message":
            for block in event.content:
                if block.type == "text":
                    text = block.text
                    agent_text_chunks.append(text)
                    sys.stdout.write(text)
                    sys.stdout.flush()
            sys.stdout.write("\n")

        elif etype == "agent.thinking":
            thinking_count += 1
            sys.stdout.write(".")  # progress dot per thinking block
            sys.stdout.flush()

        elif etype in ("agent.tool_use", "agent.mcp_tool_use", "agent.custom_tool_use"):
            tool_use_count += 1
            name = getattr(event, "tool_name", None) or getattr(event, "name", "?")
            inp = getattr(event, "input", {})
            inp_short = json.dumps(inp, default=str)[:120]
            print(f"\n[tool_use #{tool_use_count}] {name}({inp_short})")

        elif etype == "session.status_running":
            print(f"\n[status] running")

        elif etype == "session.status_idle":
            stop = getattr(event, "stop_reason", None)
            stop_type = getattr(stop, "type", None) if stop else None
            print(f"\n[status] idle (stop_reason={stop_type})")
            if stop_type and stop_type != "requires_action":
                break

        elif etype == "session.status_terminated":
            print(f"\n[status] terminated")
            break

        elif etype == "session.error":
            err = getattr(event, "error", None)
            print(f"\n[ERROR] {err}")

    elapsed = time.monotonic() - started_at

    # Save output
    full_text = "".join(agent_text_chunks)
    out_path = OUTPUT_DIR / f"{out_stem}.md"
    out_path.write_text(
        f"# Test output — {args.image.name}\n\n"
        f"- Agent: `{AGENT_ID}`\n"
        f"- Session: `{session.id}`\n"
        f"- Image file_id: `{uploaded.id}`\n"
        f"- Mounted at: `{mount_path}`\n"
        f"- Cadena: {args.cadena}\n"
        f"- Folder: {folder_name}\n"
        f"- Vigencia: {args.vigencia or '(no provista)'}\n"
        f"- Tool calls: {tool_use_count}\n"
        f"- Thinking blocks: {thinking_count}\n"
        f"- Elapsed: {elapsed:.1f}s\n\n"
        f"---\n\n## Output del agente\n\n{full_text}\n",
        encoding="utf-8",
    )
    print(f"\n\n=== resumen ===")
    print(f"Tool calls:      {tool_use_count}")
    print(f"Thinking blocks: {thinking_count}")
    print(f"Output chars:    {len(full_text)}")
    print(f"Tiempo:          {elapsed:.1f}s")
    print(f"Guardado en:     {out_path}")

    if not args.keep_session:
        print(f"Archivando session {session.id}...")
        try:
            client.beta.sessions.archive(session_id=session.id)
            print("OK")
        except Exception as e:
            print(f"WARN: no pude archivar la sesion: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
