"""
Описание всего модуля. Автоматически будет записано в атрибут doc
"""
from loader.portfolio import *

settings_file = 'settings.yml'
client = connection(settings_file)
accounts_id = client.user.user_accounts_get().payload.accounts
bk_account_id = accounts_id[0].broker_account_id
uuc_account_id = accounts_id[1].broker_account_id


def get_all(clients, broker_account_id):
    return free_money(clients, broker_account_id), load_portfolio(clients, broker_account_id)


usd, eur = exchange_rates(client)
cash, portfolio = get_all(client, uuc_account_id)
money = create_table_money(usd, eur, cash)
table_portfolio = create_table_portfolio(client, portfolio, usd, eur)
print(table_portfolio)
