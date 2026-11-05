"""Точка входа: инструмент визуализации графа зависимостей."""

import sys
import webbrowser
from pathlib import Path

from config import ConfigError, parse_config
from graph import build_graph, load_order
from repository import RepositoryError, find_package, load_packages
from plantuml import plantuml_text, save_image
from visualize import ascii_tree, mermaid_text

ERROR_EXIT_CODE = 1


def print_graph(root, graph, config):
    """Вывести граф на языке PlantUML или Mermaid и, если нужно, дерево."""
    if not graph:
        print(f"Пакет {root} исключён фильтром, граф пуст")
        return
    if config.plantuml or config.image:
        print(plantuml_text(graph))
    else:
        print(mermaid_text(graph))
    if config.ascii_tree:
        print()
        print(ascii_tree(root, graph))


def make_image(graph, config):
    """Получить картинку от сервера PlantUML, сохранить и открыть её."""
    save_image(config.server, plantuml_text(graph), config.image)
    print(f"Картинка сохранена: {config.image}")
    webbrowser.open(Path(config.image).resolve().as_uri())


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
        print_graph(config.package, graph, config)
        if config.image and graph:
            make_image(graph, config)


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
