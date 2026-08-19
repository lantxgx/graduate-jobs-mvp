from crawler.normalize import normalize_job, find_job_dicts

SOURCE = {
    "id": "demo",
    "company": "示例公司",
    "url": "https://example.com/campus/jobs",
    "campus_only": True,
}

def test_find_and_normalize():
    payload = {
        "data": {
            "list": [
                {
                    "jobId": "123",
                    "jobName": "算法工程师（校招）",
                    "workPlace": "上海",
                    "jobType": "校园招聘",
                    "education": "硕士及以上",
                    "requirements": "熟悉 Python / 深度学习",
                    "detailUrl": "/job/123",
                }
            ]
        }
    }
    found = find_job_dicts(payload)
    assert len(found) == 1
    job = normalize_job(found[0], SOURCE)
    assert job["title"] == "算法工程师（校招）"
    assert job["city"] == "上海"
    assert job["category"] == "算法/AI"
    assert job["apply_url"] == "https://example.com/job/123"


def test_normalize_xiaomi_specific_job():
    source = {
        "id": "xiaomi-campus",
        "company": "小米集团",
        "url": "https://xiaomi.jobs.f.mioffice.cn/internship/",
        "mode": "xiaomi_jobs_browser",
        "campus_only": True,
    }
    raw = {
        "id": "7621150010131400998",
        "title": "项目申报&政策支持岗（实习生）",
        "description": "负责项目申报、政策监测与材料整理。",
        "requirement": "硕士学历，26届应届生，有转正机会。",
        "recruit_type": {
            "name": "实习",
            "parent": {"name": "校招"},
        },
        "city_list": [{"name": "北京"}],
        "job_function": {"name": "职能类"},
        "publish_time": 1774437635867,
    }
    job = normalize_job(raw, source)
    assert job["title"] == "项目申报&政策支持岗（实习生）"
    assert job["city"] == "北京"
    assert job["job_nature"] == "校招 / 实习"
    assert job["category"] == "职能类"
    assert job["graduate_year"] == "2026"
    assert job["requirements"].startswith("硕士学历")
    assert job["apply_url"].endswith(
        "/position/7621150010131400998/detail"
    )
