"""Точка входа: инструмент визуализации графа зависимостей."""

import sys

from config import ConfigError, parse_config
from repository import RepositoryError, find_package, load_packages

ERROR_EXIT_CODE = 1


def print_dependencies(package):
    """Вывести все прямые зависимости пакета."""
    if not package.depends:
        print(f"У пакета {package.name} нет прямых зависимостей")
        return
    print(f"Прямые зависимости пакета {package.name}:")
    for dependency in package.depends:
        print(f"  {dependency}")


def run(config):
    """Загрузить репозиторий и вывести зависимости заданного пакета."""
    packages = load_packages(config.repo, config.test_mode)
    print_dependencies(find_package(packages, config.package))


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
