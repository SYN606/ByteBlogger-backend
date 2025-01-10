import os
ENV = os.getenv("ENVIRONMENT")

if ENV == "production":
    from .production import *
else:
    from .development import *
