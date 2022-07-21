from flemi.models import db, Group
from .base import Base


class GroupTestCase(Base):
    def setUp(self) -> None:
        super().setUp()
        self.set_headers()

    def test_all_groups(self):
        g = Group(name="test")
        g2 = Group(name="test2", members=[self.test_user], private=True)
        db.session.add(g)
        db.session.add(g2)
        db.session.commit()

        resp = self.client.get(
            "/group/all",
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data[0]["name"], "test")
        self.assertTrue(len(data) == 1)

        resp = self.client.get(
            "/group/all",
            headers=self.headers
        )
        data = resp.get_json()
        print(len(data))
        self.assertTrue(len(data) == 2)
