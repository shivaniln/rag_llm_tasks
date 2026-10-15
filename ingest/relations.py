import networkx as nx
from collections import deque

from app.common import sid


def make_relation(source_id, target_id, relation_type, weight, evidence):
    return {
        "source_id": source_id,
        "target_id": target_id,
        "type": relation_type,
        "weight": float(weight),
        "evidence": str(evidence),
    }


def relation_id(relation):
    return sid(
        relation["source_id"],
        relation["target_id"],
        relation["type"],
    )


def build_graph(relations):
    graph = nx.MultiDiGraph()

    for relation in relations:
        graph.add_edge(
            relation["source_id"],
            relation["target_id"],
            key=relation["type"],
            type=relation["type"],
            weight=relation["weight"],
            evidence=relation["evidence"],
        )

    return graph


def neighbours(graph, entity_id, hops=2, types=None, max_expand=20):
    seen = {entity_id}
    output = {}
    queue = deque([(entity_id, [entity_id], 0)])

    while queue:
        node, path, depth = queue.popleft()
        if depth >= hops:
            continue

        edges = []

        for _, target, key, data in graph.out_edges(
            node, keys=True, data=True
        ):
            edges.append((target, key, data))

        for source, _, key, data in graph.in_edges(
            node, keys=True, data=True
        ):
            edges.append((source, key, data))

        if types is not None:
            edges = [e for e in edges if e[2]["type"] in types]

        edges.sort(key=lambda edge: (-edge[2]["weight"], edge[0]))
        edges = edges[:max_expand]

        for target, _, _ in edges:
            if target in seen:
                continue

            seen.add(target)
            next_path = path + [target]
            output[target] = {
                "path": next_path,
                "hops": depth + 1,
            }
            queue.append((target, next_path, depth + 1))

    return output

import os
import requests
import geopandas as gpd
from shapely.geometry import shape


def build_near_relations(
    geoserver_url="http://localhost:8080/geoserver/ows",
    roads_path=r"D:\geoassistant_osm\eastern-zone.gpkg",
    max_distance=300,
):
    """Create School-to-Road near relations using GeoServer and OSM roads."""
    headers = {}
    encoded = os.environ.get("GEOSERVER_AUTH")
    if encoded:
        headers["Authorization"] = "Basic " + encoded

    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": "east_india:schools",
        "outputFormat": "application/json",
    }

    response = requests.get(
        geoserver_url, params=params, headers=headers, timeout=60
    )
    response.raise_for_status()

    school_rows = []
    for feature in response.json().get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry")
        if geom and props.get("osm_id") is not None:
            school_rows.append({
                "osm_id": str(props["osm_id"]),
                "name": props.get("name"),
                "geometry": shape(geom),
            })

    if not school_rows:
        return []

    schools = gpd.GeoDataFrame(
        school_rows, geometry="geometry", crs="EPSG:4326"
    ).to_crs("EPSG:32646")

    roads = gpd.read_file(
        roads_path, layer="gis_osm_roads_free",
        columns=["osm_id", "name", "geometry"]
    ).to_crs("EPSG:32646")

    relations = []
    for _, school in schools.iterrows():
        if school.geometry is None or school.geometry.is_empty:
            continue

        # Buffer first to avoid measuring every road against every school.
        candidates = roads[roads.geometry.intersects(
            school.geometry.buffer(max_distance)
        )]

        for _, road in candidates.iterrows():
            distance = school.geometry.distance(road.geometry)
            if distance > max_distance:
                continue

            weight = max(0.3, 1.0 - distance / max_distance)
            relations.append(make_relation(
                source_id=sid("School", school["osm_id"]),
                target_id=sid("Road", road["osm_id"]),
                relation_type="near",
                weight=weight,
                evidence=(
                    f"geoserver school osm_id={school['osm_id']}; "
                    f"road osm_id={road['osm_id']}; distance_m={distance:.2f}"
                ),
            ))

    return relations
