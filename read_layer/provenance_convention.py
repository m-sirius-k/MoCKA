# W-1 read layer: Relay provenance 5-role free_note convention (parser + encoder).
# DC_20260714_001. Non-destructive: new-event application ONLY. This module does not
# modify app.py endpoints, does not rewrite existing events, and does not change schema.
# It provides encode/decode so that NEW events can carry separated provenance in free_note.
import sqlite3

# Five separated roles (D-1). operation_actor stays the event actor; origin_* are additive.
ROLE_KEYS = ["operation_actor", "relay_operator", "origin_author", "origin_source", "origin_url"]

# Keys already used by the existing free_note convention (must not collide).
EXISTING_CONVENTION_KEYS = {
    "who_role", "event_source", "orig_channel", "source", "type",
    "require_human_gate", "session_id",
}


def parse_freenote(fn):
    """Mirror of the existing lightweight 'k=v|k=v' free_note parser."""
    d = {}
    for part in str(fn).split("|"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def encode_roles(roles):
    """Encode the 5 roles into a free_note fragment. Omits keys with None value."""
    return "|".join(f"{k}={roles[k]}" for k in ROLE_KEYS if roles.get(k) is not None)


def decode_roles(fn):
    """Extract the 5 roles from a free_note (missing roles -> None)."""
    d = parse_freenote(fn)
    return {k: d.get(k) for k in ROLE_KEYS}


def augment_free_note(existing_fn, roles):
    """For a NEW event only: append role fragment to an existing free_note, preserving it.
    Never call this against a stored/past event."""
    frag = encode_roles(roles)
    existing = (existing_fn or "").strip()
    if not existing or existing == "N/A":
        return frag
    return existing + "|" + frag if frag else existing


def check_collision(sample_free_notes):
    """Return any collision between ROLE_KEYS and existing convention keys (static + observed)."""
    observed = set()
    for fn in sample_free_notes:
        observed |= set(parse_freenote(fn).keys())
    return {
        "static_collisions": sorted(set(ROLE_KEYS) & EXISTING_CONVENTION_KEYS),
        "observed_collisions": sorted(set(ROLE_KEYS) & observed),
        "distinct_observed_keys": sorted(observed),
    }


if __name__ == "__main__":
    import json, hashlib
    DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"

    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        return h.hexdigest()

    # round-trip
    sample = {"operation_actor": "Claude-opus-4-8", "relay_operator": "human_nsjsiro",
              "origin_author": "chatgpt", "origin_source": "chatgpt",
              "origin_url": "https://chatgpt.com/c/deadbeef"}
    enc = encode_roles(sample)
    dec = decode_roles(enc)
    roundtrip_ok = dec == sample

    # collision + existing-reader compat against REAL production free_notes (read-only)
    h1 = sha(DB)
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    write_rejected = False
    try:
        con.execute("CREATE TABLE _rl_should_fail (x int)")
    except sqlite3.OperationalError:
        write_rejected = True
    rows = [r[0] for r in con.execute(
        "SELECT free_note FROM events WHERE free_note IS NOT NULL AND free_note != '' "
        "ORDER BY rowid DESC LIMIT 200").fetchall()]
    con.close()
    h2 = sha(DB)

    coll = check_collision(rows)
    # existing-reader non-interference: augment real free_notes, ensure originals preserved
    interfere = 0
    for fn in rows[:50]:
        orig = parse_freenote(fn)
        aug = parse_freenote(augment_free_note(fn, sample))
        if any(aug.get(k) != v for k, v in orig.items()):
            interfere += 1
        if any(aug.get(k) != sample[k] for k in ROLE_KEYS):
            interfere += 1

    print(json.dumps({
        "roundtrip_ok": roundtrip_ok,
        "encoded": enc,
        "collision": coll,
        "no_collision": not coll["static_collisions"] and not coll["observed_collisions"],
        "existing_reader_interference_count": interfere,
        "write_rejected": write_rejected,
        "events_db_sha_before": h1,
        "events_db_sha_after": h2,
        "events_db_unchanged": h1 == h2,
    }, ensure_ascii=False, indent=2))
