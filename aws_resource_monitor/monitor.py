import json
import os
import urllib.request
import uuid
from contextlib import contextmanager
from datetime import timedelta
from threading import Event
from threading import Thread


class AWSResourceMonitor(Thread):
    def __init__(
        self,
        interval,
        statsd_client,
        metrics_prefix,
        metadata_uri,
        stats_metadata_uri,
    ):
        Thread.__init__(self)

        self.daemon = False
        self.stopped = Event()

        self.interval = interval
        self.statsd_client = statsd_client
        self.metrics_prefix = metrics_prefix
        self.metadata_uri = metadata_uri
        self.task_uuid = self.get_task_uuid()
        self.stats_metadata_uri = stats_metadata_uri

    def get_task_uuid(self):
        if self.metadata_uri:
            metadata = self.read_metadata(self.metadata_uri)

            if (
                "Labels" in metadata
                and "com.amazonaws.ecs.task-arn" in metadata["Labels"]
            ):
                return metadata["Labels"]["com.amazonaws.ecs.task-arn"].split(
                    "/"
                )[-1]

        return str(uuid.uuid4())

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute()

    def stop(self):
        self.stopped.set()
        self.join()

    def execute(self):
        metadata = self.read_metadata(self.stats_metadata_uri)

        if (
            not metadata
            or "cpu_stats" not in metadata
            or "precpu_stats" not in metadata
        ):
            return

        cpu_stats = metadata.get("cpu_stats", {})
        prev_cpu_stats = metadata.get("precpu_stats", {})

        value_system = cpu_stats.get("system_cpu_usage")
        if value_system is not None:
            self.gauge("cpu.system", value_system)

        value_total = cpu_stats.get("cpu_usage", {}).get("total_usage")
        if value_total is not None:
            self.gauge("cpu.user", value_total)

        prevalue_total = prev_cpu_stats.get("cpu_usage", {}).get("total_usage")
        prevalue_system = prev_cpu_stats.get("system_cpu_usage")

        if prevalue_system is not None and prevalue_total is not None:
            cpu_delta = float(value_total) - float(prevalue_total)
            system_delta = float(value_system) - float(prevalue_system)
        else:
            cpu_delta = 0.0
            system_delta = 0.0

        online_cpus = float(cpu_stats.get("online_cpus", 0.0))

        if system_delta > 0 and cpu_delta > 0 and online_cpus > 0:
            self.gauge(
                "cpu.percent", (cpu_delta / system_delta) * online_cpus * 100.0
            )

        memory_stats = metadata.get("memory_stats", {})

        for metric in ["limit", "usage", "max_usage"]:
            value = memory_stats.get(metric)
            if value is not None:
                self.gauge(f"memory.{metric}", value)

    def read_metadata(self, uri):
        metadata = {}

        request = urllib.request.urlopen(uri)

        if request.getcode() == 200:
            try:
                metadata = json.loads(request.read())
            except (TypeError, json.JSONDecodeError):
                pass

        return metadata

    def gauge(self, key, value):
        self.statsd_client.gauge(
            ".".join([self.metrics_prefix, self.task_uuid, key]), value
        )


@contextmanager
def resource_monitoring(statsd_client, metrics_prefix, interval=None):
    if not interval:
        interval = timedelta(seconds=5)

    metadata_uri = os.environ.get("ECS_CONTAINER_METADATA_URI")

    if metadata_uri:
        monitor = AWSResourceMonitor(
            interval=interval,
            statsd_client=statsd_client,
            metrics_prefix=metrics_prefix,
            metadata_uri=metadata_uri,
            stats_metadata_uri=metadata_uri + "/stats",
        )
        monitor.start()
    else:
        monitor = None

    try:
        yield monitor
    finally:
        if monitor:
            monitor.stop()
