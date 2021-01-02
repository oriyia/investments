"""
Описание всего модуля. Автоматически будет записано в атрибут doc
"""
from calculations.mathem import custom_sum
import yaml

import os

print(os.getenv('pswrd'))


def yaml_loader(file):
    with open(file, 'r') as f:
        data = yaml.load(f, Loader=yaml.BaseLoader)
    return data


if __name__ == '__main__':
    result = custom_sum(3, 1)
    print(result)
    a = yaml_loader('C:/Users/Ilya/settings/config')
    print(a['api_tkn']['tkn_ucc'])
