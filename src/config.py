"""Параметры командной строки и их проверка."""

import argparse
import re
from dataclasses import dataclass
from os.path import isfile
from urllib.parse import urlparse

PACKAGE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
SPACE_PATTERN = re.compile(r"\s")
URL_SCHEMES = ("http", "https")


class ConfigError(Exception):
    """Ошибка в значении параметра."""


@dataclass
class Config:
    """Параметры, заданные пользователем."""

    package: str
    repo: str
    test_mode: bool
    ascii_tree: bool
    substring: str


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Граф зависимостей пакета Alpine Linux"
    )
    parser.add_argument(
        "--package", required=True, help="имя анализируемого пакета"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="URL репозитория или путь к файлу тестового репозитория",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="работать с тестовым репозиторием",
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="выводить зависимости в виде ASCII-дерева",
    )
    parser.add_argument(
        "--filter",
        default="",
        dest="substring",
        help="подстрока для фильтрации пакетов",
    )
    return parser


def check_package(name):
    """Проверить имя пакета."""
    if not PACKAGE_PATTERN.match(name):
        raise ConfigError(f"недопустимое имя пакета: {name!r}")


def check_repo(repo, test_mode):
    """Проверить URL репозитория или путь к тестовому файлу."""
    if test_mode:
        if not isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
        return
    parts = urlparse(repo)
    if parts.scheme not in URL_SCHEMES or not parts.netloc:
        raise ConfigError(f"некорректный URL репозитория: {repo}")


def check_substring(text):
    """Проверить подстроку для фильтрации: без пробельных символов."""
    if SPACE_PATTERN.search(text):
        raise ConfigError(f"подстрока не должна содержать пробелов: {text!r}")


def parse_config(argv=None):
    """Разобрать и проверить параметры. Вернуть объект Config."""
    args = build_parser().parse_args(argv)
    check_package(args.package)
    check_repo(args.repo, args.test_mode)
    check_substring(args.substring)
    return Config(
        package=args.package,
        repo=args.repo,
        test_mode=args.test_mode,
        ascii_tree=args.ascii_tree,
        substring=args.substring,
    )
