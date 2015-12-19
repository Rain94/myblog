import logging, models

logging.basicConfig(level = logging.DEBUG)

print models.User.__sql__
print models.Blog.__sql__
print models.Comment.__sql__
