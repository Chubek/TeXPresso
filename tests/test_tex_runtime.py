"""Runtime ABI checks run on any system with TeX installed."""
import pathlib
import shutil
import subprocess
import unittest

HERE = pathlib.Path(__file__).resolve().parent


@unittest.skipUnless(shutil.which("tex"), "plain TeX binary is unavailable")
class TexRuntimeTest(unittest.TestCase):
    def tex(self, filename):
        p = subprocess.run(
            ["tex", "-interaction=nonstopmode", "-halt-on-error", filename],
            cwd=HERE,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("No pages of output", p.stdout)
        return p.stdout

    def test_type_tags_and_escaped_output(self):
        out = self.tex("runtime-smoke.tex")
        for needle in [
            "TEXPRESSO-SMOKE:49",
            "TEXPRESSO-ZERO-IS-TRUE:1",
            "TEXPRESSO-FALSE-IS-FALSE:0",
            "#f",
            "A%B{C}D",
        ]:
            self.assertIn(needle, out)

    def test_metacharacter_escaping(self):
        self.assertIn(r"A#B$C&D_E^F~G\H%I{J}K", self.tex("runtime-escaping.tex"))

    def test_multiple_named_functions(self):
        out = self.tex("runtime-multi-function.tex")
        self.assertIn("Hello from TeXPresso!", out)
        self.assertIn("144", out)

    def test_while_intrinsic_abi(self):
        self.assertIn("\n5\n", self.tex("runtime-while.tex"))

    def test_recursive_activation_records(self):
        self.assertIn("TEXPRESSO-FACTORIAL:720", self.tex("runtime-recursion.tex"))
