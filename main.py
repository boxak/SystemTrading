from api.Kiwoom import *
import sys

app = QApplication(sys.argv)
kiwoom = Kiwoom()
kiwoom.get_account_number()

kospi_code_list = kiwoom.get_code_list_by_market("0")
print(kospi_code_list)

app.exec_()

