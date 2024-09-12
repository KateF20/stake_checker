import requests

from settings.settings import TOKEN_ID


def get_token_price(token_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data[TOKEN_ID]['usd']
    else:
        return f"Error: {response.status_code}"


price_data = get_token_price(TOKEN_ID)
