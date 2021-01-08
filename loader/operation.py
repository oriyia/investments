import datetime
from pytz import timezone
from datetime import timedelta
import pandas as pd
import numpy as np
import apimoex as mx
import requests
import json


# загрузка сделок
def load_deal(client, broker_account_id, t1, t2):
    return client.operations.operations_get(_from=t1.isoformat(), to=t2.isoformat(), broker_account_id=broker_account_id)


# установка временного промежутка для загрузки сделок ('2020-02-29 00:01:00' стандарт записи)
def period(deal):
    try:
        last_data = deal.date.iloc[-1]  # получаем последнюю дату загрузки
        t = datetime.datetime.strptime(last_data, '%Y-%m-%d %H:%M:%S')  # преобразовываем дату-строку в дату-объект
        last_data = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, t.second + 1,
                                      tzinfo=timezone('Europe/Moscow'))
    except IndexError:
        last_data = datetime.datetime(2019, 10, 14, 0, 0, 0, tzinfo=timezone('Europe/Moscow'))
    return last_data, datetime.datetime.now(tz=timezone('Europe/Moscow'))


# открываем файлы, если их нет, то создаем новые
def open_files():
    try:
        file1 = pd.read_csv('deal.csv')
        file2 = pd.read_csv('portfolio.csv')
        file3 = pd.read_csv('price_portfolio.csv')
        file4 = pd.read_csv('total_cash.csv')
    except FileNotFoundError:
        file1 = pd.DataFrame(columns=['date', 'figi', 'ticker', 'operation', 'price', 'count', 'commission', 'instrumental_type', 'tax'])
        file2 = pd.DataFrame(columns=['figi', 'ticker', 'count', 'price', 'instrumental_type'])
        file3 = pd.DataFrame(dict(date='2019-10-14 00:00:00', total_price=0, invest=0, cash=0), index=[0])
        file4 = pd.DataFrame(columns=['date', 'cash', 'total_cash'])
    return file1, file2, file3, file4


# добавляем операции в таблицу deal
def add_deal(client, dict_deal, deal, usd, eur):
    # перебираем все операции по одной
    for i, n in enumerate(reversed(dict_deal.payload.operations)):
        operation = n.operation_type
        date = n.date
        if operation == 'BrokerCommission':
            continue

        if operation in ['Buy', 'Sell']:
            figi = n.figi
            if n.instrument_type == 'Bond':
                ticker = client.market.market_search_by_figi_get(figi).payload.isin
            else:
                ticker = client.market.market_search_by_figi_get(figi).payload.ticker
            price = n.trades[0].price
            if n.commission in [None]:
                commission = 0
            else:
                commission = abs(n.commission.value)
            if n.currency == 'USD':
                price = n.trades[0].price * usd
                commission = commission * usd
            elif n.currency == 'EUR':
                price = n.trades[0].price * eur
                commission = commission * eur
            count = n.trades[0].quantity
            instrument_type = n.instrument_type
            tax = 0
        elif operation in ['PayIn', 'PayOut']:
            figi = None
            ticker = None
            price = n.payment
            count = 1
            commission = 0
            instrument_type = None
            tax = 0
        elif operation in ['Dividend', 'Coupon']:
            figi = n.figi
            if n.instrument_type == 'Bond':
                ticker = client.market.market_search_by_figi_get(figi).payload.isin
            else:
                ticker = client.market.market_search_by_figi_get(figi).payload.ticker
            price = n.payment
            if n.currency == 'USD':
                price = n.payment * usd
            elif n.currency == 'EUR':
                price = n.payment * eur
            count = 1
            commission = 0
            instrument_type = n.instrument_type
            tax = 0
        elif operation in ['TaxDividend', 'PartRepayment']:
            figi = n.figi
            if n.instrument_type == 'Bond':
                ticker = client.market.market_search_by_figi_get(figi).payload.isin
            else:
                ticker = client.market.market_search_by_figi_get(figi).payload.ticker
            price = abs(n.payment)
            if n.currency == 'USD':
                price = price * usd
            elif n.currency == 'EUR':
                price = price * eur
            count = 1
            commission = 0
            instrument_type = n.instrument_type
            tax = 0
        elif operation in ['ServiceCommission']:
            figi = None
            ticker = None
            price = abs(n.payment)
            if n.currency == 'USD':
                price = price * usd
            elif n.currency == 'EUR':
                price = price * eur
            count = 1
            commission = 0
            instrument_type = n.instrument_type
            tax = 0
        else:
            figi = 'НЕ ОБРАБОТАННО'
            ticker = None
            price = 0
            count = 1
            commission = 0
            instrument_type = None
            tax = 0

        deal.loc[i] = [date,
                       figi,
                       ticker,
                       operation,
                       price,
                       count,
                       commission,
                       instrument_type,
                       tax]
    return deal.reset_index(drop=True)


