from driver.wxarticle import Web
from driver.success import Success
from driver.wx import WX_API
from core.print import print_error,print_info,print_success
from jobs.fetch_no_article import fetch_articles_without_content
import base64
import re


def testWeb():
    urls="""
    """.strip().split("\n")

    Web.FixArticle(mp_id="MP_WXS_3009671561",urls=urls)
    pass
 
def testWx_Api():
      # 测试代码
    def login_success_callback(session_data, account_info):
        print("登录成功！")
        print(f"Token: {session_data.get('token')}")
        print(f"账号信息: {account_info}")
    
    def notice_callback(message):
        print(f"通知: {message}")
    
    from driver.wx_api import get_qr_code,login_with_token
    # 保持程序运行以等待登录
    # 使用token登录
    login_with_token(login_success_callback)
    # 获取二维码
    result = get_qr_code(login_success_callback, notice_callback)
    # print(f"二维码结果: {result}")


def testMarkDown():
    from core.models import Article
    from core.db import DB
    session=DB.get_session()
    art=session.query(Article).filter(Article.content != None).order_by(Article.id.desc()).first()
    # print(art.content)
    from core.content_format import  format_content
    content= format_content(art.content,"markdown")
    return content

def testMd2Doc():
    from tools.mdtools.export import export_md_to_doc
    doc_id="3918391364-2247502779_3,3076560530-2673097250_1,3076560530-2673097167_1,3076560530-2673097166_1".split(",")
    export_md_to_doc(mp_id="MP_WXS_3918391364",doc_id=doc_id,export_md=True, zip_file=False,remove_images=False,remove_links=False)



def testToken():
    from driver.auth import auth
    auth()
    # input("按任意键退出")

def testLogin():
    from driver.wx import WX_API
    from driver.success import Success
    de_url=WX_API.GetCode(Success)
    print(de_url)
    # input("按任意键退出")
def testNotice():
    from jobs.notice import sys_notice
    text="""
    消息测试<font color="warning">132例</font>，请相关同事注意。
> 类型:<font color="comment">用户反馈</font>
> 普通用户反馈:<font color="comment">117例</font>
> VIP用户反馈:<font color="comment">15例</font>
"""
    sys_notice(text,"测试通知","测试通知","测试通知")


if __name__=="__main__":
    # testLogin()
    # testWeb()
    # testNotice()
    testWx_Api()
    # testMd2Doc()
    # testToken()
    # testMarkDown()