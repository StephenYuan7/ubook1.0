from flask import Blueprint

from app.api.v2 import client, interest, message, activity, \
    schoolbook, product, attention, focus, transaction, chatting


def create_blueprint_v2():
    bp_v2 = Blueprint('v2', __name__)
    client.api.register(bp_v2)
    interest.api.register(bp_v2)
    message.api.register(bp_v2)
    activity.api.register(bp_v2)
    schoolbook.api.register(bp_v2)
    product.api.register(bp_v2)
    attention.api.register(bp_v2)
    focus.api.register(bp_v2)
    transaction.api.register(bp_v2)
    chatting.api.register(bp_v2)
    return bp_v2
