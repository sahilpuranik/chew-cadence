import json
import time
from datetime import datetime
from pathlib import Path

import config

SESSIONS_DIR = Path(__file__).resolve().parent.parent / "sessions"


class SessionLogger:
    def __init__(self, mode, path=None):
        SESSIONS_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = Path(path) if path else SESSIONS_DIR / f"{stamp}_{mode}.jsonl"
        self._f = open(self.path, "w")
        self._write({"type": "meta", "mode": mode, "config": config.as_dict(),
                     "started": datetime.now().isoformat()})

    def _write(self, rec, t=None):
        rec["t"] = time.time() if t is None else t
        self._f.write(json.dumps(rec) + "\n")
        self._f.flush()

    def chew(self, t):
        self._write({"type": "chew"}, t)

    def cpm(self, t, value):
        self._write({"type": "cpm", "cpm": value}, t)

    def cue(self, t):
        self._write({"type": "cue"}, t)

    def state(self, t, state):
        self._write({"type": "state", "state": state}, t)

    def close(self):
        self._f.close()


def load_session(path):
    with open(path) as f:
        return [json.loads(line) for line in f]
