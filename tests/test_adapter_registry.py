import unittest

from crawler.adapters import default_registry


class AdapterRegistryTests(unittest.TestCase):
    def test_legacy_modes_share_one_compatibility_adapter(self):
        registry = default_registry()
        self.assertEqual(
            registry.names(),
            ["beisen_jobs_browser", "browser_json", "custom_html", "feishu_jobs_browser", "greenhouse", "legacy", "lever", "mihoyo", "oppo", "papegames", "xiaomi_jobs_browser"],
        )
        self.assertIs(registry.get("browser_json"), registry.get("feishu_jobs_browser"))

    def test_unknown_adapter_is_rejected(self):
        with self.assertRaises(KeyError):
            default_registry().get("not-registered")


if __name__ == "__main__":
    unittest.main()
