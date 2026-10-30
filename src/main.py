"""Точка входа: инструмент визуализации графа зависимостей."""

import sys

from config import ConfigError, parse_config
from graph import build_graph, load_order
from repository import RepositoryError, find_package, load_packages

ERROR_EXIT_CODE = 1


def print_graph(root, graph):
    """Вывести граф: в каждой строке пакет и его прямые зависимости."""
    if not graph:
        print(f"Пакет {root} исключён фильтром, граф пуст")
        return
    for name, dependencies in graph.items():
        print(f"{name}: {' '.join(dependencies)}".rstrip())


def print_order(root, graph):
    """Вывести порядок загрузки: по одному пакету в строке."""
    order = load_order(root, graph)
    for number, name in enumerate(order, start=1):
        print(f"{number}. {name}")


def run(config):
    """Загрузить репозиторий, построить и вывести граф зависимостей."""
    packages = load_packages(config.repo, config.test_mode)
    find_package(packages, config.package)
    graph = build_graph(config.package, packages, config.substring)
    if config.load_order:
        print_order(config.package, graph)
    else:
        print_graph(config.package, graph)


def main(argv=None):
    """Запустить приложение. Вернуть код завершения."""
    try:
        run(parse_config(argv))
    except (ConfigError, RepositoryError) as error:
        print(f"ошибка: {error}", file=sys.stderr)
        return ERROR_EXIT_CODE
    return 0


if __name__ == "__main__":
    sys.exit(main())
