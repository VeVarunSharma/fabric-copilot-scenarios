#!/usr/bin/env python3
"""Build deterministic lineage markdown from a local manifest."""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

TYPE_ORDER = {
    "source": 0,
    "pipeline": 1,
    "notebook": 2,
    "table": 3,
    "semantic_model": 4,
    "report": 5,
}

TYPE_GROUPS = {
    "source": "Sources",
    "pipeline": "Pipelines",
    "notebook": "Notebooks",
    "table": "Tables",
    "semantic_model": "SemanticModels",
    "report": "Reports",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic Mermaid lineage and downstream impact markdown."
    )
    parser.add_argument(
        "--manifest",
        default="artifacts/lineage-manifest.json",
        help="Manifest path relative to the scenario directory.",
    )
    parser.add_argument(
        "--diagram-out",
        default="generated/lineage-diagram.md",
        help="Diagram output path relative to the scenario directory.",
    )
    parser.add_argument(
        "--impact-out",
        default="artifacts/expected-impact-report.md",
        help="Impact report output path relative to the scenario directory.",
    )
    return parser.parse_args()


def scenario_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_safe(path_value: str, root: Path, expected_suffix: str) -> Path:
    candidate = Path(path_value)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Path escapes the scenario directory: {path_value}")
    if resolved.suffix.lower() != expected_suffix:
        raise ValueError(f"Expected a {expected_suffix} file: {path_value}")
    return resolved


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="ascii"))
    validate_manifest(data)
    return data


def validate_manifest(data: dict) -> None:
    nodes = data.get("nodes")
    edges = data.get("edges")
    change_scenarios = data.get("change_scenarios")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("Manifest must include a non-empty nodes list.")
    if not isinstance(edges, list) or not edges:
        raise ValueError("Manifest must include a non-empty edges list.")
    if not isinstance(change_scenarios, list) or not change_scenarios:
        raise ValueError("Manifest must include a non-empty change_scenarios list.")

    seen_ids = set()
    for node in nodes:
        node_id = node.get("id")
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Every node must include a string id.")
        if node_id in seen_ids:
            raise ValueError(f"Duplicate node id found: {node_id}")
        seen_ids.add(node_id)
        if node.get("type") not in TYPE_ORDER:
            raise ValueError(f"Unsupported node type: {node.get('type')}")

    for edge in edges:
        if edge.get("from") not in seen_ids or edge.get("to") not in seen_ids:
            raise ValueError(f"Edge references unknown node: {edge}")
        if not edge.get("relationship"):
            raise ValueError(f"Edge missing relationship: {edge}")

    for scenario in change_scenarios:
        if scenario.get("target") not in seen_ids:
            raise ValueError(f"Change scenario target is unknown: {scenario}")
        if not scenario.get("id") or not scenario.get("change"):
            raise ValueError(f"Change scenario is incomplete: {scenario}")


def build_indexes(data: dict):
    nodes = data["nodes"]
    edges = data["edges"]
    nodes_by_id = {node["id"]: node for node in nodes}
    node_order = {node["id"]: index for index, node in enumerate(nodes)}
    adjacency = {node["id"]: [] for node in nodes}
    edge_lookup = {}
    for edge in sorted(
        edges,
        key=lambda item: (node_order[item["from"]], node_order[item["to"]], item["relationship"]),
    ):
        adjacency[edge["from"]].append(edge["to"])
        edge_lookup[(edge["from"], edge["to"])] = edge["relationship"]
    return nodes_by_id, node_order, adjacency, edge_lookup


def sanitize_identifier(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value)


def collect_descendants(start_id: str, adjacency: dict, node_order: dict):
    queue = deque([(start_id, 0, [start_id])])
    visited = {start_id}
    collected = []
    while queue:
        current_id, distance, path = queue.popleft()
        next_nodes = sorted(adjacency[current_id], key=lambda item: node_order[item])
        for next_id in next_nodes:
            next_path = path + [next_id]
            if next_id not in visited:
                visited.add(next_id)
                collected.append((next_id, distance + 1, next_path))
                queue.append((next_id, distance + 1, next_path))
    return collected


def format_path(path_ids, nodes_by_id: dict) -> str:
    return " -> ".join(nodes_by_id[node_id]["label"] for node_id in path_ids)


