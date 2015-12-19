from models import User, Blog, Comment
import logging

from transwarp import db

logging.basicConfig(level = logging.DEBUG)

db.create_engine(user = 'root', password = 'password', database = 'myblog')

u = User(name='Test', email='test@example.com', password='1234567890', image='about:blank')

u.insert()

print 'new user id:', u.id
print 'create time:', u.created_at

u1 = User.find_first('where email=?', 'test@example.com')
print 'find user\'s name:', u1.name

u1.delete()

u2 = User.find_by('where email=?', 'test@example.com')

print 'find user:', u2