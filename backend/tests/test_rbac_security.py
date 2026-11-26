"""Automated RBAC, Supabase persistence, rate-limit, and privilege isolation tests."""

import os
import sys
import unittest
import uuid

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient  # noqa: E402
from auth.security import verify_password  # noqa: E402
from config import settings  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
from db_models import ActiveBooking, AuditLog, LoginAttempt, ServerLog, User  # noqa: E402
from main import app  # noqa: E402
from scripts.seed_developer import seed_developer  # noqa: E402


class RBACSecurityTestSuite(unittest.TestCase):
    """End-to-end verification of RBAC enforcement against Supabase PostgreSQL."""

    @classmethod
    def setUpClass(cls):
        cls.run_tag = uuid.uuid4().hex[:10]
        cls.user_a_email = f"rbac_user_a_{cls.run_tag}@parkkaro-test.example"
        cls.user_b_email = f"rbac_user_b_{cls.run_tag}@parkkaro-test.example"
        cls.dev_email = f"rbac_dev_{cls.run_tag}@parkkaro-test.example"
        cls.user_password = "UserPass1234"
        cls.dev_password = "DevStrongPass9876"

        cls.created_user_ids = []
        cls.created_booking_ids = []

        # Run lifespan once so Supabase tables & columns exist
        cls.client = TestClient(app, base_url="https://testserver")
        cls.client.__enter__()

        # Confirm PostgreSQL/Supabase is backing the database engine (no local SQLite file)
        cls.assertTrue_dialect()

    @classmethod
    def assertTrue_dialect(cls):
        db = SessionLocal()
        try:
            dialect = db.bind.dialect.name if db.bind else "unknown"
            assert dialect == "postgresql", f"Expected Supabase postgresql backend, got {dialect}"
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls):
        # Release any active test bookings and clean up all test records in Supabase
        db = SessionLocal()
        try:
            if cls.created_booking_ids:
                db.query(ActiveBooking).filter(
                    ActiveBooking.id.in_(cls.created_booking_ids)
                ).delete(synchronize_session=False)

            test_emails = [cls.user_a_email, cls.user_b_email, cls.dev_email]
            user_rows = db.query(User).filter(User.email.in_(test_emails)).all()
            all_ids = list({*(cls.created_user_ids), *(u.id for u in user_rows)})

            if all_ids:
                db.query(AuditLog).filter(AuditLog.actor_user_id.in_(all_ids)).delete(synchronize_session=False)
                db.query(ServerLog).filter(ServerLog.user_id.in_(all_ids)).delete(synchronize_session=False)
                db.query(ActiveBooking).filter(ActiveBooking.user_id.in_(all_ids)).delete(synchronize_session=False)

            db.query(LoginAttempt).filter(LoginAttempt.email.in_(test_emails)).delete(synchronize_session=False)
            if all_ids:
                db.query(User).filter(User.id.in_(all_ids)).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()

        cls.client.__exit__(None, None, None)

    def _new_client(self) -> TestClient:
        return TestClient(app, base_url="https://testserver")

    def test_01_signup_forces_user_role_ignores_client_role_and_hashes_password(self):
        c = self._new_client()
        res = c.post(
            "/api/auth/signup",
            json={
                "email": self.user_a_email,
                "password": self.user_password,
                "full_name": "Test User A",
                "role": "developer",  # Attempt privilege escalation
            },
        )
        self.assertEqual(res.status_code, 201, res.text)
        body = res.json()
        self.assertEqual(body["role"], "user")
        self.created_user_ids.append(body["id"])

        # Verify HttpOnly, Secure, SameSite cookie attributes
        set_cookie = res.headers.get("set-cookie", "").lower()
        self.assertIn(f"{settings.cookie_name}=", set_cookie)
        self.assertIn("httponly", set_cookie)
        self.assertIn("samesite=lax", set_cookie)
        if settings.cookie_secure:
            self.assertIn("secure", set_cookie)

        # Sign up second user normally
        res_b = c.post(
            "/api/auth/signup",
            json={
                "email": self.user_b_email,
                "password": self.user_password,
                "full_name": "Test User B",
            },
        )
        self.assertEqual(res_b.status_code, 201, res_b.text)
        self.created_user_ids.append(res_b.json()["id"])

        # Verify bcrypt hash in Supabase (not plaintext)
        db = SessionLocal()
        try:
            u = db.query(User).filter(User.email == self.user_a_email).first()
            self.assertIsNotNone(u)
            self.assertEqual(u.role, "user")
            self.assertNotEqual(u.password_hash, self.user_password)
            self.assertTrue(u.password_hash.startswith("$2"))
            self.assertTrue(verify_password(self.user_password, u.password_hash))
        finally:
            db.close()

    def test_02_seed_developer_creates_single_developer_account(self):
        dev_user = seed_developer(
            email=self.dev_email,
            password=self.dev_password,
            full_name="Test Developer",
        )
        self.created_user_ids.append(dev_user.id)
        self.assertEqual(dev_user.role, "developer")
        self.assertTrue(dev_user.is_active)

    def test_03_normal_user_blocked_from_all_dev_routes_and_unauth_blocked(self):
        dev_endpoints = [
            ("GET", "/api/dev/db-status"),
            ("GET", "/api/dev/health"),
            ("GET", "/api/dev/logs"),
            ("GET", "/api/dev/users"),
            ("PATCH", f"/api/dev/users/{self.created_user_ids[0]}/status"),
        ]

        # 1. Unauthenticated requests -> 401
        anon = self._new_client()
        self.assertEqual(anon.get("/api/user/dashboard").status_code, 401)
        for method, url in dev_endpoints:
            kwargs = {"json": {"is_active": False}} if method == "PATCH" else {}
            r = anon.request(method, url, **kwargs)
            self.assertEqual(r.status_code, 401, f"Expected 401 for anon {method} {url}, got {r.status_code}")

        # 2. Normal user login -> allowed /api/user/dashboard, 403 Forbidden on ALL /api/dev/*
        user_client = self._new_client()
        login_res = user_client.post(
            "/api/auth/login",
            json={"email": self.user_a_email, "password": self.user_password},
        )
        self.assertEqual(login_res.status_code, 200, login_res.text)
        self.assertEqual(login_res.json()["role"], "user")

        dash_res = user_client.get("/api/user/dashboard")
        self.assertEqual(dash_res.status_code, 200, dash_res.text)

        for method, url in dev_endpoints:
            kwargs = {"json": {"is_active": False}} if method == "PATCH" else {}
            r = user_client.request(method, url, **kwargs)
            self.assertEqual(r.status_code, 403, f"Expected 403 for normal user on {method} {url}, got {r.status_code}: {r.text}")

        # 3. Tampered cookie -> 401 Unauthorized
        user_client.cookies.set(settings.cookie_name, "tampered.jwt.token")
        self.assertEqual(user_client.get("/api/dev/db-status").status_code, 401)

    def test_04_user_dashboard_returns_only_own_bookings(self):
        client_a = self._new_client()
        client_b = self._new_client()
        self.assertEqual(
            client_a.post("/api/auth/login", json={"email": self.user_a_email, "password": self.user_password}).status_code,
            200,
        )
        self.assertEqual(
            client_b.post("/api/auth/login", json={"email": self.user_b_email, "password": self.user_password}).status_code,
            200,
        )

        # Find a spot with available car slots
        spots = client_a.get("/api/spots").json()
        bookable = next((s for s in spots if s["rule_type"] != "NO_PARKING" and s["available_car_slots"] >= 2), None)
        self.assertIsNotNone(bookable, "No available test parking spot with 2+ slots")

        b_a = client_a.post(
            "/api/book",
            json={"spot_id": bookable["id"], "user_name": f"UA-{self.run_tag}", "vehicle_type": "car", "duration_hours": 1},
        )
        self.assertEqual(b_a.status_code, 201, b_a.text)
        booking_a_id = b_a.json()["id"]
        self.created_booking_ids.append(booking_a_id)

        b_b = client_b.post(
            "/api/book",
            json={"spot_id": bookable["id"], "user_name": f"UB-{self.run_tag}", "vehicle_type": "car", "duration_hours": 1},
        )
        self.assertEqual(b_b.status_code, 201, b_b.text)
        booking_b_id = b_b.json()["id"]
        self.created_booking_ids.append(booking_b_id)

        dash_a = client_a.get("/api/user/dashboard").json()
        ids_a = {b["id"] for b in dash_a["bookings"]}
        self.assertIn(booking_a_id, ids_a)
        self.assertNotIn(booking_b_id, ids_a)

        # User A cannot end User B's booking via /api/user/bookings/{id}/end
        cross_end = client_a.post(f"/api/user/bookings/{booking_b_id}/end")
        self.assertEqual(cross_end.status_code, 403)

        # Release both bookings cleanly
        self.assertEqual(client_a.post(f"/api/user/bookings/{booking_a_id}/end").status_code, 200)
        self.assertEqual(client_b.post(f"/api/user/bookings/{booking_b_id}/end").status_code, 200)

    def test_05_developer_access_audit_logs_and_account_disable_lockout(self):
        dev_client = self._new_client()
        user_b_client = self._new_client()
        # Log in User B first to hold an active valid cookie
        self.assertEqual(
            user_b_client.post("/api/auth/login", json={"email": self.user_b_email, "password": self.user_password}).status_code,
            200,
        )
        self.assertEqual(user_b_client.get("/api/user/dashboard").status_code, 200)

        # Log in Developer
        dev_login = dev_client.post(
            "/api/auth/login",
            json={"email": self.dev_email, "password": self.dev_password},
        )
        self.assertEqual(dev_login.status_code, 200, dev_login.text)
        self.assertEqual(dev_login.json()["role"], "developer")

        db_res = dev_client.get("/api/dev/db-status")
        self.assertEqual(db_res.status_code, 200, db_res.text)
        self.assertEqual(db_res.json()["dialect"], "postgresql")

        health_res = dev_client.get("/api/dev/health")
        self.assertEqual(health_res.status_code, 200, health_res.text)
        self.assertIn("cpu_percent", health_res.json())

        users_res = dev_client.get("/api/dev/users")
        self.assertEqual(users_res.status_code, 200, users_res.text)
        user_list = users_res.json()["users"]
        self.assertTrue(all("password_hash" not in u for u in user_list))
        user_b_row = next((u for u in user_list if u["email"] == self.user_b_email), None)
        self.assertIsNotNone(user_b_row)

        # Disable User B -> creates AuditLog & immediately locks out User B's cookie
        disable_res = dev_client.patch(
            f"/api/dev/users/{user_b_row['id']}/status",
            json={"is_active": False},
        )
        self.assertEqual(disable_res.status_code, 200, disable_res.text)
        self.assertFalse(disable_res.json()["is_active"])
        self.assertEqual(user_b_client.get("/api/user/dashboard").status_code, 401)

        logs_res = dev_client.get("/api/dev/logs")
        self.assertEqual(logs_res.status_code, 200, logs_res.text)
        audit_actions = [a["action"] for a in logs_res.json()["audit_logs"]]
        self.assertIn("UPDATE_USER_STATUS", audit_actions)
        self.assertIn("VIEW_DB_STATUS", audit_actions)

    def test_06_generic_errors_and_login_rate_limiting(self):
        c = self._new_client()
        # Unknown email vs wrong password vs disabled account all say "Invalid credentials"
        r1 = c.post("/api/auth/login", json={"email": "nobody@parkkaro-test.example", "password": "BadPassword1"})
        self.assertEqual(r1.status_code, 401)
        self.assertEqual(r1.json()["detail"], "Invalid credentials")

        r2 = c.post("/api/auth/login", json={"email": self.user_b_email, "password": self.user_password})
        self.assertEqual(r2.status_code, 401)
        self.assertEqual(r2.json()["detail"], "Invalid credentials")

        # Trigger rate limit with repeated wrong password attempts on User A
        for _ in range(settings.login_rate_limit_max):
            resp = c.post("/api/auth/login", json={"email": self.user_a_email, "password": "WrongPassword99"})
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(resp.json()["detail"], "Invalid credentials")

        throttled = c.post("/api/auth/login", json={"email": self.user_a_email, "password": self.user_password})
        self.assertEqual(throttled.status_code, 429, throttled.text)

    def test_07_existing_features_and_ui_routes_still_work(self):
        c = self._new_client()
        self.assertEqual(c.get("/api/health").status_code, 200)
        self.assertEqual(c.get("/api/spots?city=Indore").status_code, 200)
        self.assertEqual(c.get("/api/predict-rush?spot_id=1&hour=18&day_of_week=4").status_code, 200)
        self.assertEqual(c.get("/login").status_code, 200)
        self.assertEqual(c.get("/dashboard").status_code, 200)
        self.assertEqual(c.get("/dev-dashboard").status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