def render_diagram(data: dict, manifest_reference: str) -> str:
    _, node_order, _, _ = build_indexes(data)
    grouped_nodes = {}
    for node in data["nodes"]:
        grouped_nodes.setdefault(node["type"], []).append(node)

    lines = [
        "# Retail lineage diagram",
        "",
        f"> Generated from `{manifest_reference}` using `scripts/build_lineage.py`.",
        "",
        "```mermaid",
        "flowchart LR",
    ]

    for node_type in sorted(grouped_nodes, key=lambda item: TYPE_ORDER[item]):
        lines.append(f"    subgraph {TYPE_GROUPS[node_type]}")
        for node in sorted(grouped_nodes[node_type], key=lambda item: node_order[item["id"]]):
            node_id = sanitize_identifier(node["id"])
            node_label = node["label"]
            lines.append(f'        {node_id}["{node_label}"]')
        lines.append("    end")

    for edge in data["edges"]:
        from_id = sanitize_identifier(edge["from"])
        to_id = sanitize_identifier(edge["to"])
        relationship = edge["relationship"]
        lines.append(f"    {from_id} -->|{relationship}| {to_id}")

    lines.extend(["```", ""])
    return "\n".join(lines)


def validation_focus(descendants, nodes_by_id: dict):
    present_types = {nodes_by_id[node_id]["type"] for node_id, _, _ in descendants}
    recommendations = []
    if "pipeline" in present_types:
        recommendations.append("Review pipeline parameters, dependencies, and retry behavior.")
    if "notebook" in present_types:
        recommendations.append("Validate notebook schema handling, transformation logic, and logging.")
    if "table" in present_types:
        recommendations.append("Re-run reconciliations and confirm row-level quality rules still pass.")
    if "semantic_model" in present_types:
        recommendations.append("Refresh the semantic model and inspect impacted relationships and measures.")
    if "report" in present_types:
        recommendations.append(
            "Confirm the report scaffold still references the semantic model; "
            "add visual-level checks only after data-bound visuals are authored."
        )
    return recommendations


def render_impact(data: dict, manifest_reference: str) -> str:
    nodes_by_id, node_order, adjacency, _ = build_indexes(data)
    lines = [
        "# Expected downstream impact report",
        "",
        f"> Generated from `{manifest_reference}` using `scripts/build_lineage.py`.",
        "",
    ]

    for scenario in sorted(data["change_scenarios"], key=lambda item: item["id"]):
        target_id = scenario["target"]
        target_node = nodes_by_id[target_id]
        descendants = collect_descendants(target_id, adjacency, node_order)
        immediate = sorted(adjacency[target_id], key=lambda item: node_order[item])

        lines.append(f"## Change scenario: {scenario['id']}")
        lines.append("")
        lines.append(f"- Target asset: `{target_node['label']}` ({target_node['type']})")
        lines.append(f"- Requested change: {scenario['change']}")
        lines.append(f"- Immediate downstream count: {len(immediate)}")
        lines.append(f"- Full downstream count: {len(descendants)}")
        lines.append("")

        if immediate:
            lines.append("### Immediate downstream assets")
            lines.append("")
            for node_id in immediate:
                node = nodes_by_id[node_id]
                lines.append(f"- `{node['label']}` ({node['type']})")
            lines.append("")

        lines.append("### Full downstream impact")
        lines.append("")
        lines.append("| Asset | Type | Owner | First downstream path |")
        lines.append("| --- | --- | --- | --- |")
        for node_id, _, path in descendants:
            node = nodes_by_id[node_id]
            lines.append(
                f"| `{node['label']}` | `{node['type']}` | {node['owner']} | {format_path(path, nodes_by_id)} |"
            )
        lines.append("")

        lines.append("### Validation focus")
        lines.append("")
        for recommendation in validation_focus(descendants, nodes_by_id):
            lines.append(f"- {recommendation}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = scenario_root()
    try:
        manifest_path = resolve_safe(args.manifest, root, ".json")
        diagram_path = resolve_safe(args.diagram_out, root, ".md")
        impact_path = resolve_safe(args.impact_out, root, ".md")
        data = load_manifest(manifest_path)
        manifest_reference = manifest_path.relative_to(root).as_posix()
        diagram_text = render_diagram(data, manifest_reference)
        impact_text = render_impact(data, manifest_reference)
        diagram_path.parent.mkdir(parents=True, exist_ok=True)
        impact_path.parent.mkdir(parents=True, exist_ok=True)
        diagram_path.write_text(diagram_text, encoding="ascii")
        impact_path.write_text(impact_text, encoding="ascii")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {diagram_path.relative_to(root)}")
    print(f"Wrote {impact_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
