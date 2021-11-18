from api.Kiwoom import *
import sys

app = QApplication(sys.argv)
kiwoom = Kiwoom()

# df = kiwoom.get_price_data("005930")
# print(df)

deposit = kiwoom.get_deposit()

app.exec_()

