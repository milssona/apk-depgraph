"""Загрузка и разбор данных репозитория пакетов Alpine Linux (apk)."""

import io
import tarfile
import urllib.request
import zlib
from dataclasses import dataclass, field

INDEX_NAME = "APKINDEX"
INDEX_ARCHIVE = "APKINDEX.tar.gz"
TIMEOUT_SECONDS = 30
ENCODING = "utf-8"


class RepositoryError(Exception):
    """Ошибка получения или разбора данных репозитория."""


@dataclass
class Package:
    """Описание пакета: имя, версия, зависимости и предоставляемые имена."""

    name: str
    version: str = ""
    depends: list = field(default_factory=list)
    provides: list = field(default_factory=list)


def index_url(repo):
    """Вернуть URL архива индекса для адреса репозитория."""
    return repo.rstrip("/") + "/" + INDEX_ARCHIVE


def download(url):
    """Скачать файл по URL и вернуть его содержимое в виде байтов."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.read()
    except OSError as error:
        message = f"не удалось получить {url}: {error}"
        raise RepositoryError(message) from error


def read_index_text(data):
    """Извлечь текст файла APKINDEX из архива APKINDEX.tar.gz."""
    try:
        with tarfile.open(
            fileobj=io.BytesIO(data), mode="r:gz", ignore_zeros=True
        ) as archive:
            return archive.extractfile(INDEX_NAME).read().decode(ENCODING)
    except (
        tarfile.TarError,
        OSError,
        EOFError,
        KeyError,
        UnicodeError,
        zlib.error,
    ) as error:
        raise RepositoryError("не удалось прочитать индекс APKINDEX") from error


def parse_entry(block):
    """Разобрать блок строк одного пакета. Вернуть Package или None."""
    fields = {}
    for line in block.splitlines():
        key, _, value = line.partition(":")
        fields[key] = value
    name = fields.get("P")
    if not name:
        return None
    return Package(
        name=name,
        version=fields.get("V", ""),
        depends=fields.get("D", "").split(),
        provides=fields.get("p", "").split(),
    )


def parse_index(text):
    """Разобрать текст APKINDEX. Вернуть словарь {имя: Package}."""
    packages = {}
    for block in text.split("\n\n"):
        package = parse_entry(block.strip())
        if package is not None:
            packages[package.name] = package
    return packages


def parse_test_repo(text):
    """Разобрать тестовый репозиторий: строки вида «A: B C»."""
    packages = {}
    for line in text.splitlines():
        name, _, rest = line.partition(":")
        name = name.strip()
        if name:
            packages[name] = Package(name=name, depends=rest.split())
    return packages


def load_test_repo(path):
    """Прочитать файл тестового репозитория."""
    try:
        with open(path, encoding=ENCODING) as file:
            return parse_test_repo(file.read())
    except OSError as error:
        raise RepositoryError(f"не удалось прочитать {path}") from error


def load_packages(repo, test_mode):
    """Получить пакеты репозитория: из URL или из тестового файла."""
    if test_mode:
        return load_test_repo(repo)
    data = download(index_url(repo))
    return parse_index(read_index_text(data))


def find_package(packages, name):
    """Найти пакет по имени или сообщить, что его нет в репозитории."""
    package = packages.get(name)
    if package is None:
        raise RepositoryError(f"пакет не найден в репозитории: {name}")
    return package
