#!/usr/bin/env python3
"""Create deterministic skill and portable-plugin ZIPs; never include user runs."""
import argparse
import hashlib
from pathlib import Path
import zipfile


def package(out):
    root = Path(__file__).resolve().parents[1]
    skill = root / "skills" / "podcast-xmind"
    files = sorted(p for p in skill.rglob("*") if p.is_file()
                   and "__pycache__" not in p.parts and p.suffix != ".pyc")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    hashes = []
    for name, plugin in [("podcast-xmind-skill.zip", False), ("podcast-xmind-plugin.zip", True)]:
        target = out / name
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            entries = [(p, "podcast-xmind/" + str(p.relative_to(root if plugin else skill.parent)).replace("\\", "/"))
                       for p in files]
            if not plugin:
                entries = [(p, str(p.relative_to(skill.parent)).replace("\\", "/")) for p in files]
            entries.append((root / "LICENSE", "podcast-xmind/LICENSE"))
            if plugin:
                entries.append((root / "plugin.json", "podcast-xmind/plugin.json"))
            for path, member in sorted(entries, key=lambda pair: pair[1]):
                info = zipfile.ZipInfo(member, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        hashes.append(f"{hashlib.sha256(target.read_bytes()).hexdigest()}  {name}")
    (out / "SHA256SUMS").write_text("\n".join(hashes) + "\n", encoding="utf-8")
    return hashes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("dist"))
    args = parser.parse_args()
    print("\n".join(package(args.out)))
