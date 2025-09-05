from flask_sqlalchemy import SQLAlchemy
from flask_security import Security
from flask_mailman import Mail
from celery import Celery, Task
from flask_caching import Cache

db = SQLAlchemy()
security = Security()
celery = Celery()
mail = Mail()
cache = Cache()

def init_extensions(app, user_datastore):
    db.init_app(app)

    security.init_app(app, user_datastore)

    mail.init_app(app)

    cache.init_app(app)

def make_celery(app):

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.conf.update(app.config)
    celery.Task = ContextTask    

# error handling