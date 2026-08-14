import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "ohaka_meshi.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


SORT_OPTIONS = {
    "date_desc": "eaten_date DESC, id DESC",
    "date_asc": "eaten_date ASC, id DESC",
    "dish_name": "dish_name COLLATE NOCASE ASC, id DESC",
}
DEFAULT_SORT = "date_desc"


def list_entries(q=None, type_filter=None, sort=DEFAULT_SORT):
    conn = get_connection()
    sql = "SELECT * FROM entries WHERE deleted_at IS NULL"
    params = []
    if q:
        sql += " AND (dish_name LIKE ? OR restaurant_name LIKE ? OR location LIKE ? OR comment LIKE ?)"
        like = f"%{q}%"
        params += [like, like, like, like]
    if type_filter == "out":
        sql += " AND is_eating_out = 1"
    elif type_filter == "home":
        sql += " AND is_eating_out = 0"
    sql += " ORDER BY " + SORT_OPTIONS.get(sort, SORT_OPTIONS[DEFAULT_SORT])
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def get_entry(entry_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM entries WHERE id = ? AND deleted_at IS NULL", (entry_id,)
    ).fetchone()
    conn.close()
    return row


def create_entry(data):
    conn = get_connection()
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.execute(
        """INSERT INTO entries
           (dish_name, is_eating_out, restaurant_name, location, reference_url,
            screenshot_filename, comment, eaten_date, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["dish_name"],
            1 if data["is_eating_out"] else 0,
            data.get("restaurant_name") or None,
            data.get("location") or None,
            data.get("reference_url") or None,
            data.get("screenshot_filename") or None,
            data.get("comment") or None,
            data["eaten_date"],
            now,
            now,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_entry(entry_id, data):
    conn = get_connection()
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """UPDATE entries SET
             dish_name = ?, is_eating_out = ?, restaurant_name = ?, location = ?,
             reference_url = ?, screenshot_filename = ?, comment = ?, eaten_date = ?,
             updated_at = ?
           WHERE id = ?""",
        (
            data["dish_name"],
            1 if data["is_eating_out"] else 0,
            data.get("restaurant_name") or None,
            data.get("location") or None,
            data.get("reference_url") or None,
            data.get("screenshot_filename") or None,
            data.get("comment") or None,
            data["eaten_date"],
            now,
            entry_id,
        ),
    )
    conn.commit()
    conn.close()


def soft_delete_entry(entry_id):
    conn = get_connection()
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute("UPDATE entries SET deleted_at = ? WHERE id = ?", (now, entry_id))
    conn.commit()
    conn.close()


def distinct_values(column):
    if column not in ("restaurant_name", "location"):
        raise ValueError(f"invalid column: {column}")
    conn = get_connection()
    rows = conn.execute(
        f"SELECT DISTINCT {column} FROM entries "
        f"WHERE {column} IS NOT NULL AND {column} != '' AND deleted_at IS NULL "
        f"ORDER BY {column} COLLATE NOCASE"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]
