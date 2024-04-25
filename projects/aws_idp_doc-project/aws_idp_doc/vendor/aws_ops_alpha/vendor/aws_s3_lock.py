# -*- coding: utf-8 -*-

"""
This module provides a distributed lock using AWS S3 backend.

Requirements::

    python>=3.7
    boto3

Usage:

.. code-block:: python

    import boto3
    from aws_s3_lock.py import Lock, Vault, get_utc_now, AlreadyLockedError

    s3_client = boto3.client("s3")

    # define a vault backend
    vault = Vault(bucket="my-bucket", key="my-task.json", expire=900, wait=1.0)

    # acquire the lock before doing any task
    lock = vault.acquire(s3_client) # or vault.acquire(s3_client, owner="alice")

    # do yor task that requires the distributed lock here
    ...

    # release the lock after the task is done
    vault.release(s3_client, lock)
"""

import typing as T
import json
import time
import uuid
import dataclasses
from datetime import datetime, timezone

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client

__version__ = "0.1.1"

def get_utc_now() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class AlreadyLockedError(RuntimeError):
    pass


@dataclasses.dataclass
class Lock:
    expire: int = dataclasses.field()
    lock_time: str = dataclasses.field()
    release_time: T.Optional[str] = dataclasses.field()
    owner: T.Optional[str] = dataclasses.field()

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "Lock":
        return cls(**json.loads(json_str))

    @property
    def lock_datetime(self) -> datetime:
        return datetime.fromisoformat(self.lock_time)

    def is_expired(self, utc_now: datetime) -> bool:
        return (utc_now - self.lock_datetime).total_seconds() >= self.expire

    def is_locked(
        self,
        utc_now: datetime,
        expect_owner: str,
    ) -> bool:
        """
        From the expect_owner point of view, is the lock locked?

        - if the lock has no owner, then it is NOT LOCKED
        - if the lock's owner matches the expected owner, then it is NOT LOCKED
        - if the lock's owner is not the expected owner:
            - if the lock is expired, then it is NOT LOCKED
            - if the lock is not expired, then it is LOCKED
        """
        if self.owner is None:
            return False

        if self.owner == expect_owner:
            return False
        else:
            if self.is_expired(utc_now=utc_now):
                return False
            else:
                return True


@dataclasses.dataclass
class Vault:
    """
    A vault is an S3 object to store a lock.

    :param bucket: the S3 bucket.
    :param key: the S3 key.
    :param expire: how long the lock will expire in seconds.
    :param wait: how long we should wait after we thought we successfully
        acquired the lock, before actually doing any task.
    """

    bucket: str = dataclasses.field()
    key: str = dataclasses.field()
    expire: int = dataclasses.field()
    wait: float = dataclasses.field(default=1.0)

    def _read(self, s3_client: "S3Client") -> Lock:
        try:
            response = s3_client.get_object(Bucket=self.bucket, Key=self.key)
            return Lock.from_json(response["Body"].read().decode("utf-8"))
        except Exception as e:
            if "NoSuchKey" in str(e):
                lock = Lock(
                    expire=self.expire,
                    lock_time=EPOCH.isoformat(),
                    release_time=None,
                    owner=None,
                )
                self._write(s3_client=s3_client, lock=lock)
                return lock
            else:  # pragma: no cover
                raise e

    def _write(self, s3_client: "S3Client", lock: Lock):
        s3_client.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=lock.to_json(),
            ContentType="application/json",
        )

    def acquire(self, s3_client: "S3Client", owner: T.Optional[str] = None) -> Lock:
        """
        The owner tries to acquire the lock.

        - If failed, raise AlreadyLockedError.
        - If the lock is already owned by the owner, and still not expired, then
            refresh lock_time.

        :param s3_client:
        :param owner: the owner of the lock. If None, then a random uuid will be used.
        """
        if owner is None:
            owner = uuid.uuid4().hex

        # read the current lock
        lock = self._read(s3_client=s3_client)
        utc_now = get_utc_now()
        if lock.is_locked(utc_now=utc_now, expect_owner=owner):
            raise AlreadyLockedError(f"Lock is already acquired by {lock}")

        lock.expire = self.expire
        lock.lock_time = utc_now.isoformat()
        lock.release_time = None
        lock.owner = owner
        self._write(s3_client, lock)

        if self.wait > 0:
            time.sleep(self.wait)

        lock = self._read(s3_client=s3_client)
        if lock.owner != owner:  # pragma: no cover
            raise AlreadyLockedError(f"Lock is already acquired by {lock}")

        return lock

    def release(self, s3_client: "S3Client", lock: Lock) -> Lock:
        """
        Release the lock. Set the owner as None and update release time.

        :param s3_client:
        :param lock: the lock to release.
        """
        lock.release_time = get_utc_now().isoformat()
        lock.owner = None
        self._write(s3_client, lock)
        return lock
