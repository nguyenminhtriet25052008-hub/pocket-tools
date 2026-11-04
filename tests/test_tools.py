"""Tests for pocket-tools (stdlib unittest only).  Run:  python -m unittest -v"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import bigfiles  # noqa: E402
import bulkrename  # noqa: E402
import dupfind  # noqa: E402
import jsonq  # noqa: E402
import lanshare  # noqa: E402
import organize  # noqa: E402
import pomodoro  # noqa: E402
import pwgen  # noqa: E402
import resistor  # noqa: E402
import watchrun  # noqa: E402


def write(path, content=b"x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()


class TestDupfind(TempDirTest):
    def test_finds_only_identical_files(self):
        write(os.path.join(self.dir, "a.txt"), b"hello")
        write(os.path.join(self.dir, "sub", "b.txt"), b"hello")
        write(os.path.join(self.dir, "c.txt"), b"world")  # same size, different content
        groups = dupfind.find_duplicates([self.dir])
        self.assertEqual(len(groups), 1)
        self.assertEqual(sorted(os.path.basename(p) for p in groups[0]), ["a.txt", "b.txt"])

    def test_parse_size(self):
        self.assertEqual(dupfind.parse_size("1K"), 1024)
        self.assertEqual(dupfind.parse_size("1.5m"), 1572864)
        self.assertEqual(dupfind.parse_size("42"), 42)


class TestBigfiles(TempDirTest):
    def test_folder_sizes_roll_up(self):
        write(os.path.join(self.dir, "a", "b", "f.bin"), b"x" * 100)
        write(os.path.join(self.dir, "g.bin"), b"x" * 10)
        files, dirs = bigfiles.scan(self.dir)
        self.assertEqual(len(files), 2)
        root = os.path.abspath(self.dir)
        self.assertEqual(dirs[root], 110)
        self.assertEqual(dirs[os.path.join(root, "a")], 100)

    def test_human(self):
        self.assertEqual(bigfiles.human(1536), "1.5 KB")


class TestOrganize(TempDirTest):
    def test_plan_categories(self):
        for name in ("pic.JPG", "song.mp3", "weird.xyz"):
            write(os.path.join(self.dir, name))
        dests = {os.path.basename(s): os.path.basename(os.path.dirname(d)) for s, d in organize.plan(self.dir)}
        self.assertEqual(dests, {"pic.JPG": "Images", "song.mp3": "Audio", "weird.xyz": "Other"})

    def test_unique_path(self):
        write(os.path.join(self.dir, "a.txt"))
        self.assertTrue(organize.unique_path(os.path.join(self.dir, "a.txt")).endswith("a (1).txt"))


class TestBulkrename(unittest.TestCase):
    def test_regex_groups(self):
        self.assertEqual(bulkrename.plan(["IMG_1.jpg", "x.png"], r"IMG_(\d+)", r"trip_\1"),
                         [("IMG_1.jpg", "trip_1.jpg")])

    def test_counter(self):
        self.assertEqual(bulkrename.plan(["b.png", "a.png"], r".*\.png$", "s_{n:02}.png"),
                         [("a.png", "s_01.png"), ("b.png", "s_02.png")])


class TestLanshare(unittest.TestCase):
    def test_parse_multipart(self):
        body = (b"--XY\r\nContent-Disposition: form-data; name=\"f\"; filename=\"C:\\\\tmp\\\\a.txt\"\r\n"
                b"Content-Type: text/plain\r\n\r\nhi there\r\n--XY--\r\n")
        self.assertEqual(list(lanshare.parse_multipart(body, b"XY")), [("a.txt", b"hi there")])

    def test_parse_multipart_binary_without_content_type(self):
        body = b'--XY\r\nContent-Disposition: form-data; name="f"; filename="b.bin"\r\n\r\n\x00\r\n\r\nz\r\n--XY--\r\n'
        self.assertEqual(list(lanshare.parse_multipart(body, b"XY")), [("b.bin", b"\x00\r\n\r\nz")])


class TestPwgen(unittest.TestCase):
    def test_password_has_all_classes(self):
        for _ in range(50):
            pw = pwgen.password(12)
            self.assertEqual(len(pw), 12)
            self.assertTrue(any(c.isupper() for c in pw) and any(c.isdigit() for c in pw))

    def test_passphrase(self):
        self.assertEqual(len(pwgen.passphrase(4).split("-")), 4)


class TestPomodoro(unittest.TestCase):
    def test_format(self):
        self.assertEqual(pomodoro.fmt(125), "02:05")
        self.assertEqual(pomodoro.bar(5, 10, 10), "#####-----")


class TestWatchrun(TempDirTest):
    def test_detects_change(self):
        path = os.path.join(self.dir, "a.py")
        write(path)
        before = watchrun.snapshot([os.path.join(self.dir, "*.py")])
        os.utime(path, (1, 1))
        after = watchrun.snapshot([os.path.join(self.dir, "*.py")])
        self.assertEqual(watchrun.changed(before, after), [path])

    def test_split_argv(self):
        self.assertEqual(watchrun.split_argv(["*.py", "--", "make", "-j"]), (["*.py"], ["make", "-j"]))


class TestResistor(unittest.TestCase):
    def test_decode(self):
        self.assertEqual(resistor.decode(["brown", "black", "red", "gold"]), (1000, 5))
        self.assertEqual(resistor.decode(["yellow", "violet", "black", "brown", "brown"]), (4700, 1))
        self.assertEqual(resistor.decode(["green", "blue", "gold", "silver"]), (5.6, 10))

    def test_encode(self):
        self.assertEqual(resistor.encode("4.7k"), ["yellow", "violet", "red", "gold"])
        self.assertEqual(resistor.encode("1M"), ["brown", "black", "green", "gold"])
        self.assertEqual(resistor.encode("0.47"), ["yellow", "violet", "silver", "gold"])
        self.assertEqual(resistor.encode("220", bands=5), ["red", "red", "black", "black", "brown"])

    def test_roundtrip(self):
        for value in (10, 47, 330, 1000, 2200, 68000, 100000):
            self.assertAlmostEqual(resistor.decode(resistor.encode(str(value)))[0], value)

    def test_ohm(self):
        r = resistor.ohm(V=12, R=470)
        self.assertAlmostEqual(r["I"], 12 / 470)
        self.assertAlmostEqual(r["P"], 144 / 470)


class TestJsonq(unittest.TestCase):
    DATA = {"users": [{"name": "An", "tags": ["a"]}, {"name": "Binh", "tags": []}]}

    def test_paths(self):
        self.assertEqual(jsonq.query(self.DATA, "users[0].name"), "An")
        self.assertEqual(jsonq.query(self.DATA, "users[-1].name"), "Binh")
        self.assertEqual(jsonq.query(self.DATA, "users[*].name"), ["An", "Binh"])
        self.assertEqual(jsonq.query(self.DATA, ""), self.DATA)

    def test_missing(self):
        with self.assertRaises(KeyError):
            jsonq.query(self.DATA, "nope")


if __name__ == "__main__":
    unittest.main()
