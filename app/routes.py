from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import json
import datetime
from app.forms import LoginForm, RegisterForm
from app import app, db
from app.Models import Course, User
from sqlalchemy import and_, desc, asc, or_


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # 如果已经登陆，跳转到首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        # 将数据填入User表
        user = User(
            user_name=data["user_name"],
            email=data["email"],
            password=generate_password_hash(data["password"])
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('邮箱和密码不匹配', 'danger')
    return render_template('login.html', form=form)


@app.route('/')
def index():
    free_course = Course.query.filter_by(original_price=0).order_by(desc('learner_count')).limit(6).all()
    hot_course = Course.query.filter(Course.original_price > 0).order_by(desc('learner_count')).limit(6).all()
    return render_template('index.html', free_course=free_course, hot_course=hot_course)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/change_pwd')
@login_required
def change_pwd():
    return '修改密码'


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/course/<course_id>')
def detail(course_id):
    course = Course.query.filter_by(course_id=course_id).first_or_404()
    return render_template('detail.html', course=course)


@app.route('/course_data/<course_id>/type/<type>')
def course_data(course_id, type):
    if type == 'week':
        title = '最近一周销量'
        condition = f'WHERE course_id = {course_id} and DATE_SUB(CURDATE(),INTERVAL 7 DAY) <= DATE(create_time)'
        sql = f'SELECT create_time,learner_count from sale {condition} ORDER BY create_time' # 最近一周
        sale_data = db.session.execute(sql)
    elif type == 'month':
        title = '最近一月销量'
        condition = f'WHERE course_id = {course_id} and DATE_SUB(CURDATE(),INTERVAL 1 MONTH) <= DATE(create_time)'
        sql = f'SELECT create_time,learner_count from sale {condition} ORDER BY create_time'  # 最近一周
        sale_data = db.session.execute(sql)
    else:
        year = datetime.datetime.today().year
        days = []
        for i in range(1,13):
            days.append(f'{year}-{i:02}-01')

        title = '本年度每月销量'  # 每月一号
        condition = f"WHERE course_id = {course_id} and create_time in {tuple(days)}"
        sql = f'SELECT create_time,learner_count from sale {condition} ORDER BY create_time'  # 最近一周
        sale_data = db.session.execute(sql)
    data = {}
    create_time = []
    learner_count = []
    for item in sale_data:
        create_time.append(item[0].strftime('%m-%d'))
        learner_count.append(item[1])
    data['title'] = title
    data['categories'] = create_time
    data['data'] = learner_count
    result = json.dumps(data)
    return result


@app.route('/course/')
def course_list():
    page = request.args.get('page', 1, type=int)
    # 处理tag
    tag = request.args.get('tag', 'common')
    if tag == 'common':  # 综合
        condition = and_(Course.original_price > 0, Course.score > 4.8)
    elif tag == 'free':  # 免费
        condition = (Course.original_price == 0)
    else:
        price = tag.split('-')
        print(price[0])
        print(price[1])
        if 'gt' in price:
            condition = (Course.original_price > price[0])
        else:
            condition = (Course.original_price.between(price[0], price[1]))
    # 接受order参数，默认为评分
    order = request.args.get('order', 'score')
    if order == 'price-desc':
        order_condition = desc(Course.original_price)
    elif order == 'price-asc':
        order_condition = asc(Course.original_price)
    else:
        order_condition = desc(order)
    courses = Course.query.filter(condition).order_by(order_condition).paginate(page, per_page=20)
    return render_template('courses.html', courses=courses)


@app.route('/search/')
def search():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    if not keyword:
        return redirect(url_for(course_list))
    condition1 = (Course.product_name.like('%' + keyword + '%'))
    condition2 = (Course.provider.like('%' + keyword + '%'))
    courses = Course.query.filter(or_(condition1, condition2)).paginate(page, per_page=20)
    return render_template('search.html', courses=courses, keyword=keyword)


@app.route('/collect/<course_id>')
@login_required
def collect(course_id):
    # 判断是否收藏过
    if current_user.is_favorite(course_id):
        # 取消收藏
        if current_user.del_favorite(course_id):
            data = {'result': 'success'}
        else:
            data = {'result': 'error'}
    else:
        # 添加收藏
        if current_user.add_favorite(course_id):
            data = {'result': 'success'}
        else:
            data = {'result': 'error'}
    return json.dumps(data)


@app.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    courses = current_user.favorites.paginate(page, per_page=20)
    return render_template('favorites.html', courses=courses)