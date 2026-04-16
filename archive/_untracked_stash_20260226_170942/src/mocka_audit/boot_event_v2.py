from audit_writer import AuditWriter

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"


def write_boot_event(entry_path: str) -> None:
    writer = AuditWriter(DB_PATH)
    ev = writer.write_payload({
        "type": "boot_event",
        "entry_path": entry_path,
    }, note="boot_event_v2", commit=True)

    print(f"BOOT_EVENT_CONNECTED: {ev['event_id']}")


if __name__ == "__main__":
    write_boot_event("manual_boot_v2")
