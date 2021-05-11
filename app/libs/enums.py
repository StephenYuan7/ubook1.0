'''
定义枚举类型
'''

from enum import Enum


# 定义用户的各种类型
class ClientTypeEnum(Enum):
    USER_EMAIL = 100
    USER_MOBILE = 101

    # 微信小程序
    USER_MINA = 200
    # 微信公众号
    USER_WX = 201


class Booktype(Enum):
    STUDY = 100
    DAILY = 200
    ELECTRONIC = 300
    BEAUTY = 400
    CLOTH = 500
    OTHERS = 600


class Gender(Enum):
    MAN = 1
    WOMAN = 2


class Campus(Enum):
    BUPT_BENBU = 100
    BUPT_SHAHE = 200
    BUPT_OUT = 300


class BookLocation(Enum):
    BENBU = 100
    SHAHE = 200
    OUT = 300


class SearchMethod(Enum):
    TIME = 100
    CONDITION = 200
    PRICE = 300
    TYPE = 400


class Academy(Enum):
    SICE = 100
    SEE = 200
    SCS = 300
    SA = 400
    SDMDA = 500
    MPS = 600
    SCSS = 700
    PI = 800
    SCI = 900
    SEM = 1000
    PA = 1100
    SH = 1200
    IS = 1300
    SSE = 1400
