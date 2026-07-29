from resources.BancoCentral import BancoCentral
from use_cases.Xlsx import Xlsx
from use_cases.Outlook import Outlook

if __name__ == '__main__':
    bancocentral = BancoCentral()
    xlsx = Xlsx(file_path="C:\\teste.xlsx")
    outlook = Outlook()

    coins = bancocentral.get_all_coins()
    last_conversao = ''
    line = 1
    for coin in coins:
        print(coin["name"])
        conversao = bancocentral.select_coin_by_inner_html(last_result=last_conversao, coin_html=coin["name"])
        last_conversao = conversao
        print(f'CONVERSAO: {conversao}')
        xlsx.set_cell_value(sheet_name='TESTE', cell_reference=f'A{line}', value=conversao, create=True)
        line += 1
    outlook.send_email(recipients=["email@outlook.com"], subject="TESTE AUTOMAÇÃO", body="", attachments=["C:\\teste.xlsx"])
