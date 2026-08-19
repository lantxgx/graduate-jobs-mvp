from crawler.adapters.base import AdapterRegistry, CollectionResult, JobSourceAdapter, ListingItem
from crawler.adapters.legacy import LegacyModeAdapter
from crawler.adapters.papegames import PapegamesAdapter
from crawler.adapters.oppo import OppoAdapter
from crawler.adapters.mihoyo import MihoyoAdapter
from crawler.adapters.greenhouse import GreenhouseAdapter
from crawler.adapters.lever import LeverAdapter
from crawler.adapters.custom_html import CustomHtmlAdapter


def default_registry() -> AdapterRegistry:
    """Return the registry used by the production runner.

    The legacy adapter remains the compatibility implementation for the
    already verified browser sources.  New ATS adapters can be registered
    here without adding another source-mode branch to the runner.
    """
    registry = AdapterRegistry()
    legacy = LegacyModeAdapter()
    registry.register("legacy", legacy)
    for mode in ("browser_json", "beisen_jobs_browser", "xiaomi_jobs_browser", "feishu_jobs_browser"):
        registry.register(mode, legacy)
    registry.register("papegames", PapegamesAdapter())
    registry.register("oppo", OppoAdapter())
    registry.register("mihoyo", MihoyoAdapter())
    registry.register("greenhouse", GreenhouseAdapter())
    registry.register("lever", LeverAdapter())
    registry.register("custom_html", CustomHtmlAdapter())
    return registry


__all__ = [
    "AdapterRegistry",
    "CollectionResult",
    "JobSourceAdapter",
    "ListingItem",
    "LegacyModeAdapter",
    "PapegamesAdapter",
    "OppoAdapter",
    "MihoyoAdapter",
    "GreenhouseAdapter",
    "LeverAdapter",
    "CustomHtmlAdapter",
    "default_registry",
]

__all__ = ["AdapterRegistry", "CollectionResult", "JobSourceAdapter", "ListingItem"]
