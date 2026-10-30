"""Визуализация графа зависимостей: диаграмма Mermaid и ASCII-дерево."""

REPEAT_MARK = " (повтор)"
LAST_BRANCH = "`-- "
MIDDLE_BRANCH = "|-- "
LAST_SPACE = "    "
MIDDLE_SPACE = "|   "


def mermaid_text(graph):
    """Вернуть описание графа на языке диаграмм Mermaid."""
    ids = {name: f"n{number}" for number, name in enumerate(graph)}
    lines = ["graph TD"]
    for name, node in ids.items():
        lines.append(f'    {node}["{name}"]')
    for name, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f"    {ids[name]} --> {ids[dependency]}")
    return "\n".join(lines)


def tree_lines(name, graph, prefix, shown):
    """Вернуть строки ASCII-дерева для зависимостей пакета."""
    lines = []
    dependencies = graph[name]
    for number, dependency in enumerate(dependencies):
        is_last = number == len(dependencies) - 1
        branch = LAST_BRANCH if is_last else MIDDLE_BRANCH
        repeated = dependency in shown
        mark = REPEAT_MARK if repeated else ""
        lines.append(prefix + branch + dependency + mark)
        if repeated:
            continue
        shown.add(dependency)
        space = LAST_SPACE if is_last else MIDDLE_SPACE
        lines.extend(tree_lines(dependency, graph, prefix + space, shown))
    return lines


def ascii_tree(root, graph):
    """Вернуть зависимости пакета в виде ASCII-дерева."""
    lines = [root] + tree_lines(root, graph, "", {root})
    return "\n".join(lines)
