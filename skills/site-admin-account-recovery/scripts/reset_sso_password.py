#!/usr/bin/env python3
"""Reset one sakyowon SSO account password directly in the SQLite store.

Run ON THE SERVER as the service user, from a FILE (never via a heredoc --
a heredoc occupies stdin and getpass/input raise EOFError):

    sudo -u sakyowon /opt/sakyowon/server/.venv/bin/python /tmp/reset_sso_password.py

It never echoes the password and wipes all sessions so every site logs out.
"""
import getpass
import hashlib
import secrets
import sqlite3
import sys

DB = "/opt/sakyowon/data/sakyowon.db"
ITER = 200_000  # must match PBKDF2_ITER in server/app.py


def main() -> int:
    user = (sys.argv[1] if len(sys.argv) > 1 else input("username: ")).strip()
    if not user:
        print("username required")
        return 1

    pw = getpass.getpass("new password (8+ chars): ")
    if pw != getpass.getpass("again: "):
        print("mismatch - aborted")
        return 1
    if len(pw) < 8:
        print("too short - aborted")
        return 1

    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), ITER).hex()
    stored = f"pbkdf2:{ITER}:{salt}:{digest}"

    conn = sqlite3.connect(DB)
    conn.execute(
        "UPDATE users SET pw=?, role='admin', status='approved',"
        " updated_at=datetime('now') WHERE username=?",
        (stored, user),
    )
    changed = conn.total_changes
    conn.execute("DELETE FROM sessions")  # logs out every site sharing sk_session
    conn.commit()
    conn.close()

    print(f"rows updated: {changed}")
    if changed == 0:
        print("no such username - check: sqlite3 %s 'SELECT username FROM users;'" % DB)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
