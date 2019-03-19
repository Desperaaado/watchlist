import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(
            os.path.dirname(app.root_path), 
            os.getenv('DATABASE_FILE', 'data.db')
        )
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    user = User.query.get_or_404(int(user_id))
    return user

@app.context_processor
def inject_user():
    from app.models import User
    user = User.query.first()
    return dict(user=user)

from app import views, errors, commands