"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD",image_url=None
        )
        
        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",image_url=None
        )

        u1.following.append(u2)
        
        db.session.add_all([u1,u2])
        db.session.commit()

        u3=User.signup("testuser3","test3@test.com","HASHED_PASSWORD3",None)
        u4=User.signup("testuser4","test4@test.com","HASHED_PASSWORD4",None)
        u1.following.append(u3)

        db.session.commit()
        self.u1 = User.query.get(1)
        self.u1_id=self.u1.id
        self.u2= User.query.get(2)
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_following_any_user(self):
        """When you’re logged in, can you see the following pages for any user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id

            resp = c.get("/users/1/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser2",str(resp.data))
            self.assertIn("testuser3",str(resp.data))

    def test_follower_any_user(self):
        """When you’re logged in, can you see the follower pages for any user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id

            resp = c.get("/users/3/followers")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser1",str(resp.data))
            self.assertNotIn("testuser4",str(resp.data))
            #logged-in user
            self.assertIn("testuser2",str(resp.data))

    def test_users(self):
        """/users should show all users"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser1",str(resp.data))
            self.assertIn("testuser2",str(resp.data))
            self.assertIn("testuser3",str(resp.data))
            self.assertIn("testuser4",str(resp.data))


    def test_users_logged_out(self):
        """/users should show all users"""
        with self.client as c:

            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser1",str(resp.data))
            self.assertIn("testuser2",str(resp.data))
            self.assertIn("testuser3",str(resp.data))
            self.assertIn("testuser4",str(resp.data))

    def test_users_profile(self):
        """/users/<int:user_id> should show profile and comments of current user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            m = Message(
                text="Hello Test",
                user_id=self.u1.id
            )
            db.session.add(m)
            db.session.commit()

            resp = c.get(f"/users/{self.u1.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser1",str(resp.data))
            self.assertIn("Hello Test",str(resp.data))
          
    

