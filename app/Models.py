from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def user_load(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    # 多对多关系
    favorites = db.relationship('Course', secondary='collections',
                                backref=db.backref('user', lazy='dynamic'),
                                lazy='dynamic')

    # 定义收藏相关的方法
    def is_favorite(self, course_id):
        courses = self.favorites.all()
        course_list = [course.course_id for course in courses]
        if course_id in course_list:
            return True

    def add_favorite(self, course_id):
        try:
            course = Course.query.get(course_id)
            self.favorites.append(course)
            db.session.commit()
            return True
        except Exception:
            return

    def del_favorite(self,course_id):
        try:
            course = Course.query.get(course_id)
            self.favorites.remove(course)
            db.session.commit()
            return True
        except Exception:
            return


class Course(db.Model):
    course_id = db.Column(db.String(100), primary_key=True, nullable=False)  # 课程id
    product_id = db.Column(db.String(100), nullable=False)  # 产品id
    product_type = db.Column(db.Integer, nullable=False)  # 产品类型
    product_name = db.Column(db.String(125), nullable=False)  # 产品名称
    provider = db.Column(db.String(125), nullable=False)  # 提供者
    score = db.Column(db.Float(2))  # 评分
    score_level = db.Column(db.Integer)  # 评分水平
    learner_count = db.Column(db.Integer)  # 学习人数
    lesson_count = db.Column(db.Integer)  # 课程计数
    lector_name = db.Column(db.String(125))  # 讲师名称
    original_price = db.Column(db.Float(2))  # 原价
    discount_price = db.Column(db.Float(2))  # 折扣价
    discount_rate = db.Column(db.Float(2))  # 折扣率
    img_url = db.Column(db.String(125))  # 小图网址
    big_img_url = db.Column(db.String(125))  # 大图网址
    description = db.Column(db.Text)  # 描述


class Sale(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    course_id = db.Column(db.String(100), db.ForeignKey('course.course_id'))
    product_name = db.Column(db.String(125), nullable=False)  # 产品名称
    learner_count = db.Column(db.Integer)  # 学习人数
    create_time = db.Column(db.Date, default=datetime.today())
    # 关联关系
    course = db.relationship('Course', backref=db.backref('sale', lazy='dynamic'))


collections = db.Table('collections',
         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
         db.Column('course_id', db.String(100), db.ForeignKey('course.course_id')))