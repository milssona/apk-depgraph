"""Тесты загрузки и разбора данных репозитория."""

import gzip
import io
import os
import tarfile
import tempfile
import unittest

import context

repository = context.load("repository")

SAMPLE_INDEX = (
    "C:Q1abc=\nP:nginx\nV:1.26.2-r0\n"
    "D:pcre2 so:libc.musl-x86_64.so.1 zlib\n"
    "p:cmd:nginx=1.26.2-r0\n\n"
    "P:zlib\nV:1.3.1-r1\np:so:libz.so.1=1.3.1\n\n"
)


def make_archive(files):
    """Собрать tar.gz в памяти из словаря {имя: текст}."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, text in files.items():
            data = text.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


class ParseIndexTest(unittest.TestCase):
    """Разбор текста APKINDEX."""

    def test_reads_fields(self):
        """Имя, версия, зависимости и provides разбираются."""
        packages = repository.parse_index(SAMPLE_INDEX)
        nginx = packages["nginx"]
        self.assertEqual(nginx.version, "1.26.2-r0")
        self.assertEqual(
            nginx.depends, ["pcre2", "so:libc.musl-x86_64.so.1", "zlib"]
        )
        self.assertEqual(nginx.provides, ["cmd:nginx=1.26.2-r0"])

    def test_package_without_depends(self):
        """У пакета без поля D список зависимостей пуст."""
        packages = repository.parse_index(SAMPLE_INDEX)
        self.assertEqual(packages["zlib"].depends, [])

    def test_find_missing_package(self):
        """Отсутствующий пакет вызывает ошибку репозитория."""
        packages = repository.parse_index(SAMPLE_INDEX)
        with self.assertRaises(repository.RepositoryError):
            repository.find_package(packages, "absent")


class ArchiveTest(unittest.TestCase):
    """Чтение архива индекса."""

    def test_read_index_text(self):
        """Текст APKINDEX извлекается из tar.gz."""
        data = make_archive({"APKINDEX": SAMPLE_INDEX})
        self.assertEqual(repository.read_index_text(data), SAMPLE_INDEX)

    def test_signature_before_index(self):
        """Подпись перед индексом не мешает чтению."""
        data = make_archive({".SIGN.RSA.key": "x", "APKINDEX": SAMPLE_INDEX})
        text = repository.read_index_text(data)
        self.assertIn("P:nginx", text)

    def test_not_an_archive(self):
        """Произвольные байты дают ошибку репозитория."""
        with self.assertRaises(repository.RepositoryError):
            repository.read_index_text(b"not an archive")

    def test_no_index_inside(self):
        """Архив без файла APKINDEX даёт ошибку репозитория."""
        data = make_archive({"other": "text"})
        with self.assertRaises(repository.RepositoryError):
            repository.read_index_text(data)

    def test_broken_gzip(self):
        """Обрезанный gzip даёт ошибку репозитория."""
        data = gzip.compress(b"x" * 2000)[:20]
        with self.assertRaises(repository.RepositoryError):
            repository.read_index_text(data)


class UrlAndTestRepoTest(unittest.TestCase):
    """Адрес индекса и тестовый репозиторий."""

    def test_index_url(self):
        """К адресу репозитория добавляется имя архива."""
        self.assertEqual(
            repository.index_url("http://h/main/x86_64/"),
            "http://h/main/x86_64/APKINDEX.tar.gz",
        )

    def test_load_test_repo(self):
        """Файл тестового репозитория читается по строкам."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "repo.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("A: B C\nB: D\nD:\n")
            packages = repository.load_packages(path, True)
        self.assertEqual(packages["A"].depends, ["B", "C"])
        self.assertEqual(packages["D"].depends, [])

    def test_unreachable_url(self):
        """Недоступный адрес даёт ошибку репозитория."""
        with self.assertRaises(repository.RepositoryError):
            repository.download("http://127.0.0.1:9/APKINDEX.tar.gz")


if __name__ == "__main__":
    unittest.main()
