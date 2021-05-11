import json

import requests
from flask import request
from wtforms import Form
from app.config.secure import APPID, SECRET

from app.libs.error_code import ParameterException, AccessToken, MsgSecCheck


class BaseForm(Form):
    def __init__(self):
        data = request.get_json(silent=True)
        args = request.args.to_dict()
        super(BaseForm, self).__init__(data=data, **args)
        access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential' \
                           '&appid={appid}&secret={secret}'.format(appid=APPID, secret=SECRET)
        access_token_res = requests.get(access_token_url)
        if access_token_res.json().get('errcode'):
            raise AccessToken()
        msgSecCheck_url = 'https://api.weixin.qq.com/wxa/msg_sec_check?access_token={ACCESS_TOKEN}'.\
            format(ACCESS_TOKEN=access_token_res.json().get('access_token'))
        x = ''
        for key in data:
            x = x + ' ' + key + ' ' + str(data[key])
        x = json.dumps({"content": x}, ensure_ascii=False).encode("utf-8").decode("latin1")
        msgSecCheck_res = requests.post(url=msgSecCheck_url, data=x)
        if msgSecCheck_res.json().get('errcode'):
            raise MsgSecCheck()

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            # form errors
            raise ParameterException(msg=self.errors)
        return self
