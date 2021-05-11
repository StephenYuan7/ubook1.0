import json

from flask import g, current_app, jsonify, request
from flask_socketio import join_room, emit, leave_room
from sqlalchemy import or_, and_, desc

from geventwebsocket.websocket import WebSocket,WebSocketError
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from app.extension.websocket import socketio
from app.libs.error_code import Success, NotFound
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.chattingrecord import Chattingrecord
from app.models.user import User
from app.validators.forms import ChattingAddForm, ChattingGetForm, ChattingTypeChangeForm

api = Redprint('chatting')


@api.route('/add', methods=['POST'])
@auth.login_required
def add_chatting():
    form = ChattingAddForm().validate_for_api()
    uid = g.user.uid
    User.query.filter_by(id=uid).first_or_404()
    User.query.filter_by(id=form.user_id.data).first_or_404()
    chatting = Chattingrecord.up_by_mina(uid, form.user_id.data, form.text.data,form.type.data)
    chatting = jsonify(chatting)
    emit('chatting', chatting, room=form.user_id.data,namespace='/')
    return chatting


@api.route('/get', methods=['POST'])
@auth.login_required
def get_chatting():
    form = ChattingGetForm().validate_for_api()
    uid = g.user.uid
    chatting = Chattingrecord.query.\
        filter(Chattingrecord.status == 1,
               or_(and_(Chattingrecord.user1_id == uid,Chattingrecord.user2_id == form.user_id.data),
                   and_(Chattingrecord.user1_id == form.user_id.data,Chattingrecord.user2_id == uid)))\
        .order_by(desc(Chattingrecord.create_time)).all()
    page = current_app.config['PAGE']
    chatting = chatting[form.page.data * page - page:form.page.data * page]
    chatting.reverse()
    myself = User.query.filter_by(id=uid).first_or_404()
    opponent = User.query.filter_by(id=form.user_id.data).first_or_404()
    information = {"information": {"my_profile": myself.profile, "my_nickname": myself.nickname
                   , "opponent_profile": opponent.profile, "opponent_nickname": opponent.nickname},
                   "chatting": chatting}
    return jsonify(information)


@api.route('/type', methods=['POST'])
@auth.login_required
def change_type():
    form = ChattingTypeChangeForm().validate_for_api()
    uid = g.user.uid
    chatting = Chattingrecord.query.filter_by(user2_id=uid,id=form.id.data).first_or_404()
    with db.auto_commit():
        chatting.type = form.type.data
    return Success()


# @socketio.on('join')
# # @api.route('/join', methods=['POST'])
# @auth.login_required
# def on_join():
#     room = g.user.uid
#     join_room(room)
#     emit(g.user.uid + ' has entered the room.', room=room)
#
#
# @socketio.on('leave')
# @auth.login_required
# def on_leave():
#     room = g.user.uid
#     leave_room(room)
#     emit(g.user.uid + ' has left the room.', room=room)

user_socket_list = []
user_socket_dict={}


@api.route('/ws')
@auth.login_required
def ws():
    user_socket = request.environ.get("wsgi.websocket")
    if not user_socket:
        return "请以WEBSOCKET方式连接"

    user_socket_dict[g.user.uid]=user_socket
    print(user_socket_dict)

    while True:
        try:
            user_msg = user_socket.receive()
            user_msg= json.loads(user_msg)
            User.query.filter_by(id=g.user.uid).first_or_404()
            User.query.filter_by(id=user_msg.get("user_id")).first_or_404()
            Chattingrecord.up_by_mina(g.user.uid, user_msg.get("user_id"),
                                      user_msg.get("text"), user_msg.get("type"))
            to_user_socket = user_socket_dict.get(user_msg.get("user_id"))
            send_msg={
                "text":user_msg.get("text"),
                "type":user_msg.get("type"),
                "send_user":g.user.uid
            }
            to_user_socket.send(json.dumps(send_msg))
        except WebSocketError as e:
            user_socket_dict.pop(g.user.uid)
            print(user_socket_dict)
            print(e)
