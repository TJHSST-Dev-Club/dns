import os
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:
    print("Missing dependency 'pyyaml'. Add it to pyproject and run 'uv sync'.", file=sys.stderr)
    raise


BASE_ZONE_FILE = "tjdev.club.yaml"
GROUP_DIRECTORIES = ["club_sites", "user_sites"]
OUTPUT_DIRECTORY = "zones"
OUTPUT_ZONE_FILE = os.path.join(OUTPUT_DIRECTORY, "tjdev.club.yaml")


def _as_list(value):
    if isinstance(value, list):
        return value
    return [value]


def _record_sort_key(record):
    if isinstance(record, dict):
        type_str = str(record.get("type", ""))
        value_str = str(record.get("value", record.get("values", "")))
        return f"{type_str}:{value_str}"
    return str(record)


def _merge_zone_dicts(into_dict, from_dict):
    for name, new_value in from_dict.items():
        if name not in into_dict:
            into_dict[name] = new_value
            continue

        existing_value = into_dict[name]
        merged_list = _as_list(existing_value) + _as_list(new_value)

        # De-duplicate by simple stringified identity for stability
        unique = []
        seen = set()
        for item in merged_list:
            key = str(item)
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)

        unique.sort(key=_record_sort_key)
        if len(unique) == 1:
            into_dict[name] = unique[0]
        else:
            into_dict[name] = unique


def _load_yaml_file(path_str):
    path = Path(path_str)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Top-level YAML must be a mapping in {path}")
        return data


def _normalize_record_dict(record):
    # Some input files may incorrectly nest keys under 'octodns'. Lift them up.
    if not isinstance(record, dict):
        return record
    octo = record.get("octodns")
    if isinstance(octo, dict):
        for key in ("ttl", "type", "value", "values"):
            if key in octo and key not in record:
                record[key] = octo.pop(key)
        # Drop empty octodns blocks
        if not octo:
            record.pop("octodns", None)
    return record


def _normalize_zone(merged):
    normalized = {}
    for name, value in merged.items():
        items = _as_list(value)
        items = [_normalize_record_dict(dict(item)) if isinstance(item, dict) else item for item in items]
        # Collapse back to single dict when applicable
        normalized[name] = items[0] if len(items) == 1 else items
    return normalized


def build_zone_file():
    merged = {}

    # Start with base zone file if present (e.g., apex NS)
    base = _load_yaml_file(BASE_ZONE_FILE)
    _merge_zone_dicts(merged, base)

    # Merge group directories
    for directory in GROUP_DIRECTORIES:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        for file in sorted(dir_path.glob("*.yaml")):
            data = _load_yaml_file(str(file))
            _merge_zone_dicts(merged, data)

    # Normalize any malformed record dicts
    merged = _normalize_zone(merged)

    # Ensure output directory exists
    Path(OUTPUT_DIRECTORY).mkdir(parents=True, exist_ok=True)

    # Dump merged YAML deterministically
    with open(OUTPUT_ZONE_FILE, "w", encoding="utf-8") as fh:
        fh.write("---\n")
        yaml.safe_dump(merged, fh, sort_keys=True, default_flow_style=False)

    print(f"Wrote merged zone to {OUTPUT_ZONE_FILE}")


def main():
    build_zone_file()


if __name__ == "__main__":
    main()
