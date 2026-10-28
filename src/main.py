"""Точка входа: инструмент визуализации графа зависимостей."""

import sys

from config import ConfigError, format_config, parse_config

ERROR_EXIT_CODE = 1


def main(argv=None):
    """Запустить приложение. Вернуть код завершения."""
    try:
        config = parse_config(argv)
    except ConfigError as error:
        print(f"ошибка: {error}", file=sys.stderr)
        return ERROR_EXIT_CODE
    for line in format_config(config):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
