import base64
import io
import os
import zipfile
import unittest
from unittest.mock import patch

import httpx

from fastapi.testclient import TestClient

from app.main import app
from app.ai_profile import _validate_provider_profile
from app.resume_parser import extract_resume_text, extract_candidate_profile


class ResumeParserTests(unittest.TestCase):
    def test_docx_text_and_candidate_profile(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(
                "word/document.xml",
                "<document xmlns='x'><body><p><r><t>Master Python 2027 算法</t></r></p></body></document>",
            )
        text = extract_resume_text("resume.docx", buffer.getvalue())
        profile = extract_candidate_profile(text)
        self.assertIn("Python", profile["skills"])
        self.assertTrue(profile["needs_user_confirmation"])

    def test_preview_endpoint_does_not_save_profile(self):
        data = b"%PDF-1.4\nstream\nBT (Master Python 2027) Tj ET\nendstream"
        client = TestClient(app)
        response = client.post(
            "/api/resume/preview",
            json={"filename": "resume.pdf", "content_base64": base64.b64encode(data).decode()},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["saved"])
        client.close()

    def test_unsupported_format_is_rejected(self):
        client = TestClient(app)
        response = client.post(
            "/api/resume/preview",
            json={"filename": "resume.txt", "content_base64": base64.b64encode(b"x").decode()},
        )
        self.assertEqual(response.status_code, 400)
        client.close()

    def test_analyze_endpoint_defaults_to_local_rules(self):
        data = b"%PDF-1.4\nstream\nBT (Master Python 2027) Tj ET\nendstream"
        client = TestClient(app)
        with patch.dict(os.environ, {"AI_PROFILE_PROVIDER": "rules"}, clear=False):
            response = client.post(
                "/api/resume/analyze",
                json={"filename": "resume.pdf", "content_base64": base64.b64encode(data).decode()},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"]["provider"], "local_rules")
        client.close()

    def test_external_provider_requires_consent_and_configuration(self):
        data = b"%PDF-1.4\nstream\nBT (Master Python 2027) Tj ET\nendstream"
        client = TestClient(app)
        with patch.dict(os.environ, {
            "AI_PROFILE_PROVIDER": "openai_compatible",
            "AI_BASE_URL": "",
            "AI_API_KEY": "",
            "AI_MODEL": "",
        }, clear=False):
            denied = client.post(
                "/api/resume/analyze",
                json={"filename": "resume.pdf", "content_base64": base64.b64encode(data).decode()},
            )
            self.assertEqual(denied.status_code, 403)
            consented = client.post(
                "/api/resume/analyze",
                json={"filename": "resume.pdf", "content_base64": base64.b64encode(data).decode(), "external_ai_consent": True},
            )
            self.assertEqual(consented.status_code, 503)
        client.close()

    def test_external_profile_schema_rejects_intent_or_wrong_types(self):
        with self.assertRaises(ValueError):
            _validate_provider_profile({"target_roles": ["algorithm"]})
        with self.assertRaises(ValueError):
            _validate_provider_profile({"skills": "Python"})
        self.assertEqual(_validate_provider_profile({"skills": ["Python"]})["skills"], ["Python"])

    def test_external_provider_failure_is_a_clear_service_unavailable(self):
        data = b"%PDF-1.4\nstream\nBT (Master Python 2027) Tj ET\nendstream"
        client = TestClient(app)
        with patch.dict(os.environ, {
            "AI_PROFILE_PROVIDER": "openai_compatible",
            "AI_BASE_URL": "http://ai.invalid/v1",
            "AI_API_KEY": "test-key",
            "AI_MODEL": "test-model",
        }, clear=False), patch("app.ai_profile.httpx.Client") as http_client:
            http_client.return_value.__enter__.return_value.post.side_effect = httpx.ConnectError("offline")
            response = client.post(
                "/api/resume/analyze",
                json={
                    "filename": "resume.pdf",
                    "content_base64": base64.b64encode(data).decode(),
                    "external_ai_consent": True,
                },
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "ai_provider_request_failed")
        client.close()


if __name__ == "__main__":
    unittest.main()
