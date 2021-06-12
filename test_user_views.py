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
            password="HASHED_PASSWORD"
        )
        
        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        u1.following.append(u2)
        db.session.add_all([u1,u2])
        db.session.commit()

        u3=User.signup("testuser3","test3@test.com","HASHED_PASSWORD3",None)
        db.session.commit()
        
        self.u1 = User.query.get(1)
        self.u1_id=self.u1.id
        self.u2= User.query.get(2)
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()