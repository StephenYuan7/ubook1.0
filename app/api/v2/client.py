from datetime import datetime
import os
import random
import string

import requests
from flask import current_app, jsonify, g, request, send_from_directory, render_template
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, \
    BadSignature

from app.config.secure import APPID, SECRET
from app.libs.error_code import Success, NotFound, UserExist, DeleteSuccess, SizeOverflow, FormatErrors
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.activity import Activity
from app.models.attention import Attention
from app.models.base import db
from app.models.chattingrecord import Chattingrecord
from app.models.commit import Commit
from app.models.focuson import Focuson
from app.models.interest import Interest
from app.models.interesttag import Interesttag
from app.models.leavingmessage import Message
from app.models.product import Product
from app.models.school import School
from app.models.schoolbook import Schoolbook
from app.models.transaction import Transaction
from app.models.user import User
from app.validators.forms import ClientForm, MinacodeForm, ClientResetForm, ProfileForm, MyPageForm
from app.validators.image import image_check

api = Redprint('client')


@api.route('/check', methods=['POST'])
def check_client():
    # form = MinacodeForm().validate_for_api()
    # CODE = form.code.data
    # url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}' \
    #       '&grant_type=authorization_code'.format(appid=APPID, secret=SECRET, code=CODE)
    # res = requests.get(url)
    # openid = res.json().get('openid')
    # session_key = res.json().get('session_key')
    openid = '668'
    user = User.query.filter_by(openid=openid).first()
    if user:
        expiration = current_app.config['TOKEN_EXPIRATION']
        scope = 'AdminScope' if user.auth == 2 else 'UserScope'
        token = generate_auth_token(user.id,
                                    scope,
                                    expiration)
        t = {'registered': 1, 'session': token.decode('ascii')}
        return jsonify(t), 201
    else:
        t = {'registered': 0}
        return jsonify(t)


@api.route('/create', methods=['POST'])
def create_client():
    form = ClientForm().validate_for_api()
    CODE = form.code.data
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}' \
          '&grant_type=authorization_code'.format(appid=APPID, secret=SECRET, code=CODE)
    res = requests.get(url)
    openid = res.json().get('openid')
    session_key = res.json().get('session_key')
    openid = '668'
    user = User.query.filter_by(openid=openid).first()
    # if user:
    #     return UserExist()
    # school = School.query.filter_by(name=form.school.data).first_or_404()
    # school_id = school.id
    User.register_by_mina(openid,
                          form.real_name.data,
                          form.user_academy.data,
                          form.nickname.data,
                          form.school_id.data,
                          form.user_grade.data,
                          form.student_number.data,
                          form.qq.data)
    user = User.query.filter_by(openid=openid).first()
    if user:
        expiration = current_app.config['TOKEN_EXPIRATION']
        scope = 'AdminScope' if user.auth == 2 else 'UserScope'
        token = generate_auth_token(user.id,
                                    scope,
                                    expiration)
        t = {'registered': 1, 'session': token.decode('ascii')}
        return jsonify(t), 201
    return Success()


@api.route('/reset', methods=['POST'])
@auth.login_required
def reset_client():
    uid = g.user.uid
    with db.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        form = ClientResetForm().validate_for_api()
        user.real_name = form.real_name.data
        user.user_academy = form.user_academy.data
        user.nickname = form.nickname.data
        user.school_id = form.school_id.data
        user.user_grade = form.user_grade.data
        user.student_number = form.student_number.data
        user.qq = form.qq.data
    return Success()


@api.route('/profile', methods=['POST'])
@auth.login_required
def add_profile():
    uid = g.user.uid
    with db.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        form = ProfileForm().validate_for_api()
        user.profile = form.profile.data
    return Success()


