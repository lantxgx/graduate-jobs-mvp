import unittest

from crawler.adapters.papegames import normalize_papegames_job


class PapegamesAdapterTests(unittest.TestCase):
    SOURCE = {
        "id": "papegames-campus",
        "company": "叠纸",
        "url": "https://career.papegames.com/campus/position/list?limit=20",
    }

    def test_normalizes_concrete_list_item(self):
        job = normalize_papegames_job({
            "id": "123",
            "title": "客户端开发工程师（2027届秋招）",
            "description": "负责客户端开发",
            "requirement": "本科及以上，熟悉 C++",
            "job_category": {"name": "互联网 / 电子 / 网游"},
            "recruit_type": {"name": "正式", "parent": {"name": "校招"}},
            "city_list": [{"name": "上海"}],
            "job_post_info": {},
        }, self.SOURCE)
        self.assertIsNotNone(job)
        self.assertEqual(job["job_nature"], "全职")
        self.assertEqual(job["city"], "上海")
        self.assertEqual(job["degree"], "本科及以上")
        self.assertEqual(job["apply_url"], "https://career.papegames.com/campus/position/123/detail")

    def test_rejects_navigation_or_empty_item(self):
        self.assertIsNone(normalize_papegames_job({"id": "filter", "title": "校招"}, self.SOURCE))


if __name__ == "__main__":
    unittest.main()
