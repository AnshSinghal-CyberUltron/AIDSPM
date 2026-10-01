"""Structural checks for the proposed contract; not a full OpenAPI or SQL validator."""

import json
import re
from datetime import datetime
from pathlib import Path
from uuid import UUID

import yaml

ROOT = Path(__file__).resolve().parents[1]


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key!r}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def walk(value, root, operation_ids):
    if isinstance(value, dict):
        ref = value.get("$ref")
        if ref is not None:
            assert ref.startswith("#/"), f"External ref unsupported by this structural check: {ref}"
            target = root
            for segment in ref[2:].split("/"):
                target = target[segment.replace("~1", "/").replace("~0", "~")]
            assert target is not None, ref
        if "operationId" in value:
            operation_id = value["operationId"]
            assert operation_id not in operation_ids, f"Duplicate operationId: {operation_id}"
            operation_ids.add(operation_id)
        if value.get("type") == "array":
            assert "items" in value, f"Array without items: {value}"
        for child in value.values():
            walk(child, root, operation_ids)
    elif isinstance(value, list):
        for child in value:
            walk(child, root, operation_ids)


def check_example(value, schema, spec, path="$", depth=0):
    """Check a useful JSON Schema subset; a full 3.1 validator is still required."""
    assert depth < 30, path
    if "$ref" in schema:
        schema = spec["components"]["schemas"][schema["$ref"].split("/")[-1]]
    expected = schema.get("type")
    if isinstance(expected, str):
        expected = [expected]
    predicates = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (float, int)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }
    if expected:
        assert any(predicates[t](value) for t in expected), (path, "type", expected)
    if value is None:
        return
    if "const" in schema:
        assert value == schema["const"], (path, "const")
    if "enum" in schema:
        assert value in schema["enum"], (path, "enum")
    if isinstance(value, dict):
        assert set(schema.get("required", [])) <= set(value), (path, "required")
        if schema.get("additionalProperties") is False:
            assert set(value) <= set(schema.get("properties", {})), (path, "extra")
        for key, item in value.items():
            if key in schema.get("properties", {}):
                check_example(item, schema["properties"][key], spec, path + "." + key, depth + 1)
    if isinstance(value, list):
        for index, item in enumerate(value):
            check_example(item, schema["items"], spec, f"{path}[{index}]", depth + 1)
    if isinstance(value, str):
        if schema.get("format") == "uuid":
            UUID(value)
        if schema.get("format") == "date-time":
            datetime.fromisoformat(value)
        if "pattern" in schema:
            assert re.search(schema["pattern"], value), (path, "pattern")
        if "maxLength" in schema:
            assert len(value) <= schema["maxLength"], (path, "maxLength")
        if "minLength" in schema:
            assert len(value) >= schema["minLength"], (path, "minLength")
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        if "minimum" in schema:
            assert value >= schema["minimum"], (path, "minimum")
        if "maximum" in schema:
            assert value <= schema["maximum"], (path, "maximum")


def main():
    spec = yaml.load((ROOT / "openapi.yaml").read_text(), Loader=UniqueLoader)
    assert spec["openapi"] == "3.1.1"
    operations = set()
    walk(spec, spec, operations)
    assert len(operations) >= 15, f"Only {len(operations)} operations found"
    assert set(spec["components"]["schemas"]["ErrorResponse"]["required"]) == {"error"}
    for path in spec["paths"]:
        if path.startswith("/api/v1/") and path not in {"/api/v1/system"}:
            assert spec.get("security"), path
    example_types = {
        "session.json": "Session", "source.json": "Source", "asset.json": "Asset",
        "partial_scan.json": "Scan", "declared_finding.json": "Finding",
        "unknown_path.json": "AccessPathResult", "error.json": "ErrorResponse",
    }
    for filename, schema_name in example_types.items():
        example = json.loads((ROOT / "examples" / filename).read_text())
        check_example(example, spec["components"]["schemas"][schema_name], spec)
    ddl = (ROOT / "schema.postgres.sql").read_text()
    for table in ("tenants", "tenant_memberships", "sources", "scan_jobs", "assets",
                  "asset_versions", "evidence", "findings", "graph_edges", "audit_events"):
        assert f"CREATE TABLE {table}" in ddl, table
    assert "FORCE ROW LEVEL SECURITY" in ddl
    assert "tenant_memberships_auth_lookup" in (ROOT / "roles.example.sql").read_text()
    print(f"Structural contract check passed: {len(operations)} operations, "
          f"{len(list((ROOT / 'examples').glob('*.json')))} JSON examples")


if __name__ == "__main__":
    main()