# добавляем пополнения в таблицу total_cash
def add_total_cash(deal, total_cash=None):
    df = deal[(deal.operation == 'PayIn') | (deal.operation == 'PayOut')]
    total_cash_new = pd.DataFrame(columns=['date', 'cash', 'total_cash'])
    total_cash_new.date = df.date
    total_cash_new.cash = df.price
    total_cash_new.total_cash = df.price.cumsum()
    total_cash_new = total_cash_new.reset_index(drop=True)
    return total_cash_new


# обновление котировок в таблице portfolio после фиксации транзакции
def update_quotes(portfolio, tr, repeat, usd, eur):
    def download_quotes(repeat):
        if repeat == 1:
            return
        set_etf = dict(board='TQTF', market='shares')
        set_stock = dict(board='TQBR', market='shares')
        set_bond = dict(board='TQCB', market='bonds')
        coeff = 1
        d = tr.date
        date = tr.date.strftime('%Y-%m-%d')
        for i in range(portfolio.shape[0]):
            row = portfolio.loc[i]  # строка из портфеля
            with requests.Session() as session:
                if row.instrumental_type == 'Stock':
                    board = set_stock['board']
                    market = set_stock['market']
                elif row.instrumental_type == 'Etf':
                    board = set_etf['board']
                    market = set_etf['market']
                elif row.instrumental_type == 'Bond':
                    board = set_bond['board']
                    market = set_bond['market']
                else:
                    board = 'TQBR'
                    market = 'shares'
                print(row.figi, row.ticker, board, market, date, row.instrumental_type)
                new_quote = mx.get_market_history(session, security=row.ticker, start=date, end=date, market=market)
                j = 0
                while not new_quote:
                    j += 1
                    date = datetime.datetime(d.year, d.month, d.day) - timedelta(j)
                    date = date.strftime('%Y-%m-%d')
                    new_quote = mx.get_market_history(session, security=row.ticker, start=date, end=date, market=market)
                    if j == 14:
                        print('уже 14 циклов')  # если цикл больше 14 раз, то оставляем старую цену и выходим
                        new_price = portfolio.loc[portfolio.figi == tr.figi, 'price']
                        break
                if len(new_quote) > 1:
                    new_price = new_quote[0]['CLOSE'] * usd
                else:
                    r = requests.get(f'https://iss.moex.com/iss/engines/stock/markets/{market}/securities/{row.ticker}.json')
                    k = pd.DataFrame(json.loads(r.text)).loc['metadata'].values[0].keys()
                    v = pd.DataFrame(json.loads(r.text)).loc['data'][['securities']][0][0]
                    b = pd.DataFrame(v, index=k).loc['CURRENCYID'].values[0]
                    if b == 'USD':
                        new_price = new_quote[0]['CLOSE'] * usd
                    else:
                        new_quote = new_quote[0]['CLOSE']
            portfolio.loc[portfolio.figi == tr.figi, 'price'] = new_price

    # если транзакция не является покупкой, продажей и частичным погашением, то просто обновляем котировки
    if tr.operation in ['PayIn', 'PayOut', 'Dividend', 'Coupon', 'TaxDividend', 'ServiceCommission', 'НЕ ОБРАБОТАННО']:
        download_quotes(repeat)
    else:  # иначе обновим портфель по бумагам (по кол-ву, для погашения цену)
        if tr.operation == 'Buy':
            a = 1
        else:
            a = -1
        if tr.figi is portfolio.figi:  # если такой figi есть в портфеле
            if tr.operation in ['Buy', 'Sell']:  # обновляем количество бумаг
                portfolio.loc[portfolio.figi == tr.figi, 'count'] += tr['count'] * a
                # если бумага полностью продана, то удаляем ее из портфеля
                if portfolio.loc[portfolio.figi == tr.figi, 'count'] == 0:
                    portfolio.drop(index=portfolio[portfolio.figi == tr.figi].index[0], inplace=True)
            else:  # обновляем котировки и обновляем цену касаемо данной транзакции и выходим из функции
                download_quotes(repeat)
                portfolio.loc[portfolio.figi == tr.figi, 'price'] -= tr.price
                return (portfolio.price * portfolio['count']).sum()
        else:  # если такой бумаги нет, то добавляем ее в портфель
            portfolio.loc[portfolio.shape[0]] = [tr.figi, tr.ticker, tr.price, tr['count'], tr.instrumental_type]
        # после обновления бумаг, обновляем цены и выходим из функции для данной транзакции
        download_quotes(repeat)
    return (portfolio.price * portfolio['count']).sum()


