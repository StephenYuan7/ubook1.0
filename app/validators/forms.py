"""
构建各种类型的验证器
"""

from wtforms import StringField, IntegerField, FloatField
from wtforms.validators import DataRequired, length, ValidationError, Regexp, EqualTo, NumberRange, InputRequired

from app.libs.enums import ClientTypeEnum, BookLocation, Booktype, SearchMethod, Academy
from app.validators.base import BaseForm as Form

# 验证用户
from app.models.user import User


class ClientForm(Form):
    code = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=500
    )])
    nickname = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=30
    )])
    real_name = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=50
    )])
    school_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    user_academy = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=30
    )])
    user_grade = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=7
    )])
    student_number = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=10, max=10
    )])
    qq = IntegerField(validators=[DataRequired(message='不允许为空')])


class MinacodeForm(Form):
    code = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=500
    )])


class ClientResetForm(Form):
    nickname = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=30
    )])
    real_name = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=50
    )])
    school_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    user_academy = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=30
    )])
    user_grade = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=7
    )])
    student_number = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=10, max=10
    )])
    qq = IntegerField(validators=[DataRequired(message='不允许为空')])


class ProfileForm(Form):
    profile = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100
    )])


class MessageForm(Form):
    message = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=500
    )])
    kind = IntegerField()
    hidden = IntegerField()


class MessageDeleteForm(Form):
    message_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class MessageLookForm(Form):
    onlyMe = IntegerField()
    page = IntegerField(validators=[DataRequired()])
    kind = IntegerField()
    order = IntegerField()
    search = StringField()
    user_id = IntegerField()


class ActivityForm(Form):
    key = StringField(validators=[length(max=100)])
    school_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    page = IntegerField(validators=[DataRequired()])


class SchoolbookForm(Form):
    school_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    grade = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=7)])
    academy = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=30)])
    term = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=50)])
    page = IntegerField(validators=[DataRequired()])


class ProductUpForm(Form):
    currentPrice = FloatField()
    originalPrice = FloatField()
    title = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    description = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1000)])
    address = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    kind = IntegerField(validators=[DataRequired()])
    degree = IntegerField(validators=[DataRequired()])
    state = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1)])

    def validate_degree(self, value):
        if (value.data > 100) or (value.data < 0):
            raise ValidationError()


class ProductDeleteForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class PageForm(Form):
    page = IntegerField(validators=[DataRequired(message='不允许为空')])


class ProductSearchForm(Form):
    key = StringField(validators=[length(max=100)])
    kind = IntegerField()
    method = IntegerField()
    school_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    page = IntegerField(validators=[DataRequired(message='不允许为空')])

    def validate_method(self, value):
        if (value.data > 3) or (value.data < 0):
            raise ValidationError()


class AttentionAddForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class AttentionDeleteForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class ProductChangeStateForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    state = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1)])


class UserForm(Form):
    user_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class MyPageForm(Form):
    user_id = IntegerField()
    product_page = IntegerField(validators=[DataRequired(message='不允许为空')])
    commit_page = IntegerField(validators=[DataRequired(message='不允许为空')])


class ChattingAddForm(Form):
    user_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    text = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=500)])
    type = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1)])


class ChattingGetForm(Form):
    user_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    page = IntegerField(validators=[DataRequired(message='不允许为空')])


class ProductRenewForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    currentPrice = FloatField()
    originalPrice = FloatField()
    title = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    description = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1000)])
    address = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    kind = IntegerField(validators=[DataRequired()])
    degree = IntegerField(validators=[DataRequired()])
    state = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1)])

    def validate_degree(self, value):
        if (value.data > 100) or (value.data < 0):
            raise ValidationError()


class ProductChangeCurrentPriceForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    currentPrice = FloatField()


class ProductGet(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class ProductImageDeleteForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    image = IntegerField(validators=[DataRequired(message='不允许为空')])

    def validate_image(self, value):
        if (value.data > 3) or (value.data < 1):
            raise ValidationError()


class ActivityAddForm(Form):
    organizer = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    activity_time = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    over_time = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    description = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=5000)])
    title = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])


class ActivityRenewForm(Form):
    organizer = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    activity_time = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    over_time = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    description = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=5000)])
    activity_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    title = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])


class ActivityDeleteForm(Form):
    activity_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class TransactionAddForm(Form):
    product_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    price = IntegerField()
    address = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
    order_time = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])


class TransactionLookForm(Form):
    page = IntegerField(validators=[DataRequired(message='不允许为空')])
    user_id = IntegerField()


class ChattingTypeChangeForm(Form):
    id = IntegerField(validators=[DataRequired(message='不允许为空')])
    type = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1)])


class TransactionConfirmForm(Form):
    id = IntegerField(validators=[DataRequired(message='不允许为空')])


class TransactionEvaluateForm(Form):
    id = IntegerField(validators=[DataRequired(message='不允许为空')])
    star = IntegerField(validators=[DataRequired(message='不允许为空')])
    evaluation = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=1000)])


class CountStarForm(Form):
    user_id = IntegerField()


class MessageStarAddForm(Form):
    message_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class MessageStarDelForm(Form):
    message_id = IntegerField(validators=[DataRequired(message='不允许为空')])


class MessageCommentAddForm(Form):
    message_id = IntegerField(validators=[DataRequired(message='不允许为空')])
    content = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=500
    )])
    parent = IntegerField()


class MyTimeForm(Form):
    time = StringField(validators=[DataRequired(message='不允许为空'), length(
        min=1, max=100)])
