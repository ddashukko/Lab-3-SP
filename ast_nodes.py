"""Вузол AST."""

class Node:
    def __init__(self, kind, value=None, children=None, line=0, **attrs):
        self.kind = kind
        self.value = value
        self.children = [c for c in (children or [])]
        self.line = line
        self.attrs = attrs

    def to_dict(self):
        label = self.kind if self.value is None else f"{self.kind}: {self.value}"
        if "type" in self.attrs:
            label += f" <{self.attrs['type']}>"
        if "ret" in self.attrs:
            label += f" -> {self.attrs['ret']}"
        return {"kind": self.kind, "name": label, "line": self.line,
                "children": [c.to_dict() for c in self.children]}

    def dump(self, indent=0):
        s = "  " * indent + self.to_dict()["name"] + "\n"
        for c in self.children:
            s += c.dump(indent + 1)
        return s
