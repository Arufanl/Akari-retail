"""Plugin Akari Notes & Greeting State.

Menyediakan satu tool kompak `akari_notes` untuk:
1. Menyimpan, mencari, memperbarui, dan merangkum catatan terstruktur (idea, link, note, task) di SQLite.
2. Mengekspor ulang berkas Markdown rapi (`~/.hermes/plugin-data/akari_notes/Akari_Notes.md`) setiap ada perubahan.
3. Mengatur jeda sapaan spontan (`snooze_greeting` / `resume_greeting`).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from plugins.plugin_storage import plugin_data_dir, plugin_db

PLUGIN_NAME = "akari_notes"
VALID_KINDS = ("idea", "link", "note", "task")
VALID_STATUSES = ("open", "done", "archived")

AKARI_NOTES_SCHEMA = {
    "name": "akari_notes",
    "description": (
        "Kelola catatan terstruktur milik Bos (ide proyek, link, catatan umum, calon tugas) "
        "di database terpisah dari memori profil, serta atur jeda sapaan spontan Akari. "
        "Actions: add (simpan baru), list (lihat/filter), search (cari kata kunci), "
        "update (ubah isi/status open/done/archived), remove (hapus), "
        "snooze_greeting (tahan sapaan spontan selama snooze_hours atau sampai snooze_until ISO), "
        "resume_greeting (aktifkan lagi sapaan spontan)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "add",
                    "list",
                    "search",
                    "update",
                    "remove",
                    "snooze_greeting",
                    "resume_greeting",
                ],
                "description": "Aksi yang dijalankan.",
            },
            "note_id": {
                "type": "integer",
                "description": "ID catatan (wajib untuk update dan remove).",
            },
            "kind": {
                "type": "string",
                "enum": ["idea", "link", "note", "task"],
                "description": "Kategori item: idea (ide proyek), link (tautan/URL), note (catatan umum), task (calon tugas).",
            },
            "content": {
                "type": "string",
                "description": "Isi catatan, ide, atau deskripsi tugas.",
            },
            "url": {
                "type": "string",
                "description": "URL tautan (opsional, khusus kind='link' atau catatan bertautan).",
            },
            "tags": {
                "type": "string",
                "description": "Tag opsional dipisah koma (misal: 'pixel-art, game').",
            },
            "status": {
                "type": "string",
                "enum": ["open", "done", "archived"],
                "description": "Status item (open = aktif/belum selesai, done = selesai/sudah dibuka, archived = arsip).",
            },
            "query": {
                "type": "string",
                "description": "Kata kunci pencarian untuk action='search'.",
            },
            "limit": {
                "type": "integer",
                "description": "Batas jumlah hasil (default 20).",
            },
            "snooze_hours": {
                "type": "number",
                "description": "Durasi jeda sapaan spontan dalam jam (misal 8 untuk tidur 8 jam).",
            },
            "snooze_until": {
                "type": "string",
                "description": "Waktu ISO berakhirnya jeda sapaan (misal '2026-11-06T07:00:00+07:00').",
            },
        },
        "required": ["action"],
    },
}


def _now_local() -> datetime:
    return datetime.now().astimezone()


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL DEFAULT 'note',
            content TEXT NOT NULL,
            url TEXT,
            tags TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS greeting_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )


def _export_markdown(conn: sqlite3.Connection) -> None:
    """Render seluruh catatan ke berkas Markdown rapi untuk Obsidian."""
    rows = conn.execute(
        "SELECT id, kind, content, url, tags, status, created_at, updated_at FROM notes ORDER BY id DESC"
    ).fetchall()

    now_str = _now_local().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# Catatan, Ide, Link & Tugas — Akari",
        "",
        f"*Terakhir diperbarui otomatis: {now_str}*",
        "",
    ]

    sections = [
        ("idea", "## 💡 Ide Proyek (`idea`)"),
        ("task", "## ✅ Calon Tugas (`task`)"),
        ("link", "## 🔗 Tautan & Referensi (`link`)"),
        ("note", "## 📝 Catatan Umum (`note`)"),
    ]

    for kind_key, heading in sections:
        lines.append(heading)
        items = [r for r in rows if r[1] == kind_key]
        if not items:
            lines.append("- *(Belum ada item)*")
            lines.append("")
            continue
        for nid, _k, content, url, tags, status, created_at, _updated_at in items:
            checkbox = "[x]" if status == "done" else ("[-]" if status == "archived" else "[ ]")
            date_short = str(created_at)[:16].replace("T", " ")
            line = f"- {checkbox} **#{nid}** ({date_short}): {content.strip()}"
            if url:
                line += f" — {url.strip()}"
            if tags:
                line += f" `[tags: {tags.strip()}]`"
            lines.append(line)
        lines.append("")

    md_path = plugin_data_dir(PLUGIN_NAME) / "Akari_Notes.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")


def _row_to_dict(row: tuple) -> dict[str, Any]:
    return {
        "id": row[0],
        "kind": row[1],
        "content": row[2],
        "url": row[3],
        "tags": row[4],
        "status": row[5],
        "created_at": row[6],
        "updated_at": row[7],
    }


def handle_akari_notes(args: dict[str, Any], **kwargs: Any) -> str:
    action = str(args.get("action") or "").strip().lower()
    now = _now_local()
    now_iso = now.isoformat(timespec="seconds")

    conn = plugin_db(PLUGIN_NAME, "akari_notes.db")
    try:
        with conn:
            _init_db(conn)

            if action == "add":
                content = str(args.get("content") or "").strip()
                if not content:
                    return json.dumps({"success": False, "error": "Parameter 'content' wajib diisi."}, ensure_ascii=False)
                kind = str(args.get("kind") or "note").strip().lower()
                if kind not in VALID_KINDS:
                    kind = "note"
                url = str(args.get("url") or "").strip() or None
                tags = str(args.get("tags") or "").strip() or None
                status = str(args.get("status") or "open").strip().lower()
                if status not in VALID_STATUSES:
                    status = "open"

                cur = conn.execute(
                    "INSERT INTO notes (kind, content, url, tags, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (kind, content, url, tags, status, now_iso, now_iso),
                )
                note_id = cur.lastrowid
                _export_markdown(conn)
                return json.dumps(
                    {
                        "success": True,
                        "action": "add",
                        "note": {
                            "id": note_id,
                            "kind": kind,
                            "content": content,
                            "url": url,
                            "tags": tags,
                            "status": status,
                            "created_at": now_iso,
                        },
                    },
                    ensure_ascii=False,
                )

            if action == "list":
                kind_filter = str(args.get("kind") or "").strip().lower()
                status_filter = str(args.get("status") or "").strip().lower()
                limit = max(1, min(100, int(args.get("limit") or 20)))

                sql = "SELECT id, kind, content, url, tags, status, created_at, updated_at FROM notes WHERE 1=1"
                params: list[Any] = []
                if kind_filter in VALID_KINDS:
                    sql += " AND kind = ?"
                    params.append(kind_filter)
                if status_filter in VALID_STATUSES:
                    sql += " AND status = ?"
                    params.append(status_filter)
                sql += " ORDER BY id DESC LIMIT ?"
                params.append(limit)

                rows = conn.execute(sql, params).fetchall()
                return json.dumps(
                    {"success": True, "count": len(rows), "notes": [_row_to_dict(r) for r in rows]},
                    ensure_ascii=False,
                )

            if action == "search":
                query = str(args.get("query") or args.get("content") or "").strip()
                if not query:
                    return json.dumps({"success": False, "error": "Parameter 'query' wajib diisi."}, ensure_ascii=False)
                limit = max(1, min(100, int(args.get("limit") or 20)))
                like_pat = f"%{query}%"
                rows = conn.execute(
                    """SELECT id, kind, content, url, tags, status, created_at, updated_at
                       FROM notes
                       WHERE content LIKE ? OR IFNULL(url, '') LIKE ? OR IFNULL(tags, '') LIKE ?
                       ORDER BY id DESC LIMIT ?""",
                    (like_pat, like_pat, like_pat, limit),
                ).fetchall()
                return json.dumps(
                    {"success": True, "query": query, "count": len(rows), "notes": [_row_to_dict(r) for r in rows]},
                    ensure_ascii=False,
                )

            if action == "update":
                note_id = args.get("note_id")
                if note_id is None:
                    return json.dumps({"success": False, "error": "Parameter 'note_id' wajib diisi."}, ensure_ascii=False)
                row = conn.execute(
                    "SELECT id, kind, content, url, tags, status, created_at, updated_at FROM notes WHERE id = ?",
                    (int(note_id),),
                ).fetchone()
                if not row:
                    return json.dumps({"success": False, "error": f"Catatan #{note_id} tidak ditemukan."}, ensure_ascii=False)

                kind = str(args.get("kind") or row[1]).strip().lower()
                if kind not in VALID_KINDS:
                    kind = row[1]
                content = str(args.get("content") or row[2]).strip()
                url = str(args["url"]).strip() if "url" in args and args["url"] is not None else row[3]
                tags = str(args["tags"]).strip() if "tags" in args and args["tags"] is not None else row[4]
                status = str(args.get("status") or row[5]).strip().lower()
                if status not in VALID_STATUSES:
                    status = row[5]

                conn.execute(
                    "UPDATE notes SET kind = ?, content = ?, url = ?, tags = ?, status = ?, updated_at = ? WHERE id = ?",
                    (kind, content, url, tags, status, now_iso, int(note_id)),
                )
                _export_markdown(conn)
                updated = conn.execute(
                    "SELECT id, kind, content, url, tags, status, created_at, updated_at FROM notes WHERE id = ?",
                    (int(note_id),),
                ).fetchone()
                return json.dumps({"success": True, "action": "update", "note": _row_to_dict(updated)}, ensure_ascii=False)

            if action == "remove":
                note_id = args.get("note_id")
                if note_id is None:
                    return json.dumps({"success": False, "error": "Parameter 'note_id' wajib diisi."}, ensure_ascii=False)
                cur = conn.execute("DELETE FROM notes WHERE id = ?", (int(note_id),))
                _export_markdown(conn)
                return json.dumps(
                    {"success": cur.rowcount > 0, "action": "remove", "deleted_id": int(note_id)},
                    ensure_ascii=False,
                )

            if action == "snooze_greeting":
                until_str = str(args.get("snooze_until") or "").strip()
                hours = args.get("snooze_hours")
                if not until_str:
                    dur_h = float(hours) if hours is not None else 8.0
                    until_dt = now + timedelta(hours=max(0.5, min(168.0, dur_h)))
                    until_str = until_dt.isoformat(timespec="seconds")
                conn.execute(
                    "INSERT OR REPLACE INTO greeting_state (key, value, updated_at) VALUES ('pause_until', ?, ?)",
                    (until_str, now_iso),
                )
                return json.dumps(
                    {"success": True, "action": "snooze_greeting", "pause_until": until_str},
                    ensure_ascii=False,
                )

            if action == "resume_greeting":
                conn.execute("DELETE FROM greeting_state WHERE key = 'pause_until'")
                return json.dumps(
                    {"success": True, "action": "resume_greeting", "pause_until": None},
                    ensure_ascii=False,
                )

            return json.dumps({"success": False, "error": f"Action tidak dikenal: {action!r}"}, ensure_ascii=False)
    finally:
        conn.close()


def register(ctx: Any) -> None:
    ctx.register_tool(
        name="akari_notes",
        toolset="akari_notes",
        schema=AKARI_NOTES_SCHEMA,
        handler=handle_akari_notes,
        description="Simpan dan kelola catatan, ide, link, calon tugas, serta jeda sapaan spontan Akari.",
        emoji="📝",
    )
