from sqlalchemy import text
from datetime import datetime

def log_action(db, username, action, target="", detail="", ip=""):
    """Record an operation log entry (caller must commit)"""
    db.execute(
        text("INSERT INTO operation_logs (username, action, target, detail, ip, created_at) VALUES (:u, :a, :t, :d, :i, :c)"),
        {"u": username, "a": action, "t": target, "d": detail, "i": ip, "c": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    )
