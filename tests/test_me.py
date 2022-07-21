from flog.models import User
from .base import Base


class MeTestCase(Base):
    def setUp(self) -> None:
        super().setUp()
        self.set_headers()

    def test_get_profile(self):
        resp = self.client.get(
            "/me",
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["username"], "test")

    def test_edit_basic(self):
        resp = self.client.put(
            "/me/edit/basic",
            json={"name": "new name"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.query.filter_by(username="test").first().name, "new name")

    def test_edit_avatar(self):
        resp = self.client.put(
            "/me/edit/avatar",
            json={"avatar_url": "https://example.com"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            User.query.filter_by(username="test").first().custom_avatar_url,
            "https://example.com",
        )

    def test_edit_about_me(self):
        resp = self.client.put(
            "/me/edit/about",
            json={"about_me": "nothing special"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            User.query.filter_by(username="test").first().about_me,
            "nothing special",
        )
