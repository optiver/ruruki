"""
Classes for handling locking and ownerships.
"""
import os
import os.path
from ruruki import interfaces

if os.name == 'nt':
    import msvcrt    # pylint: disable=import-error
else:
    import fcntl


class Lock(interfaces.ILock):
    """
    Base locking class.

    See :class:`~.ILock` for doco.
    """

    def __init__(self):
        self._locked = False

    @property
    def locked(self):
        """
        Return the status of the lock.

        :returns: True if the lock is acquired.
        :rtype: :class:`bool`
        """
        return self._locked

    def acquire(self):
        if self._locked is True:
            raise interfaces.AcquireError(
                "Failed to acquire lock."
            )
        self._locked = True

    def release(self):
        if self.locked is False:
            raise interfaces.ReleaseError(
                "Failed releasing lock."
            )
        self._locked = False

    def __del__(self):
        if self.locked is True:
            self.release()

    def __enter__(self):
        lock = self
        lock.acquire()
        return lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class FileLock(Lock):
    """
    File based locking.

    :param filename: Filename to create a lock on.
    :type filename: :class:`str`
    """

    def __init__(self, filename):
        super(FileLock, self).__init__()
        self.filename = filename
        self._fd = None

    def acquire(self):
        try:
            self._fd = open(self.filename, "w")
            if os.name == 'nt':
                msvcrt.locking(self._fd.fileno(), msvcrt.LK_NBLCK, -1)
            else:
                fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise interfaces.AcquireError(
                "Failed acquiring a lock on {0!r}.".format(self.filename)
            )
        super(FileLock, self).acquire()

    def _close_file(self):
        if self._fd is not None:
            self._fd.close()

    def release(self):
        self._close_file()
        super(FileLock, self).release()

    def __del__(self):
        self._close_file()
        super(FileLock, self).__del__()


class DirectoryLock(Lock):
    """
    Directory based locking.

    :param path: Path that you are locking.
    :type path: :class:`str`
    """

    def __init__(self, path):
        super(DirectoryLock, self).__init__()
        self.path = path
        self.filename = os.path.join(path, ".lock")
        self._filelock = FileLock(self.filename)

    @property
    def locked(self):
        """
        Return the status of the lock.

        :returns: True if the lock is acquired.
        :rtype: :class:`bool`
        """
        return self._filelock.locked

    def acquire(self):
        try:
            self._filelock.acquire()
        except interfaces.AcquireError:
            raise interfaces.AcquireError(
                "Failed acquiring a lock for path {0!r}.".format(self.path)
            )

    def release(self):
        try:
            self._filelock.release()
        except interfaces.ReleaseError:
            raise interfaces.ReleaseError(
                "Failed releasing the lock for path {0!r}.".format(self.path)
            )
        finally:
            if os.path.isfile(self.filename):
                os.remove(self.filename)
