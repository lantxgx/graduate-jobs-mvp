import unittest

from crawler.adapters import default_registry


class AdapterRegistryTests(unittest.TestCase):
    def test_legacy_modes_share_one_compatibility_adapter(self):
        registry = default_registry()
        self.assertEqual(
            registry.names(),
            ["alibaba", "baiwang", "beisen", "beisen_jobs_browser", "browser_json", "byd", "bytedance_ats", "ccb", "citics", "custom_html", "dewu", "dongfang", "fanruan", "feishu_jobs_browser", "fuyao", "greenhouse", "hikvision", "hotjob", "huya", "jd", "legacy", "lenovo", "lever", "lovol", "meituan", "mihoyo", "moka", "oppo", "papegames", "pdd", "sangfor", "sanqi", "sensetime", "tencent", "xiaohongshu", "xiaomi_jobs_browser", "yitu"],
        )
        self.assertIs(registry.get("browser_json"), registry.get("feishu_jobs_browser"))

    def test_unknown_adapter_is_rejected(self):
        with self.assertRaises(KeyError):
            default_registry().get("not-registered")


if __name__ == "__main__":
    unittest.main()
