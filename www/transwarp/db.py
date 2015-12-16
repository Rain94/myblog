# -*- coding: utf-8 -*-

import threading, functool

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

def connection():
	return _ConnectionCtx()

def with_connection(func):
	@functools.warps(func)
	def _warpper(*args, *kw):
		with _ConnectionCtx():
			return func(*args, *kw)
	return _warpper


