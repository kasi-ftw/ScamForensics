from collections import defaultdict

SHAREABLE = {"phone", "url", "upi", "email", "qr"}
SKIP_VALUES = {"QR referenced"}


class UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[b] = a


def build_graph(evidence, entities):
    by_evidence = defaultdict(list)
    owners = defaultdict(set)
    types = {}
    for entity in entities:
        key = (entity["type"], entity["value"])
        by_evidence[entity["evidence_id"]].append(entity)
        owners[key].add(entity["evidence_id"])
        types[key] = entity["type"]
    nodes, edges = [], []
    for index, item in enumerate(evidence):
        nodes.append({"id": f"e-{item['id']}", "type": "evidence", "label": item["filename"], "kind": item["kind"], "position": {"x": 0, "y": index * 100}})
    entity_keys = [key for key in owners if key[1] not in SKIP_VALUES and key[0] != "keyword"]
    grouped = defaultdict(list)
    for key in entity_keys:
        grouped[key[0]].append(key)
    columns = {kind: index + 1 for index, kind in enumerate(sorted(grouped))}
    for kind, keys in grouped.items():
        for index, key in enumerate(keys):
            shared = key[0] in SHAREABLE and len(owners[key]) >= 2
            node_id = f"x-{kind}-{key[1]}"
            nodes.append({"id": node_id, "type": "entity", "label": key[1], "entity_type": kind, "shared": shared, "position": {"x": columns[kind] * 250, "y": index * 80}})
            for evidence_id in owners[key]:
                edges.append({"id": f"{evidence_id}-{node_id}", "source": f"e-{evidence_id}", "target": node_id, "animated": shared, "shared": shared, "label": "contains"})
    uf = UnionFind([item["id"] for item in evidence])
    for key, linked in owners.items():
        if key[0] in SHAREABLE and key[1] not in SKIP_VALUES and len(linked) >= 2:
            linked = list(linked)
            for value in linked[1:]:
                uf.union(linked[0], value)
    clusters = defaultdict(list)
    for item in evidence:
        clusters[uf.find(item["id"])].append(item["id"])
    cluster_values = list(clusters.values())
    shared = [{"type": k[0], "value": k[1], "evidence_ids": sorted(v)} for k, v in owners.items() if k[0] in SHAREABLE and k[1] not in SKIP_VALUES and len(v) >= 2]
    return {"nodes": nodes, "edges": edges, "clusters": cluster_values, "largest_cluster": max(cluster_values, key=len, default=[]), "shared_entities": shared}
