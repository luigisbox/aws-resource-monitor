# AWS Resource Monitor

Small Python 3.5+ convenience library to easily monitor CPU and memory usage in AWS Batch jobs and report them to StatsD. Since it uses [ECS Task Metadata V3 endpoints](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v3.html) it is perfectly suitable to do so for other type of ECS tasks as well.

## Setup

You can install this package by using `pip`:

	pip install aws-resource-monitor

If you fancy `pipenv` use:

	pipenv install aws-resource-monitor

To install from source, run:

	python setup.py install


To install via requirements file, add the following:

	-e git+https://github.com/luigisbox/aws-resource-monitor.git#egg=aws-resource-monitor

## Usage

First off, you need to require the library:

	from aws_resource_monitor import resource_monitoring

The `resource_monitoring` is a context manager accepting two positional arguments:

- `statsd_client` is your own instance of StatsD client (see [PythonStatsD library](https://statsd.readthedocs.io/en/latest/) which will be used to report metrics.
- `metrics_prefix` is a string which will prefix individual metrics.

Optionally, you can pass in keyword argument `interval` with `timedelta` object customizing polling period for new metrics (default is every five seconds).

	with resource_monitoring(statsd_client, metrics_prefix):
		fn()

Behind the scenes, `resource_monitoring` context manager first checks for existence of `ECS_CONTAINER_METADATA_URI` environment variable. If it is not found, the monitor does nothing thus working well in development.

In production or when the variable exists, it creates a separate thread from your main application that reads task UUID and polls the "stats" endpoint in the metadata URI to complete and send as gauge the following metrics:

- cpu.system
- cpu.user
- cpu.percent
- memory.limit
- memory.usage
- memory.max_usage

A more complete example would be:

	import statsd
	from aws_resource_monitor import resource_monitoring

	statsd = statsd.StatsClient('localhost', 8125)

	with resource_monitoring(statsd, "example.metrics.", interval=timedelta(seconds=10)):
		fn()

For example, for the task UUID assigned by AWS "afc92259-3a0c-4e14-8e23-a49cc41e7947" this will report gauge "example.metrics.afc92259-3a0c-4e14-8e23-a49cc41e7947.memory.usage" and in ten seconds check and report again.

## Contributing

1.  Check for open issues or open a new issue for a feature request or a bug.
2.  Fork the repository and make your changes to the master branch (or branch off of it).
3.  Send a pull request.

## Development

Run the linter with:

	make lint

The client library uses Black for code formatting. Code must be formatted with Black before PRs are submitted. Run the formatter with:

	make fmt

## Changelog

### v1.0.0: 08/06/2020

Initial version.
