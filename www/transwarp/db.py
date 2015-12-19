# -*- coding: utf-8 -*-

import threading, functools, time

def next_id(t = None):
	if t is None:
		t = time.time()

	return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)

class Dict(dict):
	def __init__(self, key = (), value = (), **kw):
		super(Dict, self).__init__(**kw)
		for k, v in zip(key, value):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

class DBError(Exception):
	pass

class MultiColumnError(DBError):
	pass

engine = None

class _Engine(object):
	def __init__(self, connect):
		self._connect = connect

	def connect(self):
		return self._connect()

def create_engine(user, password, database, host = '127.0.0.1', port = 3306, **kw):
	import mysql.connector
	global engine
	param = dict(user = user, password = password, database = database, host = host, port = port)
	defaults = dict(use_unicode = True, charset = 'utf8', collation = 'utf8_general_ci', autocommit = False)
	for k, v in defaults.iteritems():
		param[k] = kw.pop(k, v)

	engine = _Engine(lambda: mysql.connector.connect(**param))

class _LazyConnection(object):
	def __init__(self):
		self.connection = None

	def cursor(self):
		if self.connection is None:
			self.connection = engine.connect()
		return self.connection.cursor()

	def cleanup(self):
		self.connection.close()
		self.connection = None

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()

class _Dbctx(threading.local):
	def __init__(self):
		self.connection = None
		self.transaction = 0

	def is_init(self):
		return self.connection is not None

	def init(self):
		self.connection = _LazyConnection()
		self.transaction = 0

	def cleanup(self):
		self.connection.cleanup()
		self.connection = None

	def cursor(self):
		return self.connection.cursor()

_db_ctx = _Dbctx()

class _ConnectionCtx(object):
	def __enter__(self):
		global _db_ctx
		self.should_cleanup = False
		if not _db_ctx.is_init:
			_db_ctx.init()
			self.should_cleanup = True
		return self

	def __exit__(self, exctype, excvalue, traceback):
		global _db_ctx
		if self.should_cleanup:
			_db_ctx.cleanup()

def with_connection(func):
	@functools.wraps(func)
	def _wrapper(*args, **kw):
		with _ConnectionCtx():
			return func(*args, **kw)
	return _wrapper

@with_connection
def _select(sql, first, *args):
	global _db_ctx
	sql = sql.replace('?', '%s')
	cursor = None
	try:
		cursor = _db_ctx.cursor()
		cursor.execute(sql, args)
		if cursor.description:
			names = [x[0] for x in cursor.description]
		if first:
			values = cursor.fetchone()
			if not values:
				return None
			return Dict(names, values)
		values = cursor.fetchall()
		if not values:
			return None
		return [Dict(names, x) for x in values]
	finally:
		if cursor:
			cursor.close()
		
def select_one(sql, *args):
	return _select(sql, True, *args)

def select_int(sql, *args):
	d = _select(sql, False, *args)
	if len(d) == 1:
		return d.values()[0]
	else:
		raise MultiColumnError('Expect only one row')

def select(sql, *args):
	return _select(sql, False, *args)

@with_connection
def _update(sql, *args):
	global _db_ctx
	cursor = None
	sql = sql.replace('?', '%s')
	try:
		cursor = _db_ctx.connection.cursor()
		cursor.execute(sql, args)
		_db_ctx.connection.commit()
		return cursor.rowcount()
	finally:
		if cursor:
			cursor.close()

def insert(table, **kw):
	cols, args = zip(*kw.iteritems())
	sql = 'insert into `%s` (%s) values (%s)' % (table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for i in range(len(cols))]))
	return _update(sql, *args)

def update(sql, *args):
	return _update(sql, *args)

	