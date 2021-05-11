import time
from datetime import datetime

from flask import g, current_app, jsonify
from sqlalchemy import or_, desc, func, not_

from app.libs.error_code import Success
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.product import Product
from app.models.transaction import Transaction
from app.models.user import User
from app.validators.forms import PageForm, TransactionAddForm, TransactionLookForm, TransactionConfirmForm, \
    TransactionEvaluateForm, CountStarForm

api = Redprint('transaction')


@api.route('/self', methods=['POST'])
@auth.login_required
def self_transaction():
    form = PageForm().validate_for_api()
    uid = g.user.uid
    transactions = Transaction.query.filter \
        (Transaction.status == 1,
         or_(Transaction.user_id == uid,
             Transaction.transaction_relate_product.has(Product.user_id == uid))) \
        .order_by(desc(Transaction.over_time)).all()
    page = current_app.config['PAGE']
    transactions = transactions[form.page.data * page - page:form.page.data * page]
    products = []
    if transactions:
        for transaction in transactions:
            products.append(transaction.transaction_relate_product)
    json_transactions = jsonify(transactions)
    i = 0
    for transaction in json_transactions.json:
        transaction['order_time'] = time.localtime(transaction['order_time'])
        transaction['order_time'] = time.strftime("%Y-%m-%d %H:%M:%S", transaction['order_time'])
        transaction['over_time'] = time.localtime(transaction['over_time'])
        transaction['over_time'] = time.strftime("%Y-%m-%d %H:%M:%S", transaction['over_time'])
        transaction['image'] = products[i]['image1']
        buyer = transactions[i].transaction_relate_user
        seller = products[i].product_relate_user
        transaction['buyer_id'] = transaction['user_id']
        transaction['buyer_nickname'] = buyer.nickname
        transaction['buyer_profile'] = buyer.profile
        transaction['seller_id'] = products[i].user_id
        transaction['seller_nickname'] = seller.nickname
        transaction['seller_profile'] = seller.profile
        transaction['product_title'] = products[i].title
        transaction.pop('user_id', '404')
        if uid == transaction['buyer_id']:
            transaction['isMine'] = 0
        else:
            transaction['isMine'] = 1
        i = i + 1
    return jsonify(json_transactions.json)


@api.route('/add', methods=['POST'])
@auth.login_required
def add_transaction():
    form = TransactionAddForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    product = Product.query.filter_by(id=form.product_id.data).first_or_404()
    t = time.strptime(form.order_time.data, "%Y-%m-%d %H:%M:%S")
    order_time = int(time.mktime(t))
    transaction_id = Transaction().up_by_mina \
        (uid, form.product_id.data, form.price.data, form.address.data, order_time)
    return transaction_id


@api.route('/look', methods=['POST'])
@auth.login_required
def look_transaction():
    form = TransactionLookForm().validate_for_api()
    uid = form.user_id.data
    transactions = Transaction.query.filter \
        (Transaction.status == 1,
         or_(Transaction.user_id == uid,
             Transaction.transaction_relate_product.has(Product.user_id == uid))) \
        .order_by(desc(Transaction.create_time)).all()
    page = current_app.config['PAGE']
    transactions = transactions[form.page.data * page - page:form.page.data * page]
    products = []
    if transactions:
        for transaction in transactions:
            products.append(transaction.transaction_relate_product)
    json_transactions = jsonify(transactions)
    i = 0
    for transaction in json_transactions.json:
        transaction['order_time'] = time.localtime(transaction['order_time'])
        transaction['order_time'] = time.strftime("%Y-%m-%d %H:%M:%S", transaction['order_time'])
        transaction['over_time'] = time.localtime(transaction['over_time'])
        transaction['over_time'] = time.strftime("%Y-%m-%d %H:%M:%S", transaction['over_time'])
        transaction['image'] = products[i]['image1']
        buyer = transactions[i].transaction_relate_user
        seller = products[i].product_relate_user
        transaction['buyer_id'] = transaction['user_id']
        transaction['buyer_nickname'] = buyer.nickname
        transaction['seller_id'] = products[i].user_id
        transaction['seller_nickname'] = seller.nickname
        transaction['product_title'] = products[i].title
        transaction.pop('user_id', '404')
    return jsonify(json_transactions.json)


@api.route('/confirm', methods=['POST'])
@auth.login_required
def confirm_transaction():
    form = TransactionConfirmForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()

    transaction = Transaction.query.filter \
        (Transaction.status == 1, Transaction.id == form.id.data
         , Transaction.state == '0',
         Transaction.transaction_relate_product.has(Product.user_id == uid)) \
        .first_or_404()
    with db.auto_commit():
        transaction.state = '1'
        transaction.transaction_relate_product.state = '2'
        transaction.over_time = int(datetime.now().timestamp())
    return Success()


@api.route('/evaluate', methods=['POST'])
@auth.login_required
def evaluate_transaction():
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    form = TransactionEvaluateForm().validate_for_api()
    transaction = Transaction.query.filter_by(id=form.id.data, user_id=uid).first_or_404()
    with db.auto_commit():
        transaction.star = form.star.data
        transaction.evaluation = form.evaluation.data
        transaction.state = '2'
    return Success()


@api.route('/look/evaluate', methods=['POST'])
@auth.login_required
def look_evaluate():
    form = TransactionLookForm().validate_for_api()
    if form.user_id.data == 0:
        uid = g.user.uid
    else:
        uid = form.user_id.data
    transactions = Transaction.query.filter \
        (Transaction.status == 1, not_(Transaction.evaluation.is_(None)),
         Transaction.transaction_relate_product.has(Product.user_id == uid)) \
        .order_by(desc(Transaction.over_time)).all()
    page = current_app.config['PAGE']
    transactions = transactions[form.page.data * page - page:form.page.data * page]
    final_transactions = []
    for transaction in transactions:
        over_time = time.localtime(transaction.over_time)
        over_time = time.strftime("%Y-%m-%d %H:%M:%S", over_time)
        user = transaction.transaction_relate_user
        temp_transaction = {'star': transaction.star, 'evaluation': transaction.evaluation,
                            'profile': user.profile, 'nickname': user.nickname,
                            'over_time': over_time}
        final_transactions.append(temp_transaction)
    return jsonify(final_transactions)


@api.route('/count/star', methods=['POST'])
@auth.login_required
def count_star():
    form = CountStarForm().validate_for_api()
    if form.user_id.data == 0:
        uid = g.user.uid
    else:
        uid = form.user_id.data
    transactions = db.session.query(Transaction.star, func.count(Transaction.star)) \
        .filter(Transaction.status == 1,
                Transaction.product_id == Product.id,
                Product.user_id == uid) \
        .group_by(Transaction.star).all()
    temp = {'badnumber': 0, 'middlenumber': 0, 'goodnumber': 0}
    for transaction in transactions:
        if transaction[0] == 3:
            temp['badnumber'] = transaction[1]
        elif transaction[0] == 2:
            temp['middlenumber'] = transaction[1]
        elif transaction[0] == 1:
            temp['goodnumber'] = transaction[1]
    return jsonify(temp)
