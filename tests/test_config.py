"""Тесты разбора и проверки параметров командной строки."""

import contextlib
import io
import os
import tempfile
import unittest

import context

settings = context.load("config")

URL = "https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64"


class ParseConfigTest(unittest.TestCase):
    """Проверки функции parse_config."""

    def assert_rejected(self, argv):
        """Проверить, что параметры отвергаются ошибкой настройки."""
        with self.assertRaises(settings.ConfigError):
            settings.parse_config(argv)

    def test_url_mode(self):
        """Обычный режим: URL принимается, остальное по умолчанию."""
        result = settings.parse_config(["--package", "nginx", "--repo", URL])
        self.assertEqual(result.package, "nginx")
        self.assertEqual(result.repo, URL)
        self.assertFalse(result.test_mode)
        self.assertFalse(result.ascii_tree)
        self.assertEqual(result.substring, "")

    def test_test_mode(self):
        """Тестовый режим: путь к существующему файлу принимается."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "repo.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("A: B\n")
            result = settings.parse_config(
                ["--package", "A", "--repo", path, "--test-mode"]
            )
        self.assertTrue(result.test_mode)

    def test_bad_package(self):
        """Имя пакета с пробелом отвергается."""
        self.assert_rejected(["--package", "bad name", "--repo", URL])

    def test_bad_url(self):
        """URL с неподдерживаемой схемой отвергается."""
        self.assert_rejected(
            ["--package", "nginx", "--repo", "ftp://host/alpine"]
        )

    def test_missing_test_file(self):
        """Несуществующий файл тестового репозитория отвергается."""
        self.assert_rejected(
            ["--package", "A", "--repo", "missing.txt", "--test-mode"]
        )

    def test_bad_filter(self):
        """Подстрока с пробелом отвергается."""
        self.assert_rejected(
            ["--package", "nginx", "--repo", URL, "--filter", "a b"]
        )

    def test_missing_required(self):
        """Без обязательных параметров разбор завершается."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                settings.parse_config([])


class FormatConfigTest(unittest.TestCase):
    """Проверки функции format_config."""

    def test_key_value(self):
        """Параметры выводятся в формате ключ=значение."""
        result = settings.parse_config(["--package", "nginx", "--repo", URL])
        lines = settings.format_config(result)
        self.assertIn("package=nginx", lines)
        self.assertIn(f"repo={URL}", lines)
        self.assertIn("test_mode=False", lines)


if __name__ == "__main__":
    unittest.main()
