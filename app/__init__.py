from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'lutian'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root:1234567qwertyu@localhost/lutian?charset=utf8mb4')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
# 配置flask_login
login_manager.login_view = 'login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'danger'
