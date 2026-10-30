"""Тесты построения графа зависимостей."""

import unittest

import context

graph = context.load("graph")
repository = context.load("repository")


def make_packages(text):
    """Собрать пакеты из текста тестового репозитория."""
    return repository.parse_test_repo(text)


class BuildGraphTest(unittest.TestCase):
    """Транзитивные зависимости, циклы и фильтр."""

    def test_transitive(self):
        """В граф попадают зависимости зависимостей."""
        packages = make_packages("A: B\nB: C\nC:\n")
        result = graph.build_graph("A", packages)
        self.assertEqual(result, {"A": ["B"], "B": ["C"], "C": []})

    def test_shared_dependency_once(self):
        """Общая зависимость обходится один раз."""
        packages = make_packages("A: B C\nB: D\nC: D\nD:\n")
        result = graph.build_graph("A", packages)
        self.assertEqual(sorted(result), ["A", "B", "C", "D"])

    def test_cycle(self):
        """Цикл не приводит к бесконечной рекурсии."""
        packages = make_packages("A: B\nB: C\nC: A\n")
        result = graph.build_graph("A", packages)
        self.assertEqual(result["C"], ["A"])
        self.assertEqual(len(result), 3)

    def test_self_dependency(self):
        """Зависимость пакета от самого себя отбрасывается."""
        packages = make_packages("A: A B\nB:\n")
        self.assertEqual(graph.build_graph("A", packages)["A"], ["B"])

    def test_filter(self):
        """Пакеты с подстрокой в имени не учитываются вместе с ветвью."""
        packages = make_packages("A: B C\nB: D\nC:\nD:\n")
        result = graph.build_graph("A", packages, "B")
        self.assertEqual(result, {"A": ["C"], "C": []})

    def test_filter_root(self):
        """Корневой пакет с подстрокой даёт пустой граф."""
        packages = make_packages("A:\n")
        self.assertEqual(graph.build_graph("A", packages, "A"), {})


class ResolveTest(unittest.TestCase):
    """Разбор записей зависимостей формата apk."""

    def test_provides_and_versions(self):
        """Записи so: и ограничения версий сопоставляются с пакетами."""
        text = (
            "P:app\nV:1\nD:so:libz.so.1 lib=1.0 !bad >=x\n\n"
            "P:zlib\nV:1\np:so:libz.so.1=1.3\n\n"
            "P:lib\nV:1.0\n\n"
        )
        packages = repository.parse_index(text)
        result = graph.build_graph("app", packages)
        self.assertEqual(result["app"], ["zlib", "lib"])

    def test_unknown_dependency_dropped(self):
        """Зависимость, которой нет в репозитории, пропускается."""
        packages = make_packages("A: Z B\nB:\n")
        self.assertEqual(graph.build_graph("A", packages)["A"], ["B"])


class LoadOrderTest(unittest.TestCase):
    """Порядок загрузки: зависимости раньше зависящих от них пакетов."""

    def order(self, text, root="A", substring=""):
        """Построить граф и вернуть порядок загрузки корня."""
        packages = make_packages(text)
        result = graph.build_graph(root, packages, substring)
        return graph.load_order(root, result)

    def test_chain(self):
        """Цепочка загружается от конца к началу."""
        self.assertEqual(self.order("A: B\nB: C\nC:\n"), ["C", "B", "A"])

    def test_diamond(self):
        """Общая зависимость загружается один раз и до обоих пакетов."""
        text = "A: B C\nB: D\nC: D\nD:\n"
        self.assertEqual(self.order(text), ["D", "B", "C", "A"])

    def test_cycle(self):
        """Цикл не зацикливает вывод, каждый пакет встречается один раз."""
        result = self.order("A: B\nB: C\nC: A\n")
        self.assertEqual(result, ["C", "B", "A"])

    def test_filter(self):
        """Отфильтрованные пакеты в порядок загрузки не попадают."""
        text = "A: B C\nB: D\nC:\nD:\n"
        self.assertEqual(self.order(text, substring="B"), ["C", "A"])

    def test_root_filtered(self):
        """Если корень отфильтрован, порядок пуст."""
        self.assertEqual(self.order("A:\n", substring="A"), [])


if __name__ == "__main__":
    unittest.main()
