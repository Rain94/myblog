# -*- coding: utf-8 -*-

import time, uuid

from transwarp import db
from transwarp.orm import Model, StringField, FloatField, BooleanField, TextField

class User(Model):
	__table__ = 'users'

	id = StringField(primary_key = True, default = db.next_id, ddl = 'varchar(50)')
	email = StringField(updatable = False, ddl = 'varchar(50)')
	password = StringField(ddl = 'varchar(50)')
	admin = BooleanField()
	name = StringField(ddl = 'varchar(50)')
	image = StringField(ddl = 'varchar(500)')
	created_at = FloatField(updatable = False, default = time.time)

class Blog(Model):
	__table__ = 'blogs'

	id = StringField(primary_key = True, default = db.next_id, ddl = 'varchar(50)')
	user_id = StringField(updatable = False, ddl = 'varchar(50)')
	user_name = StringField(ddl = 'varchar(50)')
	user_image = StringField(ddl = 'varchar(50)')
	name = StringField(ddl = 'varchar(50)')
	summary = StringField(ddl = 'varchar(200)')
	content = TextField()
	created_at = FloatField(updatable = False, default = time.time)

class Comment(Model):
	__table__ = 'comments'

	id = StringField(primary_key = True, default = db.next_id, ddl = 'varchar(50)')
	blog_id = StringField(updatable = False, ddl = 'varchar(50)')
	user_id = StringField(updatable = False, ddl = 'varchar(50)')
	user_name = StringField(ddl = 'varchar(50)')
	user_image = StringField(ddl = 'varchar(500)')
	content = TextField()
	created_at = FloatField(updatable = False, default = time.time)


if __name__ == '__main__':
	db.create_engine('root', 'password', 'myblog')
	db.update('drop table if exists users')
	db.update('drop table if exists blogs')
	db.update('drop table if exists comments')

	db.update(User().__sql__())
	db.update(Blog().__sql__())
	db.update(Comment().__sql__())



