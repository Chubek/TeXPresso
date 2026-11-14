"""Static packaging checks; not a substitute for MuLL compilation."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class PackageTest(unittest.TestCase):
    def test_required_sources_exist(self):
        for source in [
            "mull/driver.mull",
            "mull/texpresso_lexer/Package.mull",
            "mull/texpresso_reader/Package.mull",
            "mull/texpresso_analyzer/Package.mull",
            "mull/texpresso_codegen/Package.mull",
            "runtime/tex82.tex",
            "bin/texpresso",
            "AGENTS.md",
        ]:
            with self.subTest(source=source):
                self.assertGreater((ROOT / source).stat().st_size, 50)

    def test_mull_compiler_is_source_implemented(self):
        lines = sum(len(p.read_text().splitlines()) for p in (ROOT / "mull").rglob("*.mull"))
        self.assertGreater(lines, 500)

    def test_runtime_avoids_document_primitives(self):
        runtime = (ROOT / "runtime" / "tex82.tex").read_text()
        for forbidden in [r"\shipout", r"\setbox", r"\font", r"\hbox", r"\vbox"]:
            # The comment mentions shipout, so examine executable lines only.
            code = "\n".join(line for line in runtime.splitlines() if not line.lstrip().startswith("%"))
            self.assertNotIn(forbidden, code)
