from dataclasses import dataclass
from environs import Env

@dataclass
class Payment:
    provider_token: str
    pro_plan_price: int
    payment_currency: str


@dataclass
class Config:
    bot_token: str
    currency_api_key: str
    currencies: list[str]
    database: str
    payment: Payment


env = Env()
env.read_env()

config = Config(
    bot_token=env('BOT_TOKEN'),
    currency_api_key=env('API_KEY'),
    currencies=env('CURRENCIES').split(','),
    database=env('DATABASE'),
    payment=Payment(
        provider_token=env('PROVIDER_TOKEN'),
        pro_plan_price=int(env('PRO_PLAN_PRICE')),
        payment_currency=env('PAYMENT_CURRENCY')
    )
)