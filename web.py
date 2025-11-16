from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.utils import get_openapi
from apis.auth import router as auth_router
from apis.user import router as user_router
from apis.article import router as article_router
from apis.mps import router as wx_router
from apis.res import router as res_router
from apis.rss import router as rss_router,feed_router
from apis.config_management import router as config_router
from apis.message_task import router as task_router
from apis.sys_info import router as sys_info_router
from apis.tags import router as tags_router
from apis.export import router as export_router
from apis.tools import router as tools_router
import apis
import os
from core.config import cfg,VERSION,API_BASE

app = FastAPI(
    title="WeRSS API",
    description="微信公众号RSS生成服务API文档",
    version="1.0.0",
    docs_url="/api/docs",  # 指定文档路径
    redoc_url="/api/redoc",  # 指定Redoc路径
    # 指定OpenAPI schema路径
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {
            "name": "认证",
            "description": "用户认证相关接口",
        }
    ],
    swagger_ui_parameters={
        "persistAuthorization": True,
        "withCredentials": True,
    }
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def add_custom_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Version"] = VERSION
    response.headers["X-Powered-By"] = "Rachel"
    response.headers["GITHUB"] = "https://github.com/rachelos/we-mp-rss"
    response.headers["Server"] = cfg.get("app_name", "WeRSS")
    return response

# —— RSS 禁缓存中间件（覆盖 /feed、/rss、.xml/.rss/.atom）——
@app.middleware("http")
async def rss_no_cache(request: Request, call_next):
    resp = await call_next(request)
    p = request.url.path

    # 仅对 RSS 路径生效，避免影响其它 API/静态资源
    if p.startswith("/feed") or p.startswith("/rss") or p.endswith((".xml", ".rss", ".atom")):
        # 明确告知为 RSS
        resp.headers["Content-Type"] = "application/rss+xml; charset=utf-8"

        # 彻底禁缓存，避免 304 / CDN 命中
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"

        # 移除可能由上游中间件加的条件缓存头（用 del，别用 pop）
        try:
            del resp.headers["ETag"]
        except KeyError:
            pass
        try:
            del resp.headers["Last-Modified"]
        except KeyError:
            pass

    return resp


# 创建API路由分组
api_router = APIRouter(prefix=f"{API_BASE}")
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(article_router)
api_router.include_router(wx_router)
api_router.include_router(config_router)
api_router.include_router(task_router)
api_router.include_router(sys_info_router)
api_router.include_router(tags_router)
api_router.include_router(export_router)
api_router.include_router(tools_router)

resource_router = APIRouter(prefix="/static")
resource_router.include_router(res_router)
feeds_router = APIRouter()
feeds_router.include_router(rss_router)
feeds_router.include_router(feed_router)
# 注册API路由分组
app.include_router(api_router)
app.include_router(resource_router)
app.include_router(feeds_router)

# 静态文件服务配置
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")
from core.res.avatar import files_dir
app.mount("/files", StaticFiles(directory=files_dir), name="files")
# app.mount("/docs", StaticFiles(directory="./data/docs"), name="docs")
@app.get("/{path:path}",tags=['默认'],include_in_schema=False)
async def serve_vue_app(request: Request, path: str):
    """处理Vue应用路由"""
    # 排除API和静态文件路由
    if path.startswith(('api', 'assets', 'static')) or path in ['favicon.ico','vite.svg','logo.svg']:
        return None
    
    # 返回Vue入口文件
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "Not Found"}, 404

@app.get("/",tags=['默认'],include_in_schema=False)
async def serve_root(request: Request):
    """处理根路由"""

    return await serve_vue_app(request, "")
