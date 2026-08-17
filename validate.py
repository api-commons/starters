#!/usr/bin/env python3
"""Validate every starter in this repo.

  python3 validate.py

Checks, per starter:
  starter-json-schema.yml  is a valid JSON Schema 2020-12 document, and its own
                           `examples` validate against the properties they sit on
  starter-apis.yml         validates against the APIs.json schema
  starter-openapi.yml      is well-formed, and its inline Problem schema matches
                           RFC 9457 member types

The OpenAPI is additionally linted with Spectral; see README.md. This script
deliberately has no Node dependency so it runs anywhere Python does.

Exits non-zero on any failure.
"""

import sys
import urllib.request
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("Requires pyyaml and jsonschema:  pip install jsonschema pyyaml")

HERE = Path(__file__).resolve().parent

# The APIs.json schema is not vendored here — it belongs to the spec, and a copy
# would drift. Fetched at validation time, with a local override for offline use.
APIS_JSON_SCHEMA_URL = (
    "https://raw.githubusercontent.com/apis-json/api-json/develop/spec/schema_0.22.yml"
)

failures = []


def report(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def load(fn):
    return yaml.safe_load((HERE / fn).read_text())


def check_json_schema():
    doc = load("starter-json-schema.yml")
    try:
        Draft202012Validator.check_schema(doc)
    except Exception as e:  # noqa: BLE001 — surface whatever the validator says
        report("starter-json-schema.yml", False, str(e).split("\n")[0])
        return

    # A starter whose own examples do not validate is worse than no starter.
    bad = []
    for prop, subschema in doc.get("properties", {}).items():
        for ex in subschema.get("examples", []):
            errs = list(Draft202012Validator(subschema).iter_errors(ex))
            if errs:
                bad.append(f"{prop}={ex!r}: {errs[0].message}")
    if bad:
        report("starter-json-schema.yml", False, "; ".join(bad))
    else:
        n = sum(len(s.get("examples", [])) for s in doc.get("properties", {}).values())
        report("starter-json-schema.yml", True, f"valid 2020-12, {n} examples check out")


def check_apis_json():
    doc = load("starter-apis.yml")
    local = HERE / "schema_0.22.yml"
    try:
        if local.exists():
            schema = yaml.safe_load(local.read_text())
            src = "local schema_0.22.yml"
        else:
            with urllib.request.urlopen(APIS_JSON_SCHEMA_URL, timeout=20) as r:
                schema = yaml.safe_load(r.read().decode())
            src = "apis-json/api-json@develop"
    except Exception as e:  # noqa: BLE001
        report("starter-apis.yml", False, f"could not load the APIs.json schema: {e}")
        return

    errs = sorted(
        Draft202012Validator(schema).iter_errors(doc),
        key=lambda e: list(e.absolute_path),
    )
    if errs:
        detail = "; ".join(
            f"{'/'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}"
            for e in errs[:4]
        )
        report("starter-apis.yml", False, detail)
    else:
        report("starter-apis.yml", True, f"validates against {src}")


# RFC 9457 Section 3.1 — a member whose value type does not match MUST be
# ignored by a consumer, so a wrong type here fails silently in production.
RFC9457_TYPES = {
    "type": {"string"},
    "title": {"string"},
    "status": {"integer", "number"},
    "detail": {"string"},
    "instance": {"string"},
}


def check_openapi():
    doc = load("starter-openapi.yml")
    problems = []

    if not str(doc.get("openapi", "")).startswith("3.1"):
        problems.append("not an OpenAPI 3.1 document")
    if not doc.get("paths"):
        problems.append("no paths")

    for op_path, item in (doc.get("paths") or {}).items():
        for method, op in item.items():
            if method in ("parameters", "$ref") or not isinstance(op, dict):
                continue
            if not op.get("operationId"):
                problems.append(f"{method.upper()} {op_path}: no operationId")
            if not op.get("description"):
                problems.append(f"{method.upper()} {op_path}: no description")

    problem = (doc.get("components", {}).get("schemas", {}) or {}).get("Problem")
    if not problem:
        problems.append("no Problem schema — a starter should still error in the RFC 9457 shape")
    else:
        if problem.get("type") != "object":
            problems.append("Problem: missing `type: object`")
        if problem.get("additionalProperties") is False:
            problems.append("Problem: additionalProperties false forbids RFC 9457 extension members")
        for member, allowed in RFC9457_TYPES.items():
            declared = (problem.get("properties", {}).get(member) or {}).get("type")
            if declared and declared not in allowed:
                problems.append(
                    f"Problem.{member}: declared `{declared}`, RFC 9457 requires "
                    f"{' or '.join(sorted(allowed))}"
                )

    if problems:
        report("starter-openapi.yml", False, "; ".join(problems[:4]))
    else:
        ops = sum(
            1
            for i in doc["paths"].values()
            for m, o in i.items()
            if m not in ("parameters", "$ref") and isinstance(o, dict)
        )
        report("starter-openapi.yml", True, f"{ops} operations, Problem schema conforms")


check_json_schema()
check_apis_json()
check_openapi()

print()
if failures:
    print(f"FAILED: {', '.join(failures)}")
    sys.exit(1)
print("All starters valid.")
