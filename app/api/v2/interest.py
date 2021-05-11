from flask import request, g, jsonify

from app.libs.error_code import Success, InterestExist
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.interest import Interest
from app.models.interesttag import Interesttag
from app.models.user import User

api = Redprint('interest')


@api.route('/add', methods=['POST'])
@auth.login_required
def add_interest():
    uid = g.user.uid
    interests = request.json['interest']
    myinterests = Interest.query.filter_by(user_id=uid).all()
    with db.auto_commit():
        for interest in myinterests:
            if interest.tag_id in interests:
                # 找到了，将刷新列表中元素删除
                interests.remove(interest.tag_id)
            else:
                interest.delete()
        for x in interests:
            Interest.add_interest(uid, x)
    return Success()


@api.route('/my', methods=['POST'])
@auth.login_required
def my_interest():
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    interests = user.user_relate_interest
    tag_id = []
    for interest in interests:
        if interest.status == 1:
            tag_id.append(interest.tag_id)
    return jsonify(tag_id)
