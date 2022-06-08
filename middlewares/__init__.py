from loader import dp


from .antiflood_middleware import AntiFloodThrottlingMiddleware
from .incorrect_passward_rate_limit import ThrottlingMiddleware

dp.middleware.setup(AntiFloodThrottlingMiddleware())
dp.middleware.setup(ThrottlingMiddleware())

