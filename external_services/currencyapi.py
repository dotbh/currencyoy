import freecurrencyapi

from config_data.config import config


client = freecurrencyapi.Client(api_key=config.currency_api_key)


async def convert_currency(base: str, to: str, amount: int) -> float:
    data = client.latest(base_currency=base, currencies=[to])['data']
    return round(float(data[to]) * amount, 2)


async def get_currency_rates(base: str, symbols: list[str]) -> dict[str, float]:
    result_data = {}

    for cur in symbols:
        if cur == base:
            continue
        try:
            result_data[cur] = await convert_currency(base=cur, to=base, amount=1)
        except KeyError:
            print(f'Не найдено пары для {cur} {base}')

    return result_data