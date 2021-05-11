from flask import g, current_app, jsonify

from app.libs.error_code import AttentionExist, DeleteSuccess
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.attention import Attention
from app.models.base import db
from app.models.user import User
from app.validators.forms import AttentionAddForm, PageForm, AttentionDeleteForm

api = Redprint('attention')


@api.route('/add', methods=['POST'])
@auth.login_required
def add_attention():
    form = AttentionAddForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    attention = Attention.query.filter_by(user_id=uid,product_id=form.product_id.data).first()
    if attention:
        return AttentionExist()
    attention_id = Attention.up_by_mina(uid, form.product_id.data)
    return attention_id


@api.route('/my', methods=['POST'])
@auth.login_required
def my_attention():
    form = PageForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    attentions = user.user_relate_attention
    attentions.reverse()
    page = current_app.config['PAGE']
    attentions = attentions[form.page.data * page - page:form.page.data * page]
    products = []
    for attention in attentions:
        if attention.status == 1 and attention.attention_relate_product.status == 1:
            products.append(attention.attention_relate_product)
    json_products = jsonify(products)
    users = []
    if products:
        for product in products:

            users.append(product.product_relate_user)
    users = jsonify(users)
    if users:
        i = 0
        for product in json_products.json:
            product['profile'] = (users.json[i]['profile'])
            product['nickname'] = (users.json[i]['nickname'])
            product['credibility'] = (users.json[i]['credibility'])
            product['attention'] = 1
            i = i + 1

    return jsonify(json_products.json)


@api.route('/delete',methods=['DELETE'])
@auth.login_required
def delete_attention():
    form = AttentionDeleteForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        attention = Attention.query.filter_by(product_id=form.product_id.data, user_id=uid).first_or_404()
        attention.delete()
    return DeleteSuccess()