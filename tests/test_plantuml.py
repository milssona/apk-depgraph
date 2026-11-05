"""Тесты PlantUML: описание графа, кодирование и запрос к серверу."""

import http.server
import os
import tempfile
import threading
import unittest

import context

plantuml = context.load("plantuml")
repository = context.load("repository")

DIAMOND = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
DOC_EXAMPLE = "SyfFKj2rKt3CoKnELR1Io4ZDoSa70000"
FAKE_IMAGE = b"\x89PNG fake image"
LOCALHOST = "127.0.0.1"


class FakeServer(http.server.BaseHTTPRequestHandler):
    """Поддельный сервер PlantUML: запоминает путь запроса."""

    last_path = ""
    last_agent = ""

    def do_GET(self):
        """Ответить картинкой на любой запрос."""
        FakeServer.last_path = self.path
        FakeServer.last_agent = self.headers.get("User-Agent", "")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(FAKE_IMAGE)

    def log_message(self, *args):
        """Не печатать записи о запросах в консоль."""


class PlantumlTextTest(unittest.TestCase):
    """Описание графа на языке PlantUML."""

    def test_diamond(self):
        """Узлы объявляются, затем перечисляются рёбра."""
        expected = "\n".join(
            [
                "@startuml",
                'rectangle "A" as n0',
                'rectangle "B" as n1',
                'rectangle "C" as n2',
                'rectangle "D" as n3',
                "n0 --> n1",
                "n0 --> n2",
                "n1 --> n3",
                "n2 --> n3",
                "@enduml",
            ]
        )
        self.assertEqual(plantuml.plantuml_text(DIAMOND), expected)

    def test_single_package(self):
        """Пакет без зависимостей даёт один узел без рёбер."""
        text = plantuml.plantuml_text({"zlib": []})
        self.assertEqual(text, '@startuml\nrectangle "zlib" as n0\n@enduml')

    def test_special_characters(self):
        """Имена с дефисом и плюсом попадают в подпись в кавычках."""
        text = plantuml.plantuml_text({"c-ares": ["lib+"], "lib+": []})
        self.assertIn('rectangle "c-ares" as n0', text)
        self.assertIn('rectangle "lib+" as n1', text)


class EncodeTest(unittest.TestCase):
    """Кодирование текста для адреса запроса."""

    def test_documentation_example(self):
        """Результат совпадает с примером из документации PlantUML."""
        self.assertEqual(
            plantuml.encode_text("Bob -> Alice : hello"), DOC_EXAMPLE
        )

    def test_only_allowed_symbols(self):
        """В закодированном тексте нет символов, мешающих адресу."""
        encoded = plantuml.encode_text(plantuml.plantuml_text(DIAMOND))
        allowed = plantuml.PLANTUML_ALPHABET.decode("ascii")
        self.assertTrue(set(encoded) <= set(allowed))

    def test_image_url(self):
        """Адрес собирается из сервера, формата и закодированного текста."""
        url = plantuml.image_url("http://host/plantuml/", "Bob -> Alice")
        start = "http://host/plantuml/png/"
        self.assertTrue(url.startswith(start))
        encoded = plantuml.encode_text("Bob -> Alice")
        self.assertEqual(url[len(start) :], encoded)


class ServerTest(unittest.TestCase):
    """Запрос к серверу (поддельный сервер на своём компьютере)."""

    @classmethod
    def setUpClass(cls):
        """Запустить поддельный сервер в отдельном потоке."""
        cls.server = http.server.HTTPServer((LOCALHOST, 0), FakeServer)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.address = f"http://{LOCALHOST}:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        """Остановить поддельный сервер."""
        cls.server.shutdown()
        cls.server.server_close()

    def test_fetch_image(self):
        """Картинка приходит как есть, запрос идёт по адресу /png/..."""
        data = plantuml.fetch_image(self.address, "Bob -> Alice")
        self.assertEqual(data, FAKE_IMAGE)
        self.assertTrue(FakeServer.last_path.startswith("/png/"))

    def test_user_agent_is_set(self):
        """Запрос идёт со своим User-Agent, а не стандартным у Python."""
        plantuml.fetch_image(self.address, "Bob -> Alice")
        self.assertEqual(FakeServer.last_agent, repository.USER_AGENT)

    def test_save_image(self):
        """Картинка записывается в файл."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "graph.png")
            plantuml.save_image(self.address, "Bob -> Alice", path)
            with open(path, "rb") as image_file:
                self.assertEqual(image_file.read(), FAKE_IMAGE)

    def test_unreachable_server(self):
        """Недоступный сервер даёт понятную ошибку."""
        with self.assertRaises(repository.RepositoryError):
            plantuml.fetch_image("http://127.0.0.1:9", "Bob -> Alice")


if __name__ == "__main__":
    unittest.main()
