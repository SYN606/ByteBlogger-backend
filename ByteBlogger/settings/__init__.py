import os

ENV = os.getenv("ENV", "development").lower()

if ENV == "production":
    from .prod import *
else:
    from .dev import *