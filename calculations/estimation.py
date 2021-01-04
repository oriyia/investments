import pandas as pd

# rules
rub_ref = 10  # доля рублей
usd_ref = 80  # доля доллара
eur_ref = 10

stock_ref = 70  # доля акций
bond_ref = 20  # доля облигаций
gold_ref = 10  # доля золота

stock_dev_ref = 50  # доля акций развитых стран
stock_undev_ref = 50  # доля акций развивающихся стран

stock_usa_ref = 70  # доля акций америки
stock_eur_ref = 30  # доля акций европы

stock_rus_ref = 20  # доля акций россии
stock_ch_ref = 40
stock_all_ref = 40

bond_dev_ref = 80  # доля облигаций развитых стран
bond_undev_ref = 20  # доля облигаций развивающихся стран

bond_usa_ref = 50
bond_eur_ref = 50

bond_rus_ref = 30
bond_ch_ref = 40
bond_all_ref = 30


def statistic(frame, cash, usd, eur):
    money_invest = frame.value_all.sum()
    count_invest = frame.shape[0]
    money_all = cash['total'] + money_invest
    print(f"Наличные всего: {round(cash['total'], 2)} руб.")
    print(f'Рубли: {cash["rub"]} руб. ({round(cash["rub"] / cash["total"] * 100, 1)}%), '
          f'Доллары: {cash["usd"]} дол. ({round(cash["usd"] * usd, 2)} руб. {round(cash["usd"] * usd / cash["total"] * 100, 1)}%), '
          f'Евро: {cash["eur"]}({round(cash["eur"] * eur, 2)} руб. {round(cash["eur"] * eur / cash["total"] * 100, 1)}%)')
    print(f'Инвестированно: {round(money_invest, 2)} руб., (всего пунктов - {count_invest})')
    print(f'Всего на счете: {round(money_all, 2)} руб.')

    print('\n    ЗАИНВЕСТИРОВАННО')
    rub_inv = frame[frame.currency_real == 'RUB']['value_all'].sum()
    composition_rub = list(frame[frame.currency_real == 'RUB'].ticker)
    usd_inv = frame[frame.currency_real == 'USD']['value_all'].sum()
    composition_usd = list(frame[frame.currency_real == 'USD'].ticker)
    eur_inv = frame[frame.currency_real == 'EUR']['value_all'].sum()
    composition_eur = list(frame[frame.currency_real == 'EUR'].ticker)
    rub_pr = int(rub_inv / money_invest * 100)
    usd_pr = int(usd_inv / money_invest * 100)
    eur_pr = int(eur_inv / money_invest * 100)
    rub_deviation = rub_pr - rub_ref
    usd_deviation = usd_pr - usd_ref
    eur_deviation = eur_pr - eur_ref
    print(f'Рублей: {round(rub_inv, 2)}  {rub_pr}% ({rub_deviation}%)')
    print(f'    {composition_rub}')
    print(f'Долларов: {round(usd_inv, 2)}  {usd_pr}% ({usd_deviation}%)')
    print(f'    {composition_usd}')
    print(f'Евро: {round(eur_inv, 2)}  {eur_pr}% ({eur_deviation}%)')
    print(f'    {composition_eur}')

    print('\n    СООТНОШЕНИЕ ТИПОВ БУМАГ')
    stock = round(frame[frame.composition == 'Stock']['value_all'].sum(), 2)
    composition_stock = list(frame[frame.composition == 'Stock'].ticker)
    bond = round(frame[frame.composition == 'Bond']['value_all'].sum(), 2)
    composition_bond = list(frame[frame.composition == 'Bond'].ticker)
    gold = round(frame[frame.composition == 'Gold']['value_all'].sum(), 2)
    composition_gold = list(frame[frame.composition == 'Gold'].ticker)
    stock_pr = int(stock / money_invest * 100)
    bond_pr = int(bond / money_invest * 100)
    gold_pr = int(gold / money_invest * 100)
    print(f'Акции: {stock}  {stock_pr}% ({stock_pr - stock_ref}%)   {composition_stock}')
    print(f'Облигации: {bond}  {bond_pr}% ({bond_pr - bond_ref}%)   {composition_bond}')
    print(f'Золото: {gold}  {gold_pr}% ({gold_pr - gold_ref}%)    {composition_gold}')

    print('\n    АКЦИИ Соотношение развитых и развивающихся стран')
    stock_dev = round(frame[(frame.developed == 'yes') & (frame.composition == 'Stock')]['value_all'].sum(), 2)
    stock_undev = round(frame[(frame.developed == 'no') & (frame.composition == 'Stock')]['value_all'].sum(), 2)
    stock_dev_pr = int(stock_dev / stock * 100)
    stock_undev_pr = int(stock_undev / stock * 100)
    print(f'Развитые: {stock_dev}  {stock_dev_pr}% ({stock_dev_pr - stock_dev_ref}%)')
    print(f'Неразвитые: {stock_undev}  {stock_undev_pr}% ({stock_undev_pr - stock_undev_ref}%)')

    def dev():
        print('\n____ АКЦИИ Доли в развитых рынках ____')
        stock_usa = round(frame[(frame['region'] == 'Америка') & (frame['developed'] == 'yes') & (frame['composition'] == 'Stock')][
                              'value_all'].sum(), 2)
        stock_eua = round(frame[(frame['region'] == 'Европа') & (frame['developed'] == 'yes') & (frame['composition'] == 'Stock')][
                              'value_all'].sum(), 2)

        stock_usa_pr = round(stock_usa / stock_dev * 100, 2)
        stock_eua_pr = round(stock_eua / stock_dev * 100, 2)
        print(f'Америка: {stock_usa}  {stock_usa_pr}% ({stock_usa_pr - stock_usa_ref}%)')
        print(f'Европа: {stock_eua}  {stock_eua_pr}% ({stock_eua_pr - stock_eur_ref}%)')

    dev()

    def undev():
        print('\n____ АКЦИИ Доли в неразвитых рынках ____')
        stock_rus = round(frame[(frame['region'] == 'Россия') & (frame['developed'] == 'no') & (frame['composition'] == 'Stock')][
                              'value_all'].sum(), 2)
        stock_ch = round(frame[(frame['region'] == 'Китай') & (frame['developed'] == 'no') & (frame['composition'] == 'Stock')][
                             'value_all'].sum(), 2)
        stock_all = round(
            frame[(frame['region'] == 'Развив-ся') & (frame['developed'] == 'no') & (frame['composition'] == 'Stock')][
                'value_all'].sum(), 2)

        stock_rus_pr = round(stock_rus / stock_undev * 100, 2)
        stock_ch_pr = round(stock_ch / stock_undev * 100, 2)
        stock_all_pr = round(stock_all / stock_undev * 100, 2)
        print(f'Россия: {stock_rus}  {stock_rus_pr}% ({stock_rus_pr - stock_rus_ref}%)')
        print(f'Китай: {stock_ch}  {stock_ch_pr}% ({stock_ch_pr - stock_ch_ref}%)')
        print(f'Мир: {stock_all}  {stock_all_pr}% ({stock_all_pr - stock_all_ref}%)')

    undev()

    def bond_dev_undev():
        print('\n____ ОБЛИГАЦИИ Соотношение развитых и развивающихся стран ____')
        global bond_dev
        global bond_undev
        bond_dev = round(frame[(frame['developed'] == 'yes') & (frame['composition'] == 'Bond')]['value_all'].sum(), 2)
        bond_undev = round(frame[(frame['developed'] == 'no') & (frame['composition'] == 'Bond')]['value_all'].sum(), 2)
        bond_dev_pr = int(bond_dev / bond * 100)
        bond_undev_pr = int(bond_undev / bond * 100)
        print(f'Развитые: {bond_dev}  {bond_dev_pr}% ({bond_dev_pr - bond_dev_ref}%)')
        print(f'Неразвитые: {bond_undev}  {bond_undev_pr}% ({bond_undev_pr - bond_undev_ref}%)')

    if bond != 0:
        bond_dev_undev()

    def bond_dev_otn():
        print('\n____ ОБЛИГАЦИИ Доли в развитых рынках ____')
        bond_usa = round(frame[(frame['region'] == 'Америка') & (frame['developed'] == 'yes') & (frame['composition'] == 'Bond')][
                             'value_all'].sum(), 2)
        bond_eua = round(frame[(frame['region'] == 'Европа') & (frame['developed'] == 'yes') & (frame['composition'] == 'Bond')][
                             'value_all'].sum(), 2)

        bond_usa_pr = round(bond_usa / bond_dev * 100, 2)
        bond_eua_pr = round(bond_eua / bond_dev * 100, 2)
        print(f'Америка: {bond_usa}  {bond_usa_pr}% ({bond_usa_pr - bond_usa_ref}%)')
        print(f'Европа: {bond_eua}  {bond_eua_pr}% ({bond_eua_pr - bond_eur_ref}%)')

    if bond != 0:
        bond_dev_otn()

    def bond_undev_otn():
        print('\n____ ОБЛИГАЦИИ Доли в неразвитых рынках ____')
        bond_rus = round(frame[(frame['region'] == 'Россия') & (frame['developed'] == 'no') & (frame['composition'] == 'Stock')][
                             'value_all'].sum(), 2)
        bond_ch = round(frame[(frame['region'] == 'Китай') & (frame['developed'] == 'no') & (frame['composition'] == 'Stock')][
                            'value_all'].sum(), 2)
        bond_all = round(frame[(frame['region'] == 'Развив-ся') & (frame['developed'] == 'no') & (frame['composition'] == 'Stock')][
                             'value_all'].sum(), 2)

        bond_rus_pr = round(bond_rus / bond_undev * 100, 2)
        bond_ch_pr = round(bond_ch / bond_undev * 100, 2)
        bond_all_pr = round(bond_all / bond_undev * 100, 2)
        print(f'Россия: {bond_rus}  {bond_rus_pr}% ({bond_rus_pr - bond_rus_ref}%)')
        print(f'Китай: {bond_ch}  {bond_ch_pr}% ({bond_ch_pr - bond_ch_ref}%)')
        print(f'Мир: {bond_all}  {bond_all_pr}% ({bond_all_pr - bond_all_ref}%)')

    if bond != 0:
        bond_undev_otn()



