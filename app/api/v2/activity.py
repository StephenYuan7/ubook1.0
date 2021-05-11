import os
import random
import string
import time

from flask import current_app, jsonify, g, request
from sqlalchemy import desc, or_

from app.libs.error_code import SizeOverflow, FormatErrors, Success, DeleteSuccess
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.activity import Activity
from app.models.base import db
from app.models.user import User
from app.validators.forms import ActivityForm, ActivityAddForm, ActivityRenewForm, ActivityDeleteForm

api = Redprint('activity')


@api.route('/look', methods=['POST'])
@auth.login_required
def look_activity():
    form = ActivityForm().validate_for_api()
    page = current_app.config['PAGE']
    q = '%' + form.key.data + '%'
    activities = Activity.query.filter(or_(Activity.title.like(q), Activity.description.like(q)),
                                       Activity.school_id == form.school_id.data) \
        .order_by(desc(Activity.activity_time)).all()
    # activities = Activity.query.filter_by(school_id=form.school_id.data)\
    #     .order_by(desc(Activity.activity_time)).all()
    activities = activities[form.page.data * page - page:form.page.data * page]
    activities = jsonify(activities)
    uid = g.user.uid
    for activity in activities.json:
        activity['activity_time'] = time.localtime(activity['activity_time'])
        activity['activity_time'] = time.strftime("%Y-%m-%d %H:%M:%S", activity['activity_time'])
        activity['over_time'] = time.localtime(activity['over_time'])
        activity['over_time'] = time.strftime("%Y-%m-%d %H:%M:%S", activity['over_time'])
        if uid == activity['user_id']:
            activity['isme'] = 1
        else:
            activity['isme'] = 0
    return jsonify(activities.json)


@api.route('/add', methods=['POST'])
@auth.login_required
def add_activity():
    form = ActivityAddForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    t = time.strptime(form.activity_time.data, "%Y-%m-%d %H:%M:%S")
    activity_time = int(time.mktime(t))
    t = time.strptime(form.over_time.data, "%Y-%m-%d %H:%M:%S")
    over_time = int(time.mktime(t))
    activity_id = Activity().up_by_mina(form.organizer.data, activity_time,
                                        over_time, form.description.data,
                                        form.title.data,
                                        user.school_id, uid)
    return activity_id


@api.route('/upimage/<activity_id>', methods=['POST'])
@auth.login_required
def up_image(activity_id):
    uid = g.user.uid
    activity_id = int(activity_id)
    activity = Activity.query.filter_by(id=activity_id, user_id=uid).first_or_404()

    cl = request.content_length
    if cl is not None and cl > 3 * 1024 * 1024:
        return SizeOverflow()
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    # 获取图片文件 name = upload
    img = request.files.get('icon')
    if img:
        icon_or_img = 'icon'
    else:
        img = request.files.get('image')
        icon_or_img = 'image'
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
    imgName = ran_str + '_activity' + str(activity_id) + '_' + icon_or_img + "." + my_format
    imgName = imgName.replace('"', "")
    # 图片path和名称组成图片的保存路径
    file_path = path + imgName
    file_path = file_path.replace("\\", "/")
    # 保存图片
    img.save(file_path)
    # 这个是图片的访问路径，需返回前端（可有可无）
    url = imgName
    # 返回图片路径 到前端

    with db.auto_commit():
        if icon_or_img == 'icon':
            if activity.icon:
                os.remove(path + activity.icon)
            activity.icon = url
        else:
            if activity.image:
                os.remove(path + activity.image)
            activity.image = url
        db.session.add(activity)

    return url


@api.route('/renew', methods=['POST'])
@auth.login_required
def renew_activity():
    form = ActivityRenewForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first()
    t = time.strptime(form.activity_time.data, "%Y-%m-%d %H:%M:%S")
    activity_time = int(time.mktime(t))
    t = time.strptime(form.over_time.data, "%Y-%m-%d %H:%M:%S")
    over_time = int(time.mktime(t))
    with db.auto_commit():
        activity = Activity.query.filter_by(id=form.activity_id.data, user_id=uid).first_or_404()
        activity.organizer = form.organizer.data
        activity.activity_time = activity_time
        activity.over_time = over_time
        activity.description = form.description.data
        activity.title = form.title.data
    return Success()


@api.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_activity():
    form = ActivityDeleteForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first()
    with db.auto_commit():
        activity = Activity.query.filter_by(id=form.activity_id.data, user_id=uid).first_or_404()
        activity.delete()
    return DeleteSuccess()
