import time
from datetime import datetime

import os
import random
import string

from flask import g, current_app, jsonify, request
from sqlalchemy import desc

from app.libs.error_code import Success, DeleteSuccess, NotFound, SizeOverflow, FormatErrors
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.leavingmessage import Message, MessageStar, MessageComment
from app.models.user import User
from app.validators.forms import MessageForm, MessageDeleteForm, MessageLookForm, MessageStarAddForm, \
    MessageStarDelForm, MessageCommentAddForm, MyTimeForm

api = Redprint('message')


@api.route('/add', methods=['POST'])
@auth.login_required
def add_message():
    uid = g.user.uid
    form = MessageForm().validate_for_api()
    id = Message.add_message(uid,form.message.data, form.kind.data, form.hidden.data)
    return id


@api.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_message():
    form = MessageDeleteForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        message = Message.query.filter_by(id=form.message_id.data, user_id=uid).first_or_404()
        message.delete()
    return DeleteSuccess()


@api.route('/look', methods=['POST'])
@auth.login_required
def look_message():
    form = MessageLookForm().validate_for_api()
    page = current_app.config['PAGE']
    message_filters = Message.query.filter_by()
    uid = g.user.uid
    if form.user_id.data:
        message_filters = message_filters.filter_by(user_id=form.user_id.data, hidden=0)
    if form.search.data:
        q = '%' + form.search.data + '%'
        message_filters = message_filters.filter(Message.content.like(q))
    if form.onlyMe.data == 1:
        user = User.query.filter_by(id=uid).first_or_404()
        message_filters = message_filters.filter_by(user_id=uid)
    x = form.kind.data
    if form.kind.data and form.kind.data!=0:
        message_filters = message_filters.filter_by(kind=form.kind.data)
    if form.order.data == 0 or not form.order.data:
        message_filters = message_filters.order_by(desc(Message.create_time))
    else:
        message_filters = message_filters.order_by(desc(Message.hot))
    start = form.page.data * page - page
    messages = message_filters.limit(page).offset(start).all()
    # if form.onlyMe.data == 1:
    #     uid = g.user.uid
    #
    #     user = User.query.filter_by(id=uid).first_or_404()
    #     if form.kind.data == 0:
    #         messages = Message.query.filter_by(user_id=uid) \
    #             .order_by(desc(Message.create_time)).all()
    #     else:
    #         messages = Message.query.filter_by(user_id=uid,kind=form.kind.data)\
    #              .order_by(desc(Message.create_time)).all()
    # else:
    #     if form.kind.data == 0:
    #         messages = Message.query.filter_by().order_by(
    #             desc(Message.create_time)).all()
    #     else:
    #         messages = Message.query.filter_by(kind=form.kind.data)\
    #             .order_by(desc(Message.create_time)).all()
    # messages = messages[form.page.data * page - page:form.page.data * page]
    for message in messages:
        if message.status == 0:
            messages.remove(message)
    json_messages = jsonify(messages)
    users = []
    if messages:
        for message in messages:
            users.append(message.message_relate_user)
    users = jsonify(users)
    if users:
        i = 0
        for message in json_messages.json:
            if message['hidden'] == 1:
                message['user_id'] = None
                message['profile'] = None
                message['nickname'] = None
            else:
                message['profile'] = (users.json[i]['profile'])
                message['nickname'] = (users.json[i]['nickname'])

            is_star = MessageStar.query.filter_by(message_id=message['id'],user_id=uid).all()
            if is_star:
                message['is_star'] = 1
            else:
                message['is_star'] = 0
            if message['user_id'] == uid:
                message['isMine'] = 1
            else:
                message['isMine'] = 0
            comments = MessageComment.query.filter_by(message_id=message['id']).all()
            json_comments = jsonify(comments)
            comments_users = []
            if comments:
                for comment in comments:
                    comments_users.append(comment.message_comment_relate_user)
            comments_users = jsonify(comments_users)
            if comments_users:
                j = 0
                for comment in json_comments.json:
                    comment['nickname'] = comments_users.json[j]['nickname']
                    comment['profile'] = comments_users.json[j]['profile']
                    if comment['user_id'] == uid:
                        comment['isMine'] = 1
                    else:
                        comment['isMine'] = 0
                    if comments[j].parent:
                        parent = comments[j].comment_parent.message_comment_relate_user
                        comment['parent_id'] = parent['id']
                        comment['parent_nickname'] = parent['nickname']
                        comment['parent_profile'] = parent['profile']
                    j = j + 1
            message['comment'] = json_comments.json

            i = i+1
    return jsonify(json_messages.json)


