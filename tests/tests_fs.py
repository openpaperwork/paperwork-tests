import os
import unittest
import tempfile

import paperwork_backend.fs


class TestGio(unittest.TestCase):
    def setUp(self):
        self.fs = paperwork_backend.fs.GioFileSystem()

    def test_safe(self):
        self.assertEqual(self.fs.safe("file:///home/jflesch/papers"),
                         "file:///home/jflesch/papers")
        self.assertEqual(self.fs.safe("/home/jflesch/papers"),
                         "file:///home/jflesch/papers")

    def test_basename(self):
        self.assertEqual(self.fs.basename("file:///home/jflesch/toto.txt"),
                         "toto.txt")
        self.assertEqual(self.fs.basename("file:///home/jflesch/toto%21.txt"),
                         "toto!.txt")

    def test_dirname(self):
        self.assertEqual(self.fs.dirname("file:///home/jflesch/toto.txt"),
                         "file:///home/jflesch")

    def test_join(self):
        self.assertEqual(self.fs.join("file:///home/jflesch/kwain", "toto.txt"),
                         "file:///home/jflesch/kwain/toto.txt")

    def test_readwrite_binary(self):
        name = None
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            name = tmp_file.name
        uri_name = self.fs.safe(name)
        fd = None

        with self.fs.open(uri_name, 'wb') as _fd:
            self.assertIsNotNone(_fd)
            fd = _fd
            fd.write(b"TEST_LINE\n")
        self.assertTrue(fd.closed)

        with self.fs.open(uri_name, 'rb') as _fd:
            self.assertIsNotNone(_fd)
            fd = _fd
            r = fd.read()
            self.assertEqual(r, b"TEST_LINE\n")
        self.assertTrue(fd.closed)

        os.unlink(name)

    def test_readwrite_utf(self):
        name = None
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            name = tmp_file.name
        uri_name = self.fs.safe(name)
        fd = None

        with self.fs.open(uri_name, 'w') as _fd:
            self.assertIsNotNone(_fd)
            fd = _fd
            fd.write("TEST_LINE\n")
        self.assertTrue(fd.closed)

        with self.fs.open(uri_name, 'r') as _fd:
            self.assertIsNotNone(_fd)
            fd = _fd
            r = fd.read()
            self.assertEqual(r, "TEST_LINE\n")
        self.assertTrue(fd.closed)

        os.unlink(name)

    def tearDown(self):
        pass
