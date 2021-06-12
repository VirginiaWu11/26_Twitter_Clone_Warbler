"""User model tests."""

# run these tests like:
#
#   FLASK_ENV=production python -m unittest test_user_model.py
# (we set FLASK_ENV for this command, so it doesn’t use debug mode, and therefore won’t use the Debug Toolbar during our tests).


import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data



class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        u1.following.append(u2)
        db.session.add_all([u1,u2])
        db.session.commit()

        u4=User.signup("testuser3","test3@test.com","HASHED_PASSWORD3",None)
        db.session.commit()
        
        self.u1 = User.query.get(1)
        self.u1_id=self.u1.id
        self.u2= User.query.get(2)
        self.client = app.test_client()
        # import pdb; pdb.set_trace()

    def tearDown(self):
        # res = super().tearDown() # not needed
        db.session.rollback()
        # return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        # test repr method
        self.assertEqual(str(u), "<User #4: testuser, test@test.com>")


######## Following tests 

    def test_is_following(self):
        """Test user function is_following"""
        self.assertEqual(self.u1.is_following(self.u2),True)
        self.assertEqual(self.u2.is_following(self.u1),False)
        
    
    def test_is_followed_by(self):
        """Test user function is_followed_by"""
        self.assertEqual(self.u2.is_followed_by(self.u1),True)
        self.assertEqual(self.u1.is_followed_by(self.u2),False)

######## SignUp tests 


    def test_valid_user_signup(self):
        """Test user method signup"""
        u4=User.signup("testuser4","test4@test.com","HASHED_PASSWORD4",None)
        db.session.commit()
        u4 = User.query.get(u4.id)
        self.assertIsNotNone(u4)
        self.assertEqual(u4.id,4)
        self.assertEqual(u4.username,"testuser4")
        
        self.assertNotEqual(u4.password,"HASHED_PASSWORD4")
    
    def test_invalid_username_signup(self):
        u_inv=User.signup("testuser1","test4@test.com","HASHED_PASSWORD4",None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
    def test_invalid_email_signup(self):
        u_inv=User.signup("testuser5","test1@test.com","HASHED_PASSWORD4",None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testuser5", "test5@test.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testuser5", "test5@test.com", None, None)

######## Authentication tests 

    def test_valid_authentication(self):
        u = User.authenticate('testuser3', "HASHED_PASSWORD3")
        self.assertIsNotNone(u)
        
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("testuser5", "HASHED_PASSWORD"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate("testuser3", "incorrect"))
