from apps.forms import BaseForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, Email, input_required, EqualTo


class cms_login_form(BaseForm):
    username = StringField(validators=[Length(min=6, max=16, message="用户名长度应为6-16位")])
    password = PasswordField(validators=[Length(min=8, max=16, message="密码长度应为8-16位")])

class update_info_form(BaseForm):
    username = StringField(validators=[Length(min=6, max=16, message="用户名长度应为6-16位")])
    email = StringField(validators=[Email(message="不是正确的邮箱格式")])
    realname = StringField(validators=[input_required(message="请输入姓名")])

class cms_user_add_form(BaseForm):
    username = StringField(validators=[Length(min=6, max=16, message="用户名长度应为6-16位")])
    password = PasswordField(validators=[Length(min=8, max=16, message="密码长度应为8-16位")])
    password_repeat = PasswordField(validators=[ EqualTo("password", message="密码输入不一致")])