from .base import Base
from flog import fakes
from flog.models import Post, Column


class PostTestCase(Base):
    def setUp(self):
        super().setUp()
        fakes.posts(count=10, private=False)
        fakes.posts(count=2, private=True)
        fakes.columns(3)
        self.set_headers()

    def test_get_post(self):
        resp = self.client.get("/post/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json["title"],
            Post.query.get(1).title
        )

    def test_get_posts(self):
        resp = self.client.get("/posts?limit=3&offset=0")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json["posts"]), 3)
        self.assertEqual(resp.json["prev"], "")

        resp = self.client.get("/posts?limit=4&offset=8")
        self.assertEqual(len(resp.json["posts"]), 2)
        self.assertEqual(resp.json["next"], "")
        self.assertEqual(
            resp.json["posts"][0]["title"],
            Post.query.get(9).title
        )

    def test_create_post(self):
        resp = self.client.post(
            "/post",
            headers=self.headers,
            json={
                "title": "lorem",
                "content": "ipsum"
            }
        )
        self.assertEqual(resp.status_code, 201)
        resp = self.client.post(
            "/post",
            headers=self.headers,
            json={
                "title": "post2",
                "content": "post2",
                "column_ids": [1, 2]
            }
        )
        p = Post.query.filter_by(title="post2").first()
        self.assertEqual(resp.status_code, 201)
        self.assertIn(Column.query.get(1), p.columns)
        self.assertIn(Column.query.get(2), p.columns)


    def test_update_post(self):
        resp = self.client.post(
            "/post",
            headers=self.headers,
            json={
                "title": "lorem",
                "content": "ipsum"
            }
        )
        p = Post.query.filter_by(title="lorem").first()
        resp = self.client.put(
            f"/post/{p.id}",
            headers=self.headers,
            json={
                "title": "new"
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(p.title, "new")
        resp = self.client.put(
            f"/post/{p.id}",
            headers=self.headers,
            json={
                "column_ids": [3]
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(Column.query.get(1), p.columns)
        self.assertIn(Column.query.get(3), p.columns)

    def test_delete_post(self):
        self.client.post(
            "/post",
            headers=self.headers,
            json={
                "title": "lorem",
                "content": "ipsum"
            }
        )
        p = Post.query.filter_by(title="lorem").first()
        resp = self.client.delete(
            f"/post/{p.id}",
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 204)
