from crawler.adapters.base import AdapterRegistry, CollectionResult, JobSourceAdapter, ListingItem
from crawler.adapters.legacy import LegacyModeAdapter
from crawler.adapters.papegames import PapegamesAdapter
from crawler.adapters.oppo import OppoAdapter
from crawler.adapters.mihoyo import MihoyoAdapter
from crawler.adapters.greenhouse import GreenhouseAdapter
from crawler.adapters.lever import LeverAdapter
from crawler.adapters.custom_html import CustomHtmlAdapter
from crawler.adapters.beisen import BeisenAdapter
from crawler.adapters.jd import JdAdapter
from crawler.adapters.lenovo import LenovoAdapter
from crawler.adapters.meituan import MeituanAdapter
from crawler.adapters.pdd import PddAdapter
from crawler.adapters.moka import MokaAdapter
from crawler.adapters.hikvision import HikvisionAdapter
from crawler.adapters.alibaba import AlibabaCampusAdapter
from crawler.adapters.tencent import TencentCampusAdapter
from crawler.adapters.dewu import DewuCampusAdapter
from crawler.adapters.xiaohongshu import XiaohongshuCampusAdapter
from crawler.adapters.huya import HuyaCampusAdapter
from crawler.adapters.sanqi import SanqiCampusAdapter
from crawler.adapters.ccb import CcbCampusAdapter
from crawler.adapters.citics import CiticsCampusAdapter
from crawler.adapters.fuyao import FuyaoCampusAdapter
from crawler.adapters.lovol import LovolCampusAdapter
from crawler.adapters.baiwang import BaiwangCampusAdapter
from crawler.adapters.hotjob import HotjobCampusAdapter
from crawler.adapters.sensetime import SensetimeCampusAdapter, BytedanceAtsCampusAdapter
from crawler.adapters.yitu import YituCampusAdapter
from crawler.adapters.dongfang import DongfangCampusAdapter
from crawler.adapters.sangfor import SangforCampusAdapter
from crawler.adapters.fanruan import FanruanAdapter
from crawler.adapters.byd import BydCampusAdapter
from crawler.adapters.gbits import GbitsCampusAdapter
from crawler.adapters.kuaishou import KuaishouCampusAdapter
from crawler.adapters.wind import WindCampusAdapter
from crawler.adapters.leihuo import LeihuoCampusAdapter
from crawler.adapters.lixiang import LixiangCampusAdapter
from crawler.adapters.apple import AppleCampusAdapter
from crawler.adapters.cmb import CmbCampusAdapter
from crawler.adapters.anker import AnkerCampusAdapter
from crawler.adapters.gac_toyota import GacToyotaCampusAdapter
from crawler.adapters.bilibili import BilibiliCampusAdapter
from crawler.adapters.ctrip import CtripCampusAdapter


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
    registry.register("beisen", BeisenAdapter())
    registry.register("jd", JdAdapter())
    registry.register("lenovo", LenovoAdapter())
    registry.register("meituan", MeituanAdapter())
    registry.register("pdd", PddAdapter())
    registry.register("papegames", PapegamesAdapter())
    registry.register("oppo", OppoAdapter())
    registry.register("mihoyo", MihoyoAdapter())
    registry.register("greenhouse", GreenhouseAdapter())
    registry.register("lever", LeverAdapter())
    registry.register("custom_html", CustomHtmlAdapter())
    registry.register("moka", MokaAdapter())
    registry.register("hikvision", HikvisionAdapter())
    registry.register("alibaba", AlibabaCampusAdapter())
    registry.register("tencent", TencentCampusAdapter())
    registry.register("dewu", DewuCampusAdapter())
    registry.register("xiaohongshu", XiaohongshuCampusAdapter())
    registry.register("huya", HuyaCampusAdapter())
    registry.register("sanqi", SanqiCampusAdapter())
    registry.register("ccb", CcbCampusAdapter())
    registry.register("citics", CiticsCampusAdapter())
    registry.register("fuyao", FuyaoCampusAdapter())
    registry.register("lovol", LovolCampusAdapter())
    registry.register("baiwang", BaiwangCampusAdapter())
    registry.register("hotjob", HotjobCampusAdapter())
    registry.register("sensetime", SensetimeCampusAdapter())
    registry.register("bytedance_ats", BytedanceAtsCampusAdapter())
    registry.register("yitu", YituCampusAdapter())
    registry.register("dongfang", DongfangCampusAdapter())
    registry.register("sangfor", SangforCampusAdapter())
    registry.register("fanruan", FanruanAdapter())
    registry.register("byd", BydCampusAdapter())
    registry.register("gbits", GbitsCampusAdapter())
    registry.register("kuaishou", KuaishouCampusAdapter())
    registry.register("wind", WindCampusAdapter())
    registry.register("leihuo", LeihuoCampusAdapter())
    registry.register("lixiang", LixiangCampusAdapter())
    registry.register("apple", AppleCampusAdapter())
    registry.register("cmb", CmbCampusAdapter())
    registry.register("anker", AnkerCampusAdapter())
    registry.register("gac_toyota", GacToyotaCampusAdapter())
    registry.register("bilibili", BilibiliCampusAdapter())
    registry.register("ctrip", CtripCampusAdapter())
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
    "BeisenAdapter",
    "JdAdapter",
    "LenovoAdapter",
    "MeituanAdapter",
    "MokaAdapter",
    "HikvisionAdapter",
    "AlibabaCampusAdapter",
    "TencentCampusAdapter",
    "DewuCampusAdapter",
    "XiaohongshuCampusAdapter",
    "HuyaCampusAdapter",
    "SanqiCampusAdapter",
    "CcbCampusAdapter",
    "CiticsCampusAdapter",
    "FuyaoCampusAdapter",
    "LovolCampusAdapter",
    "BaiwangCampusAdapter",
    "HotjobCampusAdapter",
    "SensetimeCampusAdapter",
    "BytedanceAtsCampusAdapter",
    "YituCampusAdapter",
    "DongfangCampusAdapter",
    "SangforCampusAdapter",
    "FanruanAdapter",
    "BydCampusAdapter",
    "GbitsCampusAdapter",
    "KuaishouCampusAdapter",
    "WindCampusAdapter",
    "LeihuoCampusAdapter",
    "LixiangCampusAdapter",
    "AppleCampusAdapter",
    "CmbCampusAdapter",
    "AnkerCampusAdapter",
    "GacToyotaCampusAdapter",
    "BilibiliCampusAdapter",
    "CtripCampusAdapter",
    "default_registry",
]

__all__ = ["AdapterRegistry", "CollectionResult", "JobSourceAdapter", "ListingItem"]
