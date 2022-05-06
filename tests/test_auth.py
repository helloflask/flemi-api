from .base import Base


class AuthTestCase(Base):
    def test_get_token(self):
        resp = self.client.post("/auth/login", json={
            "username": "test",
            "password": "password",
        })
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assert_(data.get("auth_token").startswith("Bearer "))

    def test_register(self):
        user_data = {
            "username": "test2",
            "name": "test",
            "password": "password",
            "email": "test2@example.com",
        }
        resp = self.client.post("/auth/register", json=user_data)
        self.assertEqual(resp.status_code, 200)

        user_data["username"] = "test"
        resp = self.client.post("/auth/register", json=user_data)
        self.assertEqual(resp.status_code, 400)

        user_data["username"] = "test3"
        user_data["email"] = "test@example.com"
        resp = self.client.post("/auth/register", json=user_data)
        self.assertEqual(resp.status_code, 400)
