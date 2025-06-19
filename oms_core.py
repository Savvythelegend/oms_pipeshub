import time
import threading
from datetime import datetime
from collections import deque
from models import OrderRequest, OrderResponse, QueuedOrder, OrderType, ResponseType
import config

class OrderManagement:
    def __init__(self):
        self.queue = deque()
        self.pending = {}  # order_id -> sent_time
        self.responses = {}  # order_id -> (response_type, latency)
        
        self.cur_sec = int(time.time())
        self.sent_this_sec = 0
        self.session_active = False
        
        self.lock = threading.Lock()
        self.running = True
        
        # background thread for processing
        self.thread = threading.Thread(target=self._process)
        self.thread.daemon = True
        self.thread.start()
    
    def _is_trading_time(self):
        now = datetime.now().time()
        return config.TRADING_START <= now <= config.TRADING_END
    
    def _can_send(self):
        current_time = int(time.time())
        # Reset counter if we're in a new second
        if current_time != self.cur_sec:
            self.cur_sec = current_time
            self.sent_this_sec = 0
        
        return self.sent_this_sec < config.MAX_ORDERS_PER_SEC
    
    def _send_order(self, order):
        if not self._can_send():
            return False
        
        # track pending order
        self.pending[order.order_id] = time.time()
        
        # TODO: add real send() logic
        self.send(order)
        
        self.sent_this_sec += 1
        print("Sent:", order.order_id)
        return True
    
    def _process(self):
        while self.running:
            with self.lock:
                # handle session messages
                if self._is_trading_time() and not self.session_active:
                    self.sendLogon()
                    self.session_active = True
                    print("Session started")
                elif not self._is_trading_time() and self.session_active:
                    self.sendLogout()
                    self.session_active = False
                    print("Session ended")
                
                # process queue during trading hours
                if self.session_active and self.queue:
                    orders_to_remove = []
                    for i, order in enumerate(self.queue):
                        if self._can_send():
                            if self._send_order(order):
                                orders_to_remove.append(i)
                        else:
                            break
                    
                    # remove sent orders
                    for i in reversed(orders_to_remove):
                        del self.queue[i]
            
            time.sleep(0.01)
    
    def onData(self, request):
        """Handle incoming order requests"""
        with self.lock:
            print("Received:", request.order_type.value, request.order_id)
            
            # reject if outside trading hours
            if not self._is_trading_time():
                print("Rejected:", request.order_id)
                return
            
            if request.order_type == OrderType.NEW:
                order = QueuedOrder(request.order_id, request.price, 
                                  request.quantity, request.timestamp)
                self.queue.append(order)
                print("Queued:", request.order_id)
            
            elif request.order_type == OrderType.MODIFY:
                # find and modify existing order
                for order in self.queue:
                    if order.order_id == request.order_id:
                        order.price = request.price
                        order.quantity = request.quantity
                        order.timestamp = request.timestamp
                        print("Modified:", request.order_id)
                        return
                print("Not found for modify:", request.order_id)
            
            elif request.order_type == OrderType.CANCEL:
                # remove from queue
                for order in list(self.queue):
                    if order.order_id == request.order_id:
                        self.queue.remove(order)
                        print("Cancelled:", request.order_id)
                        return
                print("Not found for cancel:", request.order_id)
    
    def onData_response(self, response):
        """Handle exchange responses"""
        with self.lock:
            print("Response:", response.order_id, response.response_type.value)
            
            if response.order_id in self.pending:
                sent_time = self.pending[response.order_id]
                latency = response.timestamp - sent_time
                
                self.responses[response.order_id] = (response.response_type, latency)
                del self.pending[response.order_id]
                
                print("Latency:", response.order_id, f"{latency:.3f}s")
            else:
                print("Unknown order response:", response.order_id)
    
    def get_status(self, order_id):
        return self.responses.get(order_id)
    
    def shutdown(self):
        self.running = False
        self.thread.join()
    
    # mock functions - to be implemented by exchange
    def send(self, order):
        pass
    
    def sendLogon(self):
        pass
    
    def sendLogout(self):
        pass 