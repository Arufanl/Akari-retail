#!/usr/bin/env python3
"""Wake-gate & konteks sapaan spontan adaptif Akari (PRD Bagian 7).

Jika kondisi sapaan tidak terpenuhi (sedang mode jeda/tidur, Bos baru saja aktif mengobrol
dalam 2 jam terakhir, atau sudah ada >= 2 sapaan beruntun tanpa balasan Bos), skrip ini
mencetak baris terakhir `{"wakeAgent": false}` sehingga scheduler melewati pemanggilan LLM
(0 token terpakai).

Jika lolos, skrip ini mencetak ringkasan konteks (waktu saat ini, status sapaan terakhir,
dan 1 item ide/tugas/catatan terbuka opsional) untuk disisipkan ke prompt cron.
"""

from __future__ import annotations

import json
import os
import random
import sqlite3
import time
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))).resolve()
NOTES_DB = HERMES_HOME / "plugin-data" / "akari_notes" / "akari_notes.db"
STATE_DB = HERMES_HOME / "state.db"
EXEC_DB = HERMES_HOME / "cron" / "executions.db"
JOBS_JSON = HERMES_HOME / "cron" / "jobs.json"

RECENT_CHAT_COOLDOWN_SECS = 2 * 3600  # 2 jam setelah chat terakhir tidak perlu sapaan spontan
MAX_UNANSWERED_GREETINGS = 2          # Maksimal 2 sapaan spontan beruntun (1 awal + 1 susulan)


def _skip(reason: str) -> None:
    print(f"Gate skip: {reason}")
    print(json.dumps({"wakeAgent": False}))


def _get_pause_until() -> datetime | None:
    if not NOTES_DB.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{NOTES_DB}?mode=ro", uri=True, timeout=5.0)
        try:
            row = conn.execute("SELECT value FROM greeting_state WHERE key = 'pause_until'").fetchone()
            if row and row[0]:
                dt = datetime.fromisoformat(str(row[0]))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                return dt
        finally:
            conn.close()
    except Exception:
        return None
    return None


def _get_last_user_whatsapp_ts() -> float:
    if not STATE_DB.exists():
        return 0.0
    try:
        conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True, timeout=5.0)
        try:
            row = conn.execute(
                """SELECT MAX(m.timestamp)
                   FROM messages m
                   JOIN sessions s ON m.session_id = s.id
                   WHERE s.source = 'whatsapp' AND m.role = 'user'"""
            ).fetchone()
            return float(row[0]) if row and row[0] is not None else 0.0
        finally:
            conn.close()
    except Exception:
        return 0.0


def _get_greeting_job_ids() -> list[str]:
    if not JOBS_JSON.exists():
        return []
    try:
        data = json.loads(JOBS_JSON.read_text(encoding="utf-8"))
        ids = []
        for job in data.get("jobs", []):
            name = str(job.get("name") or "").lower()
            script = str(job.get("script") or "")
            if "sapaan" in name or "akari_greeting_gate.py" in script:
                if job.get("id"):
                    ids.append(str(job["id"]))
        return ids
    except Exception:
        return []


def _count_unanswered_greetings(last_user_ts: float, job_ids: list[str]) -> int:
    if not job_ids or not EXEC_DB.exists():
        return 0
    try:
        conn = sqlite3.connect(f"file:{EXEC_DB}?mode=ro", uri=True, timeout=5.0)
        try:
            placeholders = ",".join("?" for _ in job_ids)
            rows = conn.execute(
                f"""SELECT finished_at FROM executions
                    WHERE job_id IN ({placeholders})
                      AND status = 'completed'
                      AND delivery_outcome = 'delivered'
                    ORDER BY finished_at DESC LIMIT 5""",
                job_ids,
            ).fetchall()
            count = 0
            for (fin_str,) in rows:
                if not fin_str:
                    continue
                try:
                    fin_ts = datetime.fromisoformat(str(fin_str)).timestamp()
                    if fin_ts > last_user_ts:
                        count += 1
                except Exception:
                    continue
            return count
        finally:
            conn.close()
    except Exception:
        return 0


def _pick_open_note() -> dict | None:
    if not NOTES_DB.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{NOTES_DB}?mode=ro", uri=True, timeout=5.0)
        try:
            rows = conn.execute(
                """SELECT id, kind, content, url, created_at
                   FROM notes
                   WHERE status = 'open'
                   ORDER BY id DESC LIMIT 10"""
            ).fetchall()
            if not rows:
                return None
            picked = random.choice(rows)
            return {
                "id": picked[0],
                "kind": picked[1],
                "content": picked[2],
                "url": picked[3],
                "created_at": picked[4],
            }
        finally:
            conn.close()
    except Exception:
        return None


def main() -> None:
    now = datetime.now().astimezone()
    now_ts = time.time()

    # 1. Cek apakah sedang dalam masa jeda sapaan (snooze)
    pause_until = _get_pause_until()
    if pause_until is not None and now < pause_until:
        _skip(f"Masih dalam masa jeda sapaan sampai {pause_until.isoformat()}")
        return

    # 2. Cek kapan terakhir Bos mengirim pesan WhatsApp
    last_user_ts = _get_last_user_whatsapp_ts()
    if last_user_ts > 0 and (now_ts - last_user_ts) < RECENT_CHAT_COOLDOWN_SECS:
        mins_ago = int((now_ts - last_user_ts) / 60)
        _skip(f"Bos baru saja aktif mengobrol {mins_ago} menit lalu (< 120 menit)")
        return

    # 3. Cek berapa sapaan spontan yang belum dibalas sejak pesan terakhir Bos
    greeting_ids = _get_greeting_job_ids()
    unanswered = _count_unanswered_greetings(last_user_ts, greeting_ids)
    if unanswered >= MAX_UNANSWERED_GREETINGS:
        _skip(f"Sudah ada {unanswered} sapaan spontan beruntun yang belum dibalas Bos")
        return

    # Lolos gate! Susun konteks untuk membantu Akari menyapa dengan hangat & bervariasi
    hour = now.hour
    if 5 <= hour < 11:
        suasana = "pagi"
    elif 11 <= hour < 15:
        suasana = "siang"
    elif 15 <= hour < 18:
        suasana = "sore"
    else:
        suasana = "malam"

    lines = [
        f"Waktu lokal: {now.strftime('%Y-%m-%d %H:%M %Z')} (suasana {suasana}).",
        f"Status sapaan: {'Sapaan pertama' if unanswered == 0 else 'Sapaan susulan ke-2 (sapaan sebelumnya belum sempat dibalas Bos)'}.",
    ]
    if last_user_ts > 0:
        hours_since = round((now_ts - last_user_ts) / 3600.0, 1)
        lines.append(f"Jeda sejak pesan terakhir Bos: sekitar {hours_since} jam yang lalu.")

    open_note = _pick_open_note()
    if open_note and unanswered == 0:
        lines.append(
            f"Opsional (boleh disinggung ringan jika pas, tidak wajib): Bos punya catatan terbuka "
            f"[{open_note['kind']} #{open_note['id']}]: \"{open_note['content']}\""
        )

    print("\n".join(lines))
    print(json.dumps({"wakeAgent": True}))


if __name__ == "__main__":
    main()
