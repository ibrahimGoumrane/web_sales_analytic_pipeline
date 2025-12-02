"""Reports package public API.

This module intentionally avoids importing the heavy report generator at
module import time (matplotlib/seaborn) so that environments that do not
have plotting libraries installed (for example Airflow scheduler workers)
can still import the package and load DAGs. The real implementation is
imported lazily when `generate_analytics_report` is called.
"""

from .helpers import PlotHelper

def generate_analytics_report(*args, **kwargs):
	"""Lazy wrapper that imports and calls the real report generator.

	Importing the real implementation is deferred to runtime so top-level
	imports don't require optional plotting dependencies.
	"""
	from .base import generate_analytics_report as _gen
	return _gen(*args, **kwargs)

__all__ = ["generate_analytics_report", "PlotHelper"]
