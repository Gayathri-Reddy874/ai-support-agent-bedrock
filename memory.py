import json
import os
import time
import threading

FILE_NAME = "chat_history.json"

# ✅ Simple in-process lock to prevent read-modify-write races on the JSON file
_lock = threading.Lock()


def _load_all():
    if not os.path.exists(FILE_NAME):
        return {}
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # Corrupted/empty file — don't crash the app, start fresh
        return {}


def save_message(table, session_id, role, message):
    with _lock:
        data = _load_all()

        if session_id not in data:
            data[session_id] = []

        data[session_id].append({
            "timestamp": int(time.time()),
            "role": role,
            "message": message
        })

        with open(FILE_NAME, "w") as f:
            json.dump(data, f, indent=4)


def get_history(table, session_id):
    with _lock:
        data = _load_all()
        return data.get(session_id, [])


def get_recent_history(session_id, limit=5):
    """
    Return the last `limit` turns (You+Agent pairs count as separate entries)
    for a session, in chronological order. Used to give the LLM short-term
    conversational context without sending the entire history every call.
    """
    history = get_history(None, session_id)
    if not history:
        return []
    return history[-(limit * 2):]

