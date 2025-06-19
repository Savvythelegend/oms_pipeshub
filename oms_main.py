# OMS Test - Mehfooj June 2025
# oms_main.py - rough demo
import time
from oms_core import OrderManagement
from models import OrderRequest, OrderType

oms = OrderManagement()
oms.send = lambda o: print("sending:", o.order_id)
oms.sendLogon = lambda: print("logon")
oms.sendLogout = lambda: print("logout")

now = time.time()
oms.onData(OrderRequest("ORD001", OrderType.NEW, 101.5, 5, now))
time.sleep(0.4)
oms.onData(OrderRequest("ORD001", OrderType.MODIFY, 103.0, 8, time.time()))
time.sleep(0.3)
oms.onData(OrderRequest("ORD001", OrderType.CANCEL, 0, 0, time.time()))
time.sleep(0.5)
oms.shutdown()
