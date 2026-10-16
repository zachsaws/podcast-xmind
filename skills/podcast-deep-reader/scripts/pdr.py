#!/usr/bin/env python3
"""Offline transcript preparation and structural evidence audit. Python 3.10+."""
import argparse
import hashlib
import html
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

VERSION = "0.1.0"
MAX_SEGMENT = 4000
STAMP = r"(?:\d{1,3}:)?\d{2}:\d{2}(?:[.,]\d{1,3})?"
TIMING = re.compile(rf"^\s*({STAMP})\s*-->\s*({STAMP})(?:\s+.*)?$")
PREFIX = re.compile(rf"^\[({STAMP})\]\s*")
LABEL = re.compile(r"^(?:\*\*)?([^:：\n]{1,60}?)(?:\*\*)?\s*[:：]\s*(?:\*\*)?\s*")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def segment_digest(segments):
    return digest(json.dumps(segments, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def canonical(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def seconds(value):
    parts = value.replace(",", ".").split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"Invalid timestamp: {value}")
    values = [float(p) for p in parts]
    if not all(math.isfinite(n) and n >= 0 for n in values):
        raise ValueError(f"Invalid timestamp: {value}")
    if values[-1] >= 60 or (len(values) == 3 and values[-2] >= 60):
        raise ValueError(f"Invalid timestamp: {value}")
    return sum(n * 60 ** i for i, n in enumerate(reversed(values)))


def label(text):
    """Conservative explicit 'Name: text' syntax; labels are never identities."""
    m = LABEL.match(text)
    if m and not re.search(r"[/.#\[\]]", m[1]) and not m[1].strip().isdigit():
        return m[1].strip(" *"), text[m.end():].strip()
    return None, text


def clean_caption(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def parse_subtitles(text, vtt=False):
    result = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if vtt and (line.startswith("WEBVTT") or line.startswith("NOTE")
                    or line in ("STYLE", "REGION")):
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            continue
        # Optional SRT number or VTT cue identifier.
        if not TIMING.match(line) and i + 1 < len(lines) and TIMING.match(lines[i + 1]):
            i += 1
            line = lines[i].strip()
        match = TIMING.match(line)
        if not match:
            raise ValueError(f"Unparsed subtitle content at line {i + 1}: {line[:80]}")
        start, end = seconds(match[1]), seconds(match[2])
        if end < start:
            raise ValueError(f"Reversed cue at line {i + 1}")
        first = i + 1
        i += 1
        body = []
        while i < len(lines) and lines[i].strip():
            if "-->" in lines[i]:
                raise ValueError(f"Missing cue separator at line {i + 1}")
            body.append(lines[i])
            i += 1
        if not body:
            raise ValueError(f"Empty cue at line {first}")
        joined = "\n".join(body)
        voices = list(re.finditer(r"<v(?:\.[^\s>]*)?\s+([^>]+)>", joined))
        if voices:
            if clean_caption(joined[:voices[0].start()]):
                raise ValueError(f"Unlabelled text before voice tag at line {first}")
            for index, voice in enumerate(voices):
                stop = voices[index + 1].start() if index + 1 < len(voices) else len(joined)
                content = clean_caption(joined[voice.end():stop])
                if content:
                    result.append(dict(text=content, speaker=html.unescape(voice[1]).strip(),
                                       start=start, end=end, line_start=first, line_end=i))
        else:
            # Explicit labels on separate cue lines represent separate turns.
            turns = []
            for row in body:
                speaker, content = label(clean_caption(row))
                if speaker is not None or not turns:
                    turns.append([speaker, content])
                else:
                    turns[-1][1] += "\n" + content
            for speaker, content in turns:
                if content:
                    result.append(dict(text=content, speaker=speaker, start=start, end=end,
                                       line_start=first, line_end=i))
    return result


def parse_plain(text):
    result = []
    current = None
    for number, raw in enumerate(text.splitlines(), 1):
        row = raw.strip()
        if not row:
            current = None
            continue
        stamp = PREFIX.match(row)
        start = seconds(stamp[1]) if stamp else None
        if stamp:
            row = row[stamp.end():]
        speaker, content = label(row)
        if not content:
            raise ValueError(f"Empty labelled paragraph at line {number}")
        if current is None or speaker is not None or stamp is not None:
            current = dict(text=content, speaker=speaker, start=start, end=None,
                           line_start=number, line_end=number)
            result.append(current)
        else:
            current["text"] += "\n" + content
            current["line_end"] = number
    return result


def parse_json(text):
    data = json.loads(text)
    rows = data.get("segments") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ValueError("ASR JSON needs an object with a segments array")
    result = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict) or not isinstance(row.get("text"), str) or not row["text"].strip():
            raise ValueError(f"Invalid JSON segment {index}")
        values = [row.get("start"), row.get("end")]
        for value in values:
            if value is not None and (type(value) not in (int, float)
                                      or not math.isfinite(value) or value < 0):
                raise ValueError(f"Invalid time in JSON segment {index}")
        if values[1] is not None and (values[0] is None or values[1] < values[0]):
            raise ValueError(f"Reversed or unanchored end in JSON segment {index}")
        speaker = row.get("speaker")
        if speaker is not None and (not isinstance(speaker, str) or not speaker.strip()):
            raise ValueError(f"Invalid speaker in JSON segment {index}")
        result.append(dict(text=row["text"].strip(), speaker=speaker, start=values[0],
                           end=values[1], line_start=None, line_end=None))
    return result


def normalize(text, extension):
    if extension == ".srt":
        rows = parse_subtitles(text)
    elif extension == ".vtt":
        rows = parse_subtitles(text, vtt=True)
    elif extension == ".json":
        rows = parse_json(text)
    elif extension in (".txt", ".md"):
        rows = parse_plain(text)
    else:
        raise ValueError("Supported inputs: .txt .md .srt .vtt .json (not audio/binary)")
    if not rows:
        raise ValueError("No transcript segments found")
    result = []
    for row in rows:
        # Preserve substring order. Split long paragraphs, never fabricate cue times.
        content = row["text"]
        for offset in range(0, len(content), MAX_SEGMENT):
            part = content[offset:offset + MAX_SEGMENT]
            if part.strip():
                result.append(dict(row, id=f"S{len(result) + 1:04d}", text=part))
    return result


def chunks(segments, budget=12000, overlap=1):
    if budget < MAX_SEGMENT or overlap < 0:
        raise ValueError(f"Chunk budget must be >= {MAX_SEGMENT}; overlap >= 0")
    groups, current, size = [], [], 0
    for index, segment in enumerate(segments):
        if current and size + len(segment["text"]) > budget:
            groups.append(current)
            current, size = [], 0
        current.append(index)
        size += len(segment["text"])
    if current:
        groups.append(current)
    return [dict(id=f"C{i + 1:04d}", core_ids=[segments[n]["id"] for n in group],
                 context_ids=[segments[n]["id"] for n in range(
                     max(0, group[0] - overlap), min(len(segments), group[-1] + overlap + 1))
                              if n not in group]) for i, group in enumerate(groups)]


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
                          + "\n", encoding="utf-8")


def prepare(path, out, scope="unknown", scope_note="", source_url="", source_kind="transcript",
            title="", budget=12000, overlap=1):
    if scope not in {"full", "partial", "unknown"}:
        raise ValueError("Invalid scope")
    if source_kind not in {"transcript", "show_notes"}:
        raise ValueError("Invalid source kind")
    if scope == "full" and not scope_note.strip():
        raise ValueError("Full scope requires --scope-note documenting the basis")
    if source_kind == "show_notes" and scope == "full":
        raise ValueError("Show notes cannot establish full episode coverage")
    path, out = Path(path), Path(out)
    raw = path.read_bytes()
    if len(raw) > 30 * 1024 * 1024:
        raise ValueError("Transcript exceeds 30 MiB; split explicitly before preparation")
    text = raw.decode("utf-8-sig")
    segments = normalize(text, path.suffix.lower())
    grouped = chunks(segments, budget, overlap)
    manifest = dict(schema_version=1, source=dict(title=title or path.stem,
                    url=source_url, kind=source_kind, scope=scope, scope_note=scope_note,
                    input_name=path.name, original_sha256=digest(raw)),
                    segments_sha256=segment_digest(segments), segments=segments)
    out.mkdir(parents=True, exist_ok=False)
    (out / "source.original").write_bytes(raw)
    write_json(out / "transcript.json", manifest)
    write_json(out / "chunks.json", grouped)
    write_json(out / "ledger.json", dict(schema_version=1, reviewed_segments=[],
                                         review_notes={}, units=[]))
    return dict(segments=len(segments), chunks=len(grouped), scope=scope, out=str(out))


def audit(manifest, ledger, report):
    errors, warnings = [], []
    def error(message):
        errors.append(message)
    if not isinstance(manifest, dict) or not isinstance(ledger, dict):
        raise ValueError("Transcript and ledger must be JSON objects")
    if manifest.get("schema_version") != 1 or ledger.get("schema_version") != 1:
        error("Unsupported schema_version")
    rows = manifest.get("segments")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Transcript segments must be a nonempty array")
    if manifest.get("segments_sha256") != segment_digest(rows):
        error("Normalized transcript digest mismatch")
    segments = {}
    previous_start = -1
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("Invalid transcript segment")
        sid = row["id"]
        if sid in segments or not re.fullmatch(r"S\d{4,}", sid):
            error(f"Invalid or duplicate segment ID: {sid}")
        if not isinstance(row.get("text"), str) or not row["text"].strip():
            raise ValueError(f"Invalid segment text: {sid}")
        if row.get("speaker") is not None and not isinstance(row["speaker"], str):
            raise ValueError(f"Invalid segment speaker: {sid}")
        segments[sid] = row
        start, end = row.get("start"), row.get("end")
        for value in (start, end):
            if value is not None and (type(value) not in (int, float)
                                      or not math.isfinite(value) or value < 0):
                raise ValueError(f"Invalid time: {sid}")
        if end is not None and (start is None or end < start):
            error(f"Invalid cue range: {sid}")
        if start is not None:
            if start < previous_start:
                error(f"Out-of-order cue: {sid}")
            previous_start = start
    source = manifest.get("source", {})
    if not isinstance(source, dict):
        raise ValueError("Invalid source metadata")
    scope = source.get("scope")
    if scope not in {"full", "partial", "unknown"}:
        error("Invalid source scope")
    if source.get("kind") not in {"transcript", "show_notes"}:
        error("Invalid source kind")
    if scope == "full" and not source.get("scope_note", "").strip():
        error("Full scope requires a documented basis")
    if scope == "full" and source.get("kind") == "show_notes":
        error("Show notes cannot establish full episode coverage")
    if f"Source coverage: {scope}" not in report:
        error("Report must visibly disclose the matching Source coverage")
    if scope != "full":
        warnings.append(f"Source scope is {scope}; full-episode coverage is not established")
    reviewed = ledger.get("reviewed_segments")
    if not isinstance(reviewed, list) or not all(isinstance(s, str) for s in reviewed):
        raise ValueError("reviewed_segments must be an array of IDs")
    if len(reviewed) != len(set(reviewed)):
        error("Duplicate reviewed segment IDs")
    missing = sorted(set(segments) - set(reviewed))
    unknown = sorted(set(reviewed) - set(segments))
    if missing:
        error("Unreviewed segments: " + ", ".join(missing))
    if unknown:
        error("Unknown reviewed segments: " + ", ".join(unknown))
    start_marker, end_marker = "<!-- deep-read:start -->", "<!-- deep-read:end -->"
    deep = ""
    if report.count(start_marker) != 1 or report.count(end_marker) != 1:
        error("Report needs exactly one pair of deep-read markers")
    elif report.index(start_marker) >= report.index(end_marker):
        error("Reversed deep-read markers")
    else:
        deep = report.split(start_marker, 1)[1].split(end_marker, 1)[0]
    cited = set(re.findall(r"\[(U\d{3,})\]", deep))
    rows_units = ledger.get("units")
    if not isinstance(rows_units, list) or not rows_units:
        raise ValueError("Ledger units must be a nonempty array")
    units = {}
    for unit in rows_units:
        if not isinstance(unit, dict) or not isinstance(unit.get("id"), str):
            raise ValueError("Invalid ledger unit")
        uid = unit["id"]
        if uid in units or not re.fullmatch(r"U\d{3,}", uid):
            error(f"Invalid or duplicate unit ID: {uid}")
        units[uid] = unit
        for field in ("topic", "claim"):
            if not isinstance(unit.get(field), str) or not unit[field].strip():
                error(f"{uid}: missing {field}")
        if unit.get("kind") not in {"fact", "opinion", "speculation", "question"}:
            error(f"{uid}: invalid kind")
        if unit.get("importance") not in {"critical", "important", "optional"}:
            error(f"{uid}: invalid importance")
        disposition = unit.get("disposition")
        if disposition not in {"included", "excluded", "duplicate"}:
            error(f"{uid}: invalid disposition")
        if disposition != "included" and not str(unit.get("reason", "")).strip():
            error(f"{uid}: excluded/duplicate unit needs a reason")
        if disposition == "excluded" and unit.get("importance") != "optional":
            error(f"{uid}: important/critical unit cannot be excluded")
        if disposition == "included" and uid not in cited:
            error(f"{uid}: included unit absent from deep-read citations")
        if disposition != "included" and uid in cited:
            error(f"{uid}: non-included unit cited as retained")
        if "speaker" not in unit or (unit["speaker"] is not None and
                                         not isinstance(unit["speaker"], str)):
            error(f"{uid}: speaker must be a source label or null")
        evidence = unit.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            error(f"{uid}: evidence is required")
            continue
        for item in evidence:
            if not isinstance(item, dict) or not isinstance(item.get("segment_id"), str):
                error(f"{uid}: invalid evidence")
                continue
            segment = segments.get(item["segment_id"])
            if segment is None:
                error(f"{uid}: unknown evidence segment {item['segment_id']}")
                continue
            quote = item.get("quote")
            if not isinstance(quote, str) or not canonical(quote) or canonical(quote) not in canonical(segment["text"]):
                error(f"{uid}: quote does not match {segment['id']}")
            if unit.get("speaker") != segment.get("speaker"):
                error(f"{uid}: speaker mismatch at {segment['id']}")
    for uid, unit in units.items():
        if unit.get("disposition") == "duplicate":
            target = units.get(unit.get("duplicate_of")) if isinstance(unit.get("duplicate_of"), str) else None
            if target is None or target.get("disposition") != "included" or target.get("topic") != unit.get("topic"):
                error(f"{uid}: duplicate target must be an included unit in the same topic")
    for uid in sorted(cited - set(units)):
        error(f"Unknown report citation: {uid}")
    topics = {u.get("topic") for u in units.values() if isinstance(u.get("topic"), str)
              and u.get("disposition") != "duplicate"}
    retained_topics = {u.get("topic") for uid, u in units.items()
                       if u.get("disposition") == "included" and uid in cited}
    for topic in sorted(topics - retained_topics):
        error(f"Topic has no retained unit: {topic}")
    unique = [u for u in units.values() if u.get("disposition") != "duplicate"]
    retained = [u for u in unique if u.get("disposition") == "included" and u["id"] in cited]
    warnings.append("Structural checks only: extraction completeness, truth, importance, entailment and translation require semantic review")
    return dict(schema_version=1, status="pass" if not errors else "fail", scope=scope,
                errors=errors, warnings=warnings,
                metrics=dict(reviewed_segments=len(set(reviewed) & set(segments)),
                             total_segments=len(segments), eligible_unique_units=len(unique),
                             retained_unique_units=len(retained), topics=len(topics)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="Normalize transcript and create a new run directory")
    prep.add_argument("input", type=Path)
    prep.add_argument("--out", type=Path, required=True)
    prep.add_argument("--scope", choices=["full", "partial", "unknown"], default="unknown")
    prep.add_argument("--scope-note", default="")
    prep.add_argument("--source-url", default="")
    prep.add_argument("--source-kind", choices=["transcript", "show_notes"], default="transcript")
    prep.add_argument("--title", default="")
    prep.add_argument("--chunk-chars", type=int, default=12000)
    prep.add_argument("--overlap", type=int, default=1)
    check = sub.add_parser("audit", help="Check accounting and evidence, not semantic truth")
    check.add_argument("transcript", type=Path)
    check.add_argument("ledger", type=Path)
    check.add_argument("reading", type=Path)
    check.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(args.input, args.out, args.scope, args.scope_note,
                             args.source_url, args.source_kind, args.title,
                             args.chunk_chars, args.overlap)
        else:
            manifest = json.loads(args.transcript.read_text(encoding="utf-8"))
            ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
            report = args.reading.read_text(encoding="utf-8")
            result = audit(manifest, ledger, report)
            original = args.transcript.parent / "source.original"
            if not original.is_file() or digest(original.read_bytes()) != manifest["source"].get("original_sha256"):
                result["errors"].append("Original source missing or digest mismatch")
                result["status"] = "fail"
            if args.out:
                write_json(args.out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("status") == "fail" else 0
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        print(json.dumps(dict(status="error", error=str(exc)), ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
