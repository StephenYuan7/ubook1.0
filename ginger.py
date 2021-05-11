from flask import render_template
from werkzeug.exceptions import HTTPException

from app import create_app
# 实例化flask核心对象
from app.libs.error import APIException
from app.libs.error_code import ServerError

app = create_app()


@app.route('/')
def hello_world():
    return render_template("hello.html")


# 全局异常处理
@app.errorhandler(Exception)
def framework_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, HTTPException):
        code = e.code
        msg = e.description
        error_code = 1007
        return APIException(msg, code, error_code)
    else:
        # 调试模式
        # log
        if not app.config['DEBUG']:
            return ServerError()
        else:
            raise e

# 开启调试模式
if __name__ == '__main__':
    app.run(debug=True)
pass