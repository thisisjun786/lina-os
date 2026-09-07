import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from tools import unpack_verified


class DownloadTests(unittest.TestCase):
    def archive(self, mode="file"):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
            member = tarfile.TarInfo("fixture")
            if mode == "symlink":
                member.type = tarfile.SYMTYPE
                member.linkname = "../outside"
            else:
                member.size = 7
            archive.addfile(member, io.BytesIO(b"fixture"))
        return output.getvalue()

    def test_mismatched_checksum_cannot_extract_or_run(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                unpack_verified(self.archive(), "0" * 64, "fixture", Path(directory))
            self.assertFalse((Path(directory) / "fixture").exists())

    def test_archive_symlink_cannot_extract_or_run(self):
        content = self.archive("symlink")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "regular file"):
                unpack_verified(content, hashlib.sha256(content).hexdigest(), "fixture", Path(directory))

    def test_verified_binary_is_extracted(self):
        content = self.archive()
        with tempfile.TemporaryDirectory() as directory:
            output = unpack_verified(content, hashlib.sha256(content).hexdigest(), "fixture", Path(directory))
            self.assertEqual(output.read_bytes(), b"fixture")
            self.assertTrue(output.stat().st_mode & 0o100)
