#coding:utf8

from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    """自定义的接受正则表达式的路由转化器"""
    def __init__(self,url_map,regex):
        """在路由中填写正则表达式"""
        super(RegexConverter,self).__init__(url_map)
        self.regex=regex