@api.route('/upimage/<message_id>/<image_id>', methods=['POST'])
@auth.login_required
def up_image(message_id,image_id):
    uid = g.user.uid
    message_id = int(message_id)
    image_id = int(image_id)
    if image_id > 3 or image_id < 1:
        return NotFound()
    message = Message.query.filter_by(id=message_id,user_id=uid).first_or_404()

    cl = request.content_length
    if cl is not None and cl > 3 * 1024 * 1024:
        return SizeOverflow()
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    #获取图片文件 name = upload
    img = request.files.get('upload')
    #定义一个图片存放的位置 存放在static下面
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
    path = basedir+"/static/image/"
    #图片名称 给图片重命名 为了图片名称的唯一性
    imgName = ran_str+"_message"+str(message_id)+"_"+str(image_id)+"."+my_format
    imgName = imgName.replace('"',"")
    #图片path和名称组成图片的保存路径
    file_path = path+imgName
    file_path =  file_path.replace("\\","/")
    #保存图片
    img.save(file_path)
    #这个是图片的访问路径，需返回前端（可有可无）
    url = imgName
    #返回图片路径 到前端

    with db.auto_commit():
        if image_id == 1:
            if message.image1:
                os.remove(path + message.image1)
            message.image1 = url
        if image_id == 2:
            if message.image2:
                os.remove(path + message.image2)
            message.image2 = url
        if image_id == 3:
            if message.image3:
                os.remove(path + message.image3)
            message.image3 = url
        db.session.add(message)
    return url


@api.route('/star/add', methods=['POST'])
@auth.login_required
def star_add():
    uid = g.user.uid
    form = MessageStarAddForm().validate_for_api()
    id = MessageStar.add_star(uid, form.message_id.data)
    return id


@api.route('/star/delete', methods=['DELETE'])
@auth.login_required
def star_delete():
    form = MessageStarDelForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        message_star = MessageStar.query.filter_by(message_id=form.message_id.data, user_id=uid).first_or_404()
        message_star.delete()
        message = Message.query.filter_by(id=form.message_id.data).first_or_404()
        message.hot = message.hot - 1
    return DeleteSuccess()


@api.route('/comment/add', methods=['POST'])
@auth.login_required
def comment_add():
    uid = g.user.uid
    form = MessageCommentAddForm().validate_for_api()
    id = MessageComment.add_comment\
        (uid, form.message_id.data, form.content.data, form.parent.data)
    return id


@api.route('/comment/new', methods=['POST'])
@auth.login_required
def comment_new():
    uid = g.user.uid
    form = MyTimeForm().validate_for_api()
    t = time.strptime(form.time.data, "%Y-%m-%d %H:%M:%S")
    my_time = int(time.mktime(t))
    comments = MessageComment.query\
        .filter(MessageComment.status == 1,
                MessageComment.comment_relate_message.has(Message.user_id == uid) ,
                MessageComment.create_time > my_time) \
        .order_by(desc(MessageComment.create_time)).limit(99).all()
    json_comments = jsonify(comments)
    comments_users = []
    if comments:
        for comment in comments:
            comments_users.append(comment.message_comment_relate_user)
    comments_users = jsonify(comments_users)
    if comments_users:
        j = 0
        for comment in json_comments.json:
            comment['nickname'] = comments_users.json[j]['nickname']
            comment['profile'] = comments_users.json[j]['profile']
            if comment['user_id'] == uid:
                comment['isMine'] = 1
            else:
                comment['isMine'] = 0
            message = comments[j].comment_relate_message
            comment['message_content'] = message.content
            comment['message_image1'] = message.image1
            comment['message_image2'] = message.image2
            comment['message_image3'] = message.image3
            j = j + 1
    r = {"comments_num":len(json_comments.json),"comments":json_comments.json}
    return jsonify(r)


@api.route('/star/new', methods=['POST'])
@auth.login_required
def star_new():
    uid = g.user.uid
    form = MyTimeForm().validate_for_api()
    t = time.strptime(form.time.data, "%Y-%m-%d %H:%M:%S")
    my_time = int(time.mktime(t))
    stars = MessageStar.query\
        .filter(MessageStar.status == 1,
                MessageStar.star_relate_message.has(Message.user_id == uid) ,
                MessageStar.create_time > my_time) \
        .order_by(desc(MessageStar.create_time)).limit(99).all()
    json_stars = jsonify(stars)
    stars_users = []
    if stars:
        for star in stars:
            stars_users.append(star.message_star_relate_user)
    stars_users = jsonify(stars_users)
    if stars_users:
        j = 0
        for star in json_stars.json:
            star['nickname'] = stars_users.json[j]['nickname']
            star['profile'] = stars_users.json[j]['profile']
            message = stars[j].star_relate_message
            star['message_content'] = message.content
            star['message_image1'] = message.image1
            star['message_image2'] = message.image2
            star['message_image3'] = message.image3
            j = j + 1
    r = {"comments_num":len(json_stars.json),"comments":json_stars.json}
    return jsonify(r)
