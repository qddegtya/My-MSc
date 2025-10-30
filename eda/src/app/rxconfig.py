import reflex as rx

config = rx.Config(
    app_name="eda",  # 修正：app_name 必须匹配目录名 src/app/
    frontend_port=8700,  # 前端端口（用户访问）
    backend_port=3000,   # 后端 API 端口
    disable_plugins=[
        "reflex.plugins.sitemap.SitemapPlugin"
    ],
    show_built_with_reflex=False,
)