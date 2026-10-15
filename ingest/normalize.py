import re
import string
from difflib import SequenceMatcher

ABBREVIATIONS = {
    "govt": "government",
    "sch": "school",
}


def normalize_name(name):
    name = name.lower().translate(str.maketrans("", "", string.punctuation))
    words = name.split()
    words = [ABBREVIATIONS.get(word, word) for word in words]
    return " ".join(words)


def similarity(a, b):
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


class UnionFind:
    def __init__(self, items):
        self.parent = {item: item for item in items}

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def cluster_names(names, threshold=0.85):
    names = list(dict.fromkeys(names))
    uf = UnionFind(names)

    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if similarity(a, b) >= threshold:
                uf.union(a, b)

    clusters = {}
    for name in names:
        clusters.setdefault(uf.find(name), []).append(name)

    return [
        {
            "canonical": max(group, key=lambda name: (len(name), name)),
            "variants": group,
        }
        for group in clusters.values()
    ]
