from werkzeug.exceptions import HTTPException

from app.libs.error import APIException


class Success(APIException):
    code = 201
    msg = 'ok'
    error_code = 0


class DeleteSuccess(Success):
    code = 202
    error_code = 1


class PutSuccess(Success):
    code = 203
    error_code = 2


class ServerError(APIException):
    code = 500
    msg = 'sorry, we made a mistake (*￣︶￣)!'
    error_code = 999


class ClientTypeError(APIException):
    # 400 401 403 404
    # 500
    # 200 201 204
    # 301 302
    code = 400
    msg = 'client is invalid'
    error_code = 1006


class ParameterException(APIException):
    code = 400
    msg = 'invalid parameter'
    error_code = 1000


class NotFound(APIException):
    code = 404
    msg = 'the resource are not found O__O...'
    error_code = 1001


class AuthFailed(APIException):
    code = 401
    error_code = 1005
    msg = 'authorization failed'


class Forbidden(APIException):
    code = 403
    error_code = 1004
    msg = 'forbidden, not in scope'


class DuplicateGift(APIException):
    code = 400
    error_code = 2001
    msg = 'the current book has already in gift'


class UserExist(APIException):
    code = 406
    error_code = 2002
    msg = 'the current user has already in database '


class InterestExist(APIException):
    code = 406
    error_code = 2002
    msg = 'the current interest has already in database '


class SizeOverflow(APIException):
    code = 407
    error_code = 2003
    msg = 'the size has already overflow '


class AttentionExist(APIException):
    code = 408
    error_code = 2004
    msg = 'the current attention has already in database '


class FocusExist(APIException):
    code = 409
    error_code = 2005
    msg = 'the current focus has already in database '


class FormatErrors(APIException):
    code = 500
    error_code = 2006
    msg = 'the format is invalid '


class ProductOver(APIException):
    code = 410
    error_code = 2006
    msg = 'You have too many products'


class AccessToken(APIException):
    code = 411
    error_code = 40001
    msg = 'AccessToken fail to get'


class MsgSecCheck(APIException):
    code = 412
    error_code = 87014
    msg = 'content lawbreaking'
