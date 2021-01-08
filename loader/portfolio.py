import os
from openapi_client import openapi
import yaml
import pandas as pd
import numpy as np
from information.etf import df_etf


# получение настроек
def get_settings(file):
    with open(file, 'r') as settings:
        return yaml.load(settings, Loader=yaml.BaseLoader)


# получение api_token из окружения
def get_api_token(key):
    return os.getenv(key)


# соединение
def connection(file_settings):
    settings = get_settings(file_settings)
    key = settings['environment variables']['tnkff']
    api_token = get_api_token(key)
    return openapi.api_client(api_token)


# получение курса валют
def exchange_rates(client):
    usd_info = client.market.market_orderbook_get('BBG0013HGFT4', 1)
    eur_info = client.market.market_orderbook_get('BBG0013HJJ31', 1)
    try:
        usd = usd_info.payload.asks[0].price
        eur = eur_info.payload.asks[0].price
    except IndexError:
        usd = usd_info.payload.close_price
        eur = eur_info.payload.close_price
    return usd, eur


# загрузка кэша
def free_money(client, broker_account_id, usd, eur):
    cash_info = client.portfolio.portfolio_currencies_get(broker_account_id=broker_account_id)
    cash_rub = cash_info.payload.currencies[0].balance
    cash_usd = cash_info.payload.currencies[1].balance
    cash_eur = cash_info.payload.currencies[2].balance
    cash_total = round(cash_rub + cash_usd * usd + cash_eur * eur, 2)
    return dict(rub=cash_rub, usd=cash_usd, eur=cash_eur, total=cash_total)


# загрузка текущего портфеля
def load_portfolio(client, broker_account_id):
    pf_uuc = client.portfolio.portfolio_get(broker_account_id=broker_account_id)
    return pf_uuc


# создание табличного портфеля
def create_table_portfolio(client, portfolio, usd, eur):
    df_portfolio = pd.DataFrame(columns=['ticker', 'value', 'value_all', 'currency', 'currency_real', 'region',
                                         'branch', 'developed', 'composition', 'balance', 'isin', 'change',
                                         'instrument_type'])
    for i, position in enumerate(portfolio.payload.positions):
        try:
            if position.instrument_type == 'Currency':
                continue
            currency = position.average_position_price.currency
            balance = position.balance
            figi = position.figi
            ticker = position.ticker
            isin = position.isin
            change = position.expected_yield.value
            instrument_type = position.instrument_type
            value_info = client.market.market_orderbook_get(figi, 1)

            try:
                value = round(value_info.payload.asks[0].price, 4)
            except IndexError:
                value = round(value_info.payload.close_price, 4)

            if currency == 'USD':
                value *= usd
            elif currency == 'EUR':
                value *= eur
            value_all = round(value * balance, 4)

            if instrument_type == 'Etf':
                series = df_etf[ticker]
                currency_real = series[2]
                region = series[0]
                developed = series[1]
                composition = series[3]
                branch = series[4]
            else:
                currency_real = currency
                region = 'Россия'
                developed = 'no'
                composition = instrument_type
                branch = None

            df_portfolio.loc[i] = [ticker,
                                   value,
                                   value_all,
                                   currency,
                                   currency_real,
                                   region,
                                   branch,
                                   developed,
                                   composition,
                                   balance,
                                   isin,
                                   change,
                                   instrument_type]
        except Exception as ex:
            print(f'Не удалось обработать {i} позицию портфеля, причина: {ex}')
            continue
    return df_portfolio


def create_table_money(usd, eur, cash):
    total = round(cash['rub'] + cash['usd'] * usd + cash['eur'] * eur, 2)
    money = pd.DataFrame(dict(total=total, rub=cash['rub'], usd=cash['usd'], eur=cash['eur'],
                              cur_usd=usd, cur_eur=eur), index=[0])
    return money
