"""semantic/synonym.py — SynonymDictionary: 同義語辞書"""
from __future__ import annotations
from command_index.db import CommandIndexDB

_BUILTIN_SYNONYMS = [
    # save / backup / snapshot
    ("save",        "backup",       "storage"),
    ("save",        "snapshot",     "storage"),
    ("save",        "archive",      "storage"),
    ("save",        "checkpoint",   "storage"),
    ("backup",      "snapshot",     "storage"),
    ("backup",      "archive",      "storage"),
    # publish / deploy / release
    ("publish",     "deploy",       "publish"),
    ("publish",     "release",      "publish"),
    ("publish",     "distribute",   "publish"),
    ("deploy",      "release",      "publish"),
    # check / validate / verify
    ("check",       "validate",     "quality"),
    ("check",       "verify",       "quality"),
    ("check",       "audit",        "quality"),
    ("validate",    "verify",       "quality"),
    # search / find / query / lookup
    ("search",      "find",         "search"),
    ("search",      "query",        "search"),
    ("search",      "lookup",       "search"),
    # seo / optimize / rank
    ("seo",         "optimize",     "seo"),
    ("seo",         "rank",         "seo"),
    ("seo",         "score",        "seo"),
    # content / article / post
    ("content",     "article",      "content"),
    ("content",     "post",         "content"),
    ("content",     "blog",         "content"),
    # run / execute / perform
    ("run",         "execute",      "execution"),
    ("run",         "perform",      "execution"),
    ("execute",     "perform",      "execution"),
    # report / summary / overview
    ("report",      "summary",      "report"),
    ("report",      "overview",     "report"),
    ("summary",     "overview",     "report"),
    # context / memory / state
    ("context",     "memory",       "context"),
    ("context",     "state",        "context"),
    ("memory",      "state",        "context"),
    # resume / restore / recover
    ("resume",      "restore",      "resume"),
    ("resume",      "recover",      "resume"),
    ("restore",     "recover",      "resume"),
]


class SynonymDictionary:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._seed()

    def _seed(self) -> None:
        existing = self._db.execute("SELECT word, synonym FROM synonyms")
        existing_pairs = {(r["word"], r["synonym"]) for r in existing}
        to_insert = []
        for word, synonym, category in _BUILTIN_SYNONYMS:
            if (word, synonym) not in existing_pairs:
                to_insert.append((word, synonym, category))
            if (synonym, word) not in existing_pairs:
                to_insert.append((synonym, word, category))
        if to_insert:
            self._db.executemany_write(
                "INSERT OR IGNORE INTO synonyms(word,synonym,category) VALUES(?,?,?)",
                to_insert
            )

    def get_synonyms(self, word: str) -> list[str]:
        rows = self._db.execute(
            "SELECT synonym FROM synonyms WHERE word=?", (word.lower(),)
        )
        return [r["synonym"] for r in rows]

    def expand(self, words: list[str]) -> list[str]:
        expanded = list(words)
        seen = set(w.lower() for w in words)
        for word in words:
            for syn in self.get_synonyms(word.lower()):
                if syn not in seen:
                    expanded.append(syn)
                    seen.add(syn)
        return expanded

    def add(self, word: str, synonym: str, category: str = "") -> None:
        self._db.execute_write(
            "INSERT OR IGNORE INTO synonyms(word,synonym,category) VALUES(?,?,?)",
            (word.lower(), synonym.lower(), category)
        )
        self._db.execute_write(
            "INSERT OR IGNORE INTO synonyms(word,synonym,category) VALUES(?,?,?)",
            (synonym.lower(), word.lower(), category)
        )