# добавляем в таблицу portfolio поступившие данные
def add_price_portfolio(portfolio, deal, price_portfolio, usd, eur):
    j = price_portfolio.shape[0]  # индекс для таблицы price_portfolio
    data_comparison = (deal.loc[0].date - timedelta(1)).strftime('%Y-%m-%d')
    for i in range(deal.shape[0]):  # перебираем все транзакции из таблицы deal
        print(i)
        tr = deal.loc[i]  # наша текущая транзакция
        if tr.instrumental_type == 'Currency':
            continue
        repeat = 0
        if tr.date.strftime('%Y-%m-%d') == data_comparison:
            repeat = 1
        j += i
        if tr.operation in ['PayIn', 'PayOut']:
            cash = price_portfolio.iloc[-1].cash + tr.price
            try:
                example = portfolio.iloc[-1]
                invest = update_quotes(portfolio, tr, repeat, usd, eur)
            except IndexError:
                invest = 0

        elif tr.operation in ['Buy']:
            cash = price_portfolio.iloc[-1].cash - tr.price * tr['count'] - tr.commission
            invest = update_quotes(portfolio, tr, repeat, usd, eur)

        elif tr.operation in ['Sell']:
            cash = price_portfolio.iloc[-1].cash + tr.price * tr['count'] - tr.commission
            invest = update_quotes(portfolio, tr, repeat, usd, eur)

        elif tr.operation in ['Dividend', 'Coupon']:
            cash = price_portfolio.iloc[-1].cash + tr.price
            invest = update_quotes(portfolio, tr, repeat, usd, eur)

        elif tr.operation in ['PartRepayment']:
            cash = price_portfolio.iloc[-1].cash + tr.price
            invest = update_quotes(portfolio, tr, repeat, usd, eur)

        elif tr.operation in ['TaxDividend', 'ServiceCommission', 'НЕ ОБРАБОТАННО']:
            cash = price_portfolio.iloc[-1].cash - tr.price
            try:
                example = portfolio.iloc[-1]
                invest = update_quotes(portfolio, tr, repeat, usd, eur)
            except IndexError:
                invest = 0
        else:
            print(f'Транзакцию не удалось обработать, {i}')
            continue
        date_comparison = tr.date.strftime('%Y-%m-%d')
        price_portfolio.loc[j] = [tr.date,
                                  invest + cash,
                                  invest,
                                  cash]


# def save_file():
#     try:
#         portfel.to_csv('portfel.csv', index=False)
#         price_portfel.to_csv('price_portfel.csv', index=False)
#         cash.to_csv('cash.csv', index=False)
#     except PermissionError:
#         print(f'Ошибка! Файл используется другой программой!')


def get_operation(client, broker_account_id, usd, eur):
    deal, portfolio, price_portfolio, total_cash = open_files()
    t1, t2 = period(deal)
    dict_deal = load_deal(client, broker_account_id, t1, t2)
    deal = add_deal(client, dict_deal, deal, usd, eur)
    dd = add_total_cash(deal)
    add_price_portfolio(portfolio, deal, price_portfolio, usd, eur)
    return price_portfolio
