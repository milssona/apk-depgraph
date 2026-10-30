"""Построение графа зависимостей обходом в глубину (DFS)."""

import re

VERSION_SIGNS = re.compile(r"[<>=~]")
CONFLICT_MARK = "!"


def clean_name(token):
    """Убрать из записи зависимости ограничение версии."""
    return VERSION_SIGNS.split(token, maxsplit=1)[0]


def build_provides(packages):
    """Построить словарь {предоставляемое имя: имя пакета}."""
    provides = {}
    for package in packages.values():
        for item in package.provides:
            provides.setdefault(clean_name(item), package.name)
    for name in packages:
        provides[name] = name
    return provides


def resolve(token, provides):
    """Найти пакет, которому соответствует запись зависимости."""
    if token.startswith(CONFLICT_MARK):
        return None
    return provides.get(clean_name(token))


def direct_dependencies(package, provides, substring):
    """Вернуть имена пакетов-зависимостей без повторов и без фильтра."""
    result = []
    for token in package.depends:
        name = resolve(token, provides)
        if name is None or name == package.name or name in result:
            continue
        if substring and substring in name:
            continue
        result.append(name)
    return result


def visit(name, context, graph):
    """Рекурсивный DFS: добавить пакет и его зависимости в граф."""
    packages, provides, substring = context
    if name in graph:
        return
    graph[name] = direct_dependencies(packages[name], provides, substring)
    for dependency in graph[name]:
        visit(dependency, context, graph)


def build_graph(root, packages, substring=""):
    """Построить граф зависимостей пакета как словарь {имя: [имена]}."""
    graph = {}
    if substring and substring in root:
        return graph
    context = (packages, build_provides(packages), substring)
    visit(root, context, graph)
    return graph


def visit_order(name, graph, seen, order):
    """Рекурсивный DFS: добавить зависимости пакета, затем сам пакет."""
    seen.add(name)
    for dependency in graph[name]:
        if dependency not in seen:
            visit_order(dependency, graph, seen, order)
    order.append(name)


def load_order(root, graph):
    """Вернуть порядок загрузки: зависимости идут раньше пакетов."""
    order = []
    if root in graph:
        visit_order(root, graph, set(), order)
    return order
