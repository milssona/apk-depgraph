"""Тесты визуализации графа: Mermaid и ASCII-дерево."""

import unittest

import context

visualize = context.load("visualize")

DIAMOND = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}


class MermaidTest(unittest.TestCase):
    """Описание графа на языке Mermaid."""

    def test_diamond(self):
        """Узлы объявляются, затем перечисляются рёбра."""
        expected = "\n".join(
            [
                "graph TD",
                '    n0["A"]',
                '    n1["B"]',
                '    n2["C"]',
                '    n3["D"]',
                "    n0 --> n1",
                "    n0 --> n2",
                "    n1 --> n3",
                "    n2 --> n3",
            ]
        )
        self.assertEqual(visualize.mermaid_text(DIAMOND), expected)

    def test_single_package(self):
        """Пакет без зависимостей даёт один узел без рёбер."""
        text = visualize.mermaid_text({"zlib": []})
        self.assertEqual(text, 'graph TD\n    n0["zlib"]')

    def test_cycle_has_back_edge(self):
        """Цикл отображается обратным ребром."""
        text = visualize.mermaid_text(CYCLE)
        self.assertIn("    n2 --> n0", text)

    def test_special_characters(self):
        """Имена с дефисом и точкой попадают в подпись узла."""
        text = visualize.mermaid_text({"c-ares": ["lib.so+"], "lib.so+": []})
        self.assertIn('n0["c-ares"]', text)
        self.assertIn('n1["lib.so+"]', text)


class AsciiTreeTest(unittest.TestCase):
    """ASCII-дерево зависимостей."""

    def test_diamond(self):
        """Повторная зависимость помечается и не раскрывается."""
        expected = "\n".join(
            [
                "A",
                "|-- B",
                "|   `-- D",
                "`-- C",
                "    `-- D (повтор)",
            ]
        )
        self.assertEqual(visualize.ascii_tree("A", DIAMOND), expected)

    def test_cycle(self):
        """Цикл обрывается пометкой, дерево конечно."""
        expected = "\n".join(
            ["A", "`-- B", "    `-- C", "        `-- A (повтор)"]
        )
        self.assertEqual(visualize.ascii_tree("A", CYCLE), expected)

    def test_single_package(self):
        """Пакет без зависимостей даёт одну строку."""
        self.assertEqual(visualize.ascii_tree("zlib", {"zlib": []}), "zlib")


if __name__ == "__main__":
    unittest.main()
