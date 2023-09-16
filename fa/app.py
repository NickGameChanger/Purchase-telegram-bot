import config
import fastapi_plugins
from fastapi import FastAPI

from fa.routes import api_router
# from starlette.middleware.sessions import SessionMiddleware


class RedisSettings(fastapi_plugins.RedisSettings):
    redis_url = config.REDIS_SESSIONS_DSN


app = FastAPI(title='Frontend API')

# !temp
# app.add_middleware(SessionMiddleware, secret_key='should_remove_it_or_change')

# Docs (disable for non-dev environment)


# Redis
@app.on_event('startup')
async def on_startup() -> None:
    await fastapi_plugins.redis_plugin.init_app(app, config=RedisSettings())
    await fastapi_plugins.redis_plugin.init()


@app.on_event('shutdown')
async def on_shutdown() -> None:
    await fastapi_plugins.redis_plugin.terminate()


# API
app.include_router(api_router, prefix='/api')



# # Webhooks
# app.include_router(webhooks_router, prefix='/webhook')

# Dev router
# if config.ENVIRONMENT == 'dev':
#     app.include_router(dev_router, prefix='/dev')

# app.add_exception_handler(
#     telegram.SuccessfulLoginRedirectException, telegram.redirect_without_login_params
# )

# app.add_exception_handler(
#     exceptions.LoginRedirectException, exceptions.redirect_to_login_page
# )

# app.add_exception_handler(
#     exceptions.ClearUtilityParamsException, exceptions.redirect_with_cleared_params
# )


# Middlewares
# app.add_middleware(SentryAsgiMiddleware)
# app.add_middleware(PrometheusMiddleware,
#                    app_name='frontend_api',
#                    prefix='fa',
#                    group_paths=True,
#                    buckets=[0.1, 0.25, 0.5, 0.75, 1],
#                    always_use_int_status=False)

# app.add_route('/api/metrics', handle_metrics)

# Temporarily disabled as grafana is not up yet and it pushes lots of errors to sentry
# app.add_middleware(MonitoringMiddleware)
