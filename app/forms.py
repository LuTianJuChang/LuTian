from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.Models import User
import email_validator


class RegisterForm(FlaskForm):
    user_name = StringField('用户名',
    validators = [
        DataRequired(message="用户名不能为空"),
        Length(min=2, max=25, message='密码长度为2-25个字符')
    ])
    email = StringField('邮箱',
                        validators=[
                            DataRequired(message="邮箱不能为空"),
                            Email(message="无效的邮箱地址")])
    password = PasswordField('密码',
                             validators=[
                                 DataRequired(message="密码不能为空"),
                                 Length(min=6, max=25, message='密码长度为6-25个字符'),
                             ])
    confirm_password = PasswordField('确认密码',
                                     validators=[
                                         DataRequired(message="确认密码不能为空"),
                                         EqualTo('password', message="2次输入密码不一致")])

    # 检测用户名是否存在
    def validate_username(self, field):
        if User.query.filter_by(user_name=field.data).first():
            raise ValidationError('用户名已被注册')

    # 检测邮箱是否存在
    def validate_email(self, field):
        if User.query.filter_by(user_name=field.data).first():
            raise ValidationError('邮箱已被注册')


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[
        DataRequired(message="邮箱不能为空"),
        Email(message="无效的邮箱地址")
    ])
    password = PasswordField('密码', validators=[DataRequired(message="密码不能为空"), Length(min=6,max=25, message="密码长度为6~25个字符")])