@api.route('/upprofile', methods=['POST'])
@auth.login_required
def up_profile():
    uid = g.user.uid
    cl = request.content_length
    if cl is not None and cl > 3 * 1024 * 1024:
        return SizeOverflow()
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    # 获取图片文件 name = upload
    img = request.files.get('upload')
    # image_check(img)
    # 定义一个图片存放的位置 存放在static下面
    allow_ext = ["jpg", "png"]
    if img.filename.find('.'):
        my_format = img.filename.rsplit('.', 1)[1].strip().lower()
        if my_format[-1] == '"':
            my_format = my_format[:-1]
    else:
        return FormatErrors()
    if my_format not in allow_ext:
        return FormatErrors()
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    path = basedir + "/static/image/"
    # 图片名称 给图片重命名 为了图片名称的唯一性
    imgName = ran_str + '_' + str(uid) + "_profile." + my_format
    imgName = imgName.replace('"', "")
    # 图片path和名称组成图片的保存路径
    file_path = path + imgName
    file_path = file_path.replace("\\", "/")
    # 保存图片
    img.save(file_path)
    # 这个是图片的访问路径，需返回前端（可有可无）
    url = imgName
    # 返回图片路径 到前端

    image_check(file_path)
    with db.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        if user.profile and user.profile != 'default.jpg':
            if os.path.exists(path + user.profile):
                os.remove(path + user.profile)
        user.profile = url
        db.session.add(user)
    return url


@api.route('/download/<image>', methods=['GET'])
def download_image(image):
    # basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    path = "image/" + image
    return render_template("image.html", image_name=path)


@api.route('/information/self', methods=['POST'])
@auth.login_required
def self_information():
    uid = g.user.uid
    with db.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
    return jsonify(user)


@api.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_client():
    uid = g.user.uid
    with db.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        user.delete()
    return DeleteSuccess()


@api.route('/all/delete', methods=['DELETE'])
def delete_all_client():
    with db.auto_commit():
        users = User.query.order_by(User.create_time).all()
        for user in users:
            user.delete()
    return DeleteSuccess()


@api.route('/my/page', methods=['POST'])
@auth.login_required
def my_page():
    form = MyPageForm().validate_for_api()
    if form.user_id.data == 0:
        uid = g.user.uid
    else:
        uid = form.user_id.data
    user = User.query.filter_by(id=uid).first_or_404()
    focus_length = 0
    for focus in user.user_relate_focuson2:
        if focus.status == 1:
            focus_length = focus_length + 1
    products = user.user_relate_product
    page = current_app.config['PAGE']
    products = products[form.product_page.data * page - page:form.product_page.data * page]
    for product in products:
        if product.status == 0:
            products.remove(product)
    commits = user.user_relate_commit2
    commits = commits[form.commit_page.data * page - page:form.commit_page.data * page]
    for commit in commits:
        if commit.status == 0:
            commits.remove(commit)
    time = (datetime.now() - user.create_datetime).days
    if Focuson.query.filter_by(user1_id=g.user.uid, user2_id=uid).first():
        is_focus = 1
    else:
        is_focus = 0
    if Focuson.query.filter_by(user1_id=uid, user2_id=g.user.uid).first():
        is_be_focus = 1
    else:
        is_be_focus = 0
    page = {"id": user.id, "profile": user.profile, "nickname": user.nickname, "credibility": user.credibility,
            "focus": focus_length, "products": products, "commits": commits, "time": time, "is_focus": is_focus,
            "is_be_focus": is_be_focus, "qq": user.qq}
    return jsonify(page)


@api.route('/profile', methods=['DELETE'])
@auth.login_required
def delete_profile():
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    path = basedir + "/static/image/"
    with db.auto_commit():
        os.remove(path + user.profile)
        user.profile = None
    return DeleteSuccess()


def generate_auth_token(uid, scope=None,
                        expiration=7200):
    """生成令牌"""
    s = Serializer(current_app.config['SECRET_KEY'],
                   expires_in=expiration)
    return s.dumps({
        'uid': uid,
        'type': 200,
        'scope': scope
    })
