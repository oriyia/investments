"""
Описание всего модуля. Автоматически будет записано в атрибут doc
"""
from loader.portfolio import *
from calculations.estimation import statistic
from loader.operation import get_operation


# settings for pandas
pd.set_option('display.max_columns', 14)
desired_width = 3000
pd.set_option('display.width', desired_width)

settings_file = 'settings.yml'
client = connection(settings_file)
accounts_id = client.user.user_accounts_get().payload.accounts
bk_account_id = accounts_id[0].broker_account_id
uuc_account_id = accounts_id[1].broker_account_id


def get_all(clients, broker_account_id):
    return free_money(clients, broker_account_id, usd, eur), load_portfolio(clients, broker_account_id)


usd, eur = exchange_rates(client)
cash, portfolio = get_all(client, uuc_account_id)
money = create_table_money(usd, eur, cash)
table_portfolio = create_table_portfolio(client, portfolio, usd, eur)
# print(table_portfolio)
# statistic(table_portfolio, cash, usd, eur)
# print(get_operation(client, uuc_account_id))
# print(get_operation(client, uuc_account_id).payload.operations[0])
deal = get_operation(client, uuc_account_id, usd, eur)
print(deal)


