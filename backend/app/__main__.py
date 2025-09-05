from flask import Flask, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

from app.models import models
from flask_security import SQLAlchemyUserDatastore, hash_password, auth_required
from flask_mailman import Mail

from flask_login import current_user

from app.routes.admin_controller import admin_controller
from app.routes.user_controller import user_controller

from app.extensions import init_extensions, db, make_celery

from app.config import Config

app = Flask(__name__)

app.config.from_object(Config)
celery = make_celery(app)

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
init_extensions(app, user_datastore)

app.register_blueprint(admin_controller)
app.register_blueprint(user_controller)


with app.app_context():
    
    db.create_all()

    if not models.Role.query.filter_by(name = 'admin').first():
        db.session.add(models.Role(name = 'admin', description = 'Administrator'))
    if not models.Role.query.filter_by(name='user').first():
        db.session.add(models.Role(name = 'user', description = 'Regular user'))
    db.session.commit()

    if not models.User.query.filter_by(username = app.config.get('ADMIN_USERNAME')).first():
        admin_role = models.Role.query.filter_by(name = 'admin').first()
        admin = models.User(
            username = app.config.get('ADMIN_USERNAME'),
            password = hash_password(app.config.get('ADMIN_PASSWORD')),
            email = app.config.get('ADMIN_EMAIL'),
            roles = [admin_role],  
        )
        db.session.add(admin)
        db.session.commit()

    # error handling

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authentication-Token'
    return response

from flask_security.signals import user_registered

@user_registered.connect_via(app)
def assign_user_role(sender, user, **extra):
    user_role = models.Role.query.filter_by(name = 'user').first()
    user.roles.append(user_role)
    db.session.commit()

@app.route('/api/me', methods=['GET'])
@auth_required('token')
def get_current_user():
    roles = [role.name for role in current_user.roles]
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'roles': roles
    })

if __name__ == "__main__":
    app.run(host = app.config['HOST'], port = app.config['PORT'], debug = app.config['DEBUG'])
