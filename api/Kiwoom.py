import time

from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import pandas as pd

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._make_kiwoom_instance()
        self._set_signal_slots()
        self._comm_connect()

        self.account_number = self.get_account_number()

        self.tr_event_loop = QEventLoop()

    def _make_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._login_slot)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)

    def _on_receive_tr_data(self, screen_no, rqname,
                            trcode, record_name, next,
                            unused1, unused2, unused3, unused4):
        print("[Kiwoom] _on_receive_tr_data is called {} /"
              " {} / {}".format(screen_no, rqname, trcode))
        tr_data_cnt = self.dynamicCall("GetRepeatCnt(QString, QString)",
                                       trcode, rqname)

        self.has_next_tr_data = next=='2'

        if rqname == "opt10081_req":
            ohlcv = {'date':[],
                     'open':[],
                     'high':[],
                     'low':[],
                     'close':[],
                     'volume':[]}

            for i in range(tr_data_cnt):
                date = self.dynamicCall("GetCommData(QString,QString,int,QString)",
                                        trcode,rqname,i,"일자")
                open = self.dynamicCall("GetCommData(QString,QString,int,QString)",
                                        trcode, rqname, i, "시가")
                high = self.dynamicCall("GetCommData(QString,QString,int,QString)",
                                        trcode, rqname, i, "고가")
                low = self.dynamicCall("GetCommData(QString,QString,int,QString)",
                                        trcode, rqname, i, "저가")
                close = self.dynamicCall("GetCommData(QString,QString,int,QString)",
                                        trcode, rqname, i, "현재가")
                volume = self.dynamicCall("GetCommData(QString,QString,int,QString)",
                                        trcode, rqname, i, "거래량")

                ohlcv['date'].append(date.strip())
                ohlcv['open'].append(int(open))
                ohlcv['high'].append(int(high))
                ohlcv['low'].append(int(low))
                ohlcv['close'].append(int(close))
                ohlcv['volume'].append(int(volume))

            self.tr_data = ohlcv

        elif rqname == "opw00001_req":
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                       trcode, rqname, 0, "주문가능금액")
            self.tr_data = int(deposit)
            print(self.tr_data)

        self.tr_event_loop.exit()
        time.sleep(0.5)

    def _login_slot(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("not connected")

        self.login_event_loop.exit()

    def _comm_connect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()

        self.login_event_loop.exec_()

    def get_account_number(self, tag="ACCNO"):
        account_list = self.dynamicCall("GetLoginInfo(QString",
                                        tag)
        account_number = account_list.split(';')[0]
        print(account_number)

        return account_number

    def get_code_list_by_market(self, market_type):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)",
                                     market_type)
        code_list = code_list.split(';')[:-1]

        return code_list

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)",
                                     code)

        return code_name

    def get_price_data(self, code):
        self.dynamicCall("SetInputValue(QString, QString)",
                         "종목코드", code)
        print("종목코드 Done")
        self.dynamicCall("SetInputValue(QString, QString)",
                         "수정주가구분", "1")
        print("수정주가구분 Done")
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "opt10081_req", "opt10081", 0, "0001")
        print("데이터 Done")
        self.tr_event_loop.exec_()

        ohlcv = self.tr_data

        while self.has_next_tr_data:
            self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
            self.dynamicCall("CommRqData(QString, QString, int, QString)",
                             "opt10081_req","opt10081",2,"0001")
            self.tr_event_loop.exec_()

            for key, val in self.tr_data.items():
                ohlcv[key][-1:] = val

            df = pd.DataFrame(ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                              index=ohlcv['date'])

            return df[::-1]

    def get_deposit(self):
        self.dynamicCall("SetInputValue(QString, QString)",
                         "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)",
                         "비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(QString, QString)",
                         "조회구분","2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "opw00001_req","opw00001",0,"0002")
        self.tr_event_loop.exec_()
        return self.tr_data