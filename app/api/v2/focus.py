from flask import g, jsonify

from app.libs.error_code import FocusExist, DeleteSuccess
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.focuson import Focuson
from app.models.user import User
from app.validators.forms import UserForm

api = Redprint('focus')


@api.route('/add', methods=['POST'])
@auth.login_required
def add_focus():
    form = UserForm().validate_for_api()
    uid = g.user.uid
    User.query.filter_by(id=uid).first_or_404()
    User.query.filter_by(id=form.user_id.data).first_or_404()
    focus = Focuson.query.filter_by(user1_id=uid,user2_id=form.user_id.data).first()
    if focus:
        return FocusExist()
    focus_id = Focuson.up_by_mina(uid, form.user_id.data)
    return focus_id


@api.route('/self', methods=['POST'])
@auth.login_required
def self_focus():
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    focuses = user.user_relate_focuson1
    focuses.reverse()
    users = []
    for focus in focuses:
        if focus.status == 1:
            user = focus.focuson2_relate_user
            user_information = {"user_id": user.id, "profile": user.profile, "nickname": user.nickname}
            users.append(user_information)
    return jsonify(users)


@api.route('/me', methods=['POST'])
@auth.login_required
def me_focus():
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    focuses = user.user_relate_focuson2
    focuses.reverse()
    users = []
    for focus in focuses:
        if focus.status == 1:
            user = focus.focuson1_relate_user
            user_information = {"user_id": user.id, "profile": user.profile, "nickname": user.nickname}
            users.append(user_information)
    return jsonify(users)


@api.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_focus():
    form = UserForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        focus = Focuson.query.filter_by(user1_id=uid, user2_id=form.user_id.data).first_or_404()
        focus.delete()
    return DeleteSuccess()
