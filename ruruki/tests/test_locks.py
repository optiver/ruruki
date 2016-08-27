# pylint: disable=missing-docstring
import os.path
import tempfile
import unittest
from ruruki import interfaces
from ruruki import locks


class TestBaseLock(unittest.TestCase):
    def setUp(self):
        self.lock = locks.Lock()

    def test_acquire(self):
        self.lock.acquire()
        self.assertEqual(self.lock.locked, True)

    def test_acquire_already_locked(self):
        self.lock.acquire()
        self.assertRaises(
            interfaces.AcquireError,
            self.lock.acquire
        )

    def test_release(self):
        self.lock.acquire()
        self.lock.release()
        self.assertEqual(self.lock.locked, False)

    def test_release_not_locked(self):
        self.assertRaises(
            interfaces.ReleaseError,
            self.lock.release
        )

    def test_delete_releases_lock(self):
        self.lock.acquire()
        self.lock.__del__()
        self.assertEqual(self.lock.locked, False)

    def test_delete_not_locked(self):
        self.lock.__del__()
        self.assertEqual(self.lock.locked, False)

    def test_enter_contex_manager(self):
        with locks.Lock() as lock:
            self.assertEqual(lock.locked, True)

    def test_exit_contex_manager(self):
        context_manager = locks.Lock()
        lock = context_manager.__enter__()
        lock.__exit__(None, None, None)
        self.assertEqual(lock.locked, False)


class TestFileLock(unittest.TestCase):
    def setUp(self):
        self.filename = tempfile.NamedTemporaryFile()
        self.lock = locks.FileLock(self.filename.name)

    def test_acquire(self):
        self.lock.acquire()
        self.assertEqual(self.lock.locked, True)

    def test_acquire_flock_error(self):
        filename = tempfile.NamedTemporaryFile()
        with locks.FileLock(filename.name):
            lock = locks.FileLock(filename.name)
            self.assertRaises(
                interfaces.AcquireError,
                lock.acquire
            )

    def test_acquire_already_locked(self):
        self.lock.acquire()
        self.assertRaises(
            interfaces.AcquireError,
            self.lock.acquire,
        )

    def test_release(self):
        self.lock.acquire()
        self.lock.release()
        self.assertEqual(self.lock.locked, False)

    def test_release_not_locked(self):
        self.assertRaises(
            interfaces.ReleaseError,
            self.lock.release,
        )

    def test_delete_releases_lock(self):
        self.lock.acquire()
        self.lock.__del__()
        self.assertEqual(self.lock.locked, False)

    def test_delete_not_locked(self):
        self.lock.__del__()
        self.assertEqual(self.lock.locked, False)

    def test_enter_contex_manager(self):
        with locks.FileLock(self.filename.name) as lock:
            self.assertEqual(lock.locked, True)

    def test_exit_contex_manager(self):
        context_manager = locks.FileLock(self.filename.name)
        lock = context_manager.__enter__()
        lock.__exit__(None, None, None)
        self.assertEqual(lock.locked, False)


class TestDirectoryLock(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.mkdtemp()
        self.lock = locks.DirectoryLock(self.path)

    def test_acquire(self):
        self.lock.acquire()
        self.assertEqual(self.lock.locked, True)
        self.assertEqual(
            os.path.isfile(self.lock.filename),
            True,
        )

    def test_acquire_already_locked(self):
        self.lock.acquire()
        self.assertRaises(
            interfaces.AcquireError,
            self.lock.acquire,
        )

    def test_release(self):
        self.lock.acquire()
        self.lock.release()
        self.assertEqual(self.lock.locked, False)
        self.assertEqual(
            os.path.isfile(self.lock.filename),
            False,
        )

    def test_release_not_locked(self):
        self.assertRaises(
            interfaces.ReleaseError,
            self.lock.release,
        )

    def test_release_file_not_found(self):
        self.lock.acquire()
        os.remove(self.lock.filename)
        self.lock.release()
        self.assertEqual(self.lock.locked, False)

    def test_delete_releases_lock(self):
        self.lock.acquire()
        self.lock.__del__()
        self.assertEqual(self.lock.locked, False)
        self.assertEqual(
            os.path.isfile(self.lock.filename),
            False,
        )

    def test_delete_not_locked(self):
        self.lock.__del__()
        self.assertEqual(self.lock.locked, False)
        self.assertEqual(
            os.path.isfile(self.lock.filename),
            False,
        )

    def test_enter_contex_manager(self):
        with locks.DirectoryLock(self.path) as lock:
            self.assertEqual(lock.locked, True)
            self.assertEqual(
                os.path.isfile(lock.filename),
                True,
            )

    def test_exit_contex_manager(self):
        context_manager = locks.DirectoryLock(self.path)
        lock = context_manager.__enter__()
        lock.__exit__(None, None, None)
        self.assertEqual(lock.locked, False)
        self.assertEqual(
            os.path.isfile(lock.filename),
            False,
        )
