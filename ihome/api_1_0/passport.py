#coding:utf-8

from . import api
from flask import request,jsonify,current_app
from ihome.utils.response_code import RET
import re
from ihome import redis_store,db
from ihome.models import User




@api.route("/users",methods=["POST"])
def register():
    #用户注册

    #接受参数 手机号，短信验证码，密码，json格式的数据
    # json.loads(request.data) 转字典
    #request.get_json方法能够帮助将请求体的json数据转为字典
    req_dict=request.get_json()
    mobile=req_dict.get("mobile")
    sms_code=req_dict.get("sms_code")
    password=req_dict.get("password")


    #校验参数
    if not all([mobile,sms_code,password]):
        resp={
            "erro":RET.PARAMERR,
            "errmsg":"参数不完整"
        }
        return jsonify(resp)

        #判断手机号格式
    if not re.match(r"1[34578]\d{9}",mobile):
        resp={
            "errno":RET.DATAERR,
            "errmsg":"手机格式不正确"
        }
        return jsonify(resp)
    #处理参数（业务逻辑）
    #1 获取真实的短信验证码

    try:
        real_sms_code=redis_store.get("sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        resp={
            "errno":RET.DBERR,
            "errmsg":"查询短信验证码错误"
        }
        return jsonify(resp)

    # 判断短信验证码是否过期
    if real_sms_code is None:
        resp={
            "errno":RET.NODATA,
            "errmsg":"短信验证码过期"
        }
        return jsonify(resp)

    #判断短信验证码是否正确
    if real_sms_code!=sms_code:
        resp={
            "errno":RET.DATAERR,
            "errmsg":"短信验证码错误"
        }
        return jsonify(resp)

    #判断手机号是否已经注册
    try:
        user=User.query.filter_by(mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        resp={
            "errno":RET.DBERR,
            "errmsg":"数据库异常"
        }
        return jsonify(resp)


    user=User(name=mobile,mobile=mobile)
    user.generate_password(password)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        resp={
            "errno":RET.DATAEXIST,
            "errmsg":"用户手机号已经注册"
        }
        return jsonify(resp)


    session["user_id"]=user.id
    session["user_name"]=mobile
    session["mobile"]=mobile



    #返回数值
    resp={

    }
