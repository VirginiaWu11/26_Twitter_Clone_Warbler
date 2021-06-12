"""Message model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        u1 = User.signup("testuser1","test1@test.com","HASHED_PASSWORD1",None)
        u2 = User.signup("testuser2","test2@test.com","HASHED_PASSWORD2",None)
        db.session.commit()

        self.u1 = User.query.get(u1.id)
        self.u2 = User.query.get(u2.id)

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""
        
        m = Message(
            text="testingtext123",
            user_id=self.u1.id
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1.messages[0].text, "testingtext123")

    def test_message_likes(self):
        m1 = Message(
            text="testingtext123",
            user_id=self.u1.id
        )

        m2 = Message(
            text="moreText",
            user_id=self.u1.id
        )

        db.session.add_all([m1, m2])
        db.session.commit()

        self.u2.likes.append(m1)

        db.session.commit()

        likes = self.u2.likes
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].id, m1.id)


        