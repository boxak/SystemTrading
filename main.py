from api.Kiwoom import *
import sys

app = QApplication(sys.argv)
kiwoom = Kiwoom()

order_result = kiwoom.send_order('send_buy_order','1001',
                                 1,'007700',1,37600,'00')

print("order_result : ", order_result)
orders = kiwoom.get_order()
print("orders : ", orders)

app.exec_()

