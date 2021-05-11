import os
import random
import string

from flask import g, current_app, jsonify, request
from sqlalchemy import or_, desc

from app.libs.error_code import Success, DeleteSuccess, SizeOverflow, NotFound, FormatErrors, ProductOver
from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.attention import Attention
from app.models.base import db
from app.models.product import Product
from app.models.school import School
from app.models.user import User
from app.validators.forms import ProductUpForm, ProductDeleteForm, PageForm, ProductSearchForm, ProductChangeStateForm, \
    ProductRenewForm, ProductChangeCurrentPriceForm, ProductGet, ProductImageDeleteForm
from app.validators.image import image_check

api = Redprint('product')


@api.route('/add', methods=['POST'])
@auth.login_required
def up_product():
    form = ProductUpForm().validate_for_api()
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first()
    products = user.user_relate_product
    length = 0
    for product in products:
        if product.status == 1:
            length += 1
    if length > 20:
        return ProductOver()
    product_id = Product.up_by_mina(form.title.data,
                                    form.currentPrice.data,
                                    form.originalPrice.data,
                                    form.description.data,
                                    form.address.data,
                                    form.kind.data,
                                    form.degree.data,
                                    form.state.data,
                                    uid)
    return product_id


@api.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_product():
    form = ProductDeleteForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        product = Product.query.filter_by(id=form.product_id.data, user_id=uid).first_or_404()
        product.delete()
    return DeleteSuccess()


@api.route('/self', methods=['POST'])
@auth.login_required
def my_up():
    form = PageForm().validate_for_api()
    page = current_app.config['PAGE']
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first()
    products = user.user_relate_product
    if form.page.date == 1:
        products = products[-15:]
    else:
        products = products[-form.page.data * page:page - form.page.data * page]
    for product in products:
        if product.status == 0:
            products.remove(product)
    products.reverse()
    json_products = jsonify(products)
    i = 0
    for product in products:
        len = 0
        for attention in product.product_relate_attention:
            if attention.status == 1:
                len += 1
        json_products.json[i]['attention'] = len
        i += 1
    return jsonify(json_products.json)


@api.route('/change/state', methods=['POST'])
@auth.login_required
def change_state():
    form = ProductChangeStateForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        product = Product.query.filter_by(id=form.product_id.data, user_id=uid).first_or_404()
        product.state = form.state.data
    r = 'now state of product ' + str(product.id) + '  is  ' + product.state
    return jsonify(r)


@api.route('/change/currentprice', methods=['POST'])
@auth.login_required
def change_current_price():
    form = ProductChangeCurrentPriceForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        product = Product.query.filter_by(id=form.product_id.data, user_id=uid).first_or_404()
        product.currentPrice = form.currentPrice.data
    r = 'now currentPrice of product ' + str(product.id) + '  is  ' + str(product.currentPrice)
    return jsonify(r)


@api.route('/search', methods=['POST'])
@auth.login_required
def search_product():
    form = ProductSearchForm().validate_for_api()
    uid = g.user.uid
    q = '%' + form.key.data + '%'
    school = School.query.filter_by(id=form.school_id.data).first_or_404()
    school_users = school.school_relate_user
    school_users_id = []
    for school_user in school_users:
        school_users_id.append(school_user.id)
    if form.kind.data == 0:
        product_filter = Product.query.filter(Product.status == 1, Product.state == '1',
                                              Product.user_id.in_(school_users_id),
                                              or_(Product.title.like(q), Product.description.like(q))
                                              )
        if form.method.data == 0:
            products = product_filter.order_by(desc(Product.currentPrice)).all()
        elif form.method.data == 1:
            products = product_filter.order_by(Product.currentPrice).all()
        elif form.method.data == 2:
            products = product_filter.order_by(desc(Product.create_time)).all()
        elif form.method.data == 3:
            products = product_filter.order_by(Product.create_time).all()
    else:
        product_filter = Product.query.filter(Product.status == 1, Product.state == '1',
                                              Product.kind == form.kind.data, Product.user_id.in_(school_users_id),
                                              or_(Product.title.like(q), Product.description.like(q))
                                              )
        if form.method.data == 0:
            products = product_filter.order_by(desc(Product.currentPrice)).all()
        elif form.method.data == 1:
            products = product_filter.order_by(Product.currentPrice).all()
        elif form.method.data == 2:
            products = product_filter.order_by(desc(Product.create_time)).all()
        elif form.method.data == 3:
            products = product_filter.order_by(Product.create_time).all()
    page = current_app.config['PAGE']
    products = products[form.page.data * page - page:form.page.data * page]
    json_products = jsonify(products)
    users = []
    if products:
        for product in products:
            users.append(product.product_relate_user)
    if users:
        i = 0
        for product in json_products.json:
            product['profile'] = (users[i]['profile'])
            product['nickname'] = (users[i]['nickname'])
            product['credibility'] = (users[i]['credibility'])
            product['school_id'] = (users[i]['school_id'])
            product['user_academy'] = (users[i]['user_academy'])
            product['school_name'] = (users[i].user_relate_school['name'])
            product['qq'] = (users[i]['qq'])
            if Attention.query.filter_by(user_id=uid, product_id=product['id']).first():
                product['attention'] = 1
            else:
                product['attention'] = 0
            if uid == product['user_id']:
                product['isMine'] = 1
            else:
                product['isMine'] = 0
            i += 1

    return jsonify(json_products.json)


