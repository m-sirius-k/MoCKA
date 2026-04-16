import hashlib
import os
import zipfile


FIXED_DT = (2026, 3, 2, 0, 0, 0)


def iter_files(root_dir: str):
    items = []
    for base, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for fn in files:
            if fn.endswith(".zip"):
                continue
            full = os.path.join(base, fn)
            rel = os.path.relpath(full, root_dir)
            items.append((rel.replace("\\", "/"), full))
    items.sort(key=lambda x: x[0])
    return items


def write_zip(root_dir: str, zip_path: str) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as z:
        for rel, full in iter_files(root_dir):
            zi = zipfile.ZipInfo(rel, date_time=FIXED_DT)
            zi.compress_type = zipfile.ZIP_STORED
            zi.create_system = 0
            with open(full, "rb") as f:
                data = f.read()
            z.writestr(zi, data)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    zip_name = "verify_pack_v3.zip"
    zip_path = os.path.join(here, zip_name)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    write_zip(here, zip_path)
    digest = sha256_file(zip_path)

    out_path = os.path.join(here, "ZIP_SHA256.txt")
    with open(out_path, "w", encoding="ascii", newline="\n") as f:
        f.write(digest + "\n")

    print("zip: " + zip_name)
    print("sha256: " + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
