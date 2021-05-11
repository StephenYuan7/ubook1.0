
import os

import requests

from app.config.secure import APPID, SECRET
from app.libs.error_code import AccessToken, MsgSecCheck


def image_check(image_path):
    """

    :param image_path:
    """
    image = os.open(image_path, os.O_RDWR)
    access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential' \
                       '&appid={appid}&secret={secret}'.format(appid=APPID, secret=SECRET)
    access_token_res = requests.get(access_token_url)
    if access_token_res.json().get('errcode'):
        raise AccessToken()
    msgImgCheck_url = 'https://api.weixin.qq.com/wxa/img_sec_check?access_token={ACCESS_TOKEN}'. \
        format(ACCESS_TOKEN=access_token_res.json().get('access_token'))
    r = {"media": image}
    msgImgCheck_res = requests.post(url=msgImgCheck_url, files=r)
    os.close(image)
    if msgImgCheck_res.json().get('errcode'):
        if os.path.exists(image_path):
            os.remove(image_path)
        raise MsgSecCheck()
    return image
