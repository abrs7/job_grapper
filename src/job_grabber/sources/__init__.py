"""Registry of available job sources."""

from job_grabber.sources.arbeitnow import ArbeitnowSource
from job_grabber.sources.base import Source
from job_grabber.sources.himalayas import HimalayasSource
from job_grabber.sources.remoteok import RemoteOKSource
from job_grabber.sources.remotive import RemotiveSource
from job_grabber.sources.weworkremotely import WeWorkRemotelySource

SOURCES: dict[str, type[Source]] = {
    cls.name: cls
    for cls in (
        RemotiveSource,
        RemoteOKSource,
        WeWorkRemotelySource,
        HimalayasSource,
        ArbeitnowSource,
    )
}

__all__ = ["SOURCES", "Source"]
