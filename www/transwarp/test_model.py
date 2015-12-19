import logging, models.py, db

logging.basicConfig(level = DEBUG)

#db.create_engine(user = 'root', password = 'immaslcs520', database = 'myblog', host = '127.0.0.1', port = '3306')

print models.User.__sql__