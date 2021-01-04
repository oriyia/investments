"""
Описание всего модуля. Автоматически будет записано в атрибут doc
"""
from loader.portfolio import get_api_token
import os

tk_uuc = get_api_token('ps_uuc')
print(tk_uuc)