@api.route('/upimage/<product_id>/<image_id>', methods=['POST'])
@auth.login_required
def up_image(product_id, image_id):
    uid = g.user.uid
    product_id = int(product_id)
    image_id = int(image_id)
    if image_id > 3 or image_id < 1:
        return NotFound()
    product = Product.query.filter_by(id=product_id, user_id=uid).first_or_404()
    cl = request.content_length
    if cl is not None and cl > 3 * 1024 * 1024:
        return SizeOverflow()
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    # 获取图片文件 name = upload
    img = request.files.get('upload')
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
    imgName = ran_str + '_user' + str(uid) + "_product" + str(product_id) + "_" + str(image_id) + "." + my_format
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
        if image_id == 1:
            if product.image1:
                os.remove(path + product.image1)
            product.image1 = url
        if image_id == 2:
            if product.image2:
                os.remove(path + product.image2)
            product.image2 = url
        if image_id == 3:
            if product.image3:
                os.remove(path + product.image3)
            product.image3 = url
        db.session.add(product)
    return url


@api.route('/renew', methods=['POST'])
@auth.login_required
def renew_product():
    form = ProductRenewForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        product = Product.query.filter_by(id=form.product_id.data, user_id=uid).first_or_404()
        product.title = form.title.data
        product.currentPrice = form.currentPrice.data
        product.originalPrice = form.originalPrice.data
        product.description = form.description.data
        product.address = form.address.data
        product.kind = form.kind.data
        product.degree = form.degree.data
        product.state = form.state.data
    return Success()


@api.route('/get', methods=['POST'])
@auth.login_required
def get_product():
    form = ProductGet().validate_for_api()
    product = Product.query.filter_by(id=form.product_id.data).first_or_404()
    user = product.product_relate_user
    product = jsonify(product)
    product.json['nickname'] = user.nickname
    product.json['profile'] = user.profile
    product.json['credibility'] = user.credibility
    product.json['user_academy'] = user['school_id']
    product.json['school_id'] = (user['school_id'])
    product.json['school_name'] = (user.user_relate_school['name'])
    product.json['qq'] = user.qq
    if Attention.query.filter_by(user_id=g.user.uid, product_id=form.product_id.data).first():
        product.json['attention'] = 1
    else:
        product.json['attention'] = 0
    uid = g.user.uid
    if uid == product.json['user_id']:
        product.json['isMine'] = 1
    else:
        product.json['isMine'] = 0
    return jsonify(product.json)


@api.route('/image', methods=['DELETE'])
@auth.login_required
def delete_image():
    form = ProductImageDeleteForm().validate_for_api()
    uid = g.user.uid
    with db.auto_commit():
        product = Product.query.filter_by(id=form.product_id.data, user_id=uid).first_or_404()
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        path = basedir + "/static/image/"
        if form.image.data == 1:
            if product.image1:
                os.remove(path + product.image1)
                product.image1 = None
        elif form.image.data == 2:
            if product.image2:
                os.remove(path + product.image2)
                product.image2 = None
        else:
            if product.image3:
                os.remove(path + product.image3)
                product.image3 = None
    return DeleteSuccess()
