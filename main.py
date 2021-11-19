from api.Kiwoom import *
import sys

app = QApplication(sys.argv)
kiwoom = Kiwoom()

# df = kiwoom.get_price_data("005930")
# print(df)

order_result = kiwoom.send_order('send_buy_order','1001',
                                 1,'007700',1,37600,'00')

print("order_result : ")
print(order_result)



app.exec_()

