# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses


@dataclasses.dataclass
class ExecutionContext:
    """
    Custom state machine execution context.
    """

    exec_id: str = dataclasses.field()
    job_start_timestamp: T.Optional[int] = dataclasses.field(default=None)

    @classmethod
    def read(
        cls,
        s3_client,
        bucket: str,
        prefix: str,
        exec_id: str,
    ) -> "ExecutionContext":
        if prefix.endswith("/"):
            prefix = prefix[:-1]
        key = f"{prefix}/{exec_id}/context.json"
        return cls(
            **json.loads(
                s3_client.get_object(
                    Bucket=bucket,
                    Key=key,
                )["Body"]
                .read()
                .decode("utf-8")
            )
        )

    def write(
        self,
        s3_client,
        bucket: str,
        prefix: str,
    ) -> str:
        if prefix.endswith("/"):
            prefix = prefix[:-1]
        key = f"{prefix}/{self.exec_id}/context.json"
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(dataclasses.asdict(self)),
            ContentType="application/json",
        )
        return f"s3://{bucket}/{key}"


class JobStatus:
    running = "running"
    failed = "failed"
    succeeded = "succeeded"

    @classmethod
    def read(
        cls,
        s3_client,
        bucket: str,
        prefix: str,
        exec_id: str,
    ):
        if prefix.endswith("/"):
            prefix = prefix[:-1]
        response = s3_client.get_object(
            Bucket=bucket,
            Key=f"{prefix}/{exec_id}/status.txt",
        )
        return response["Body"].read().decode("utf-8").strip()

    @classmethod
    def write(
        cls,
        s3_client,
        bucket: str,
        prefix: str,
        exec_id: str,
        status: str,
    ):
        s3_client.put_object(
            Bucket=bucket,
            Key=f"{prefix}/{exec_id}/status.txt",
            Body=status,
            ContentType="text/plain",
        )
