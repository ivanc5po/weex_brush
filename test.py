import undetected_chromedriver as uc
import websocket
import json
import time

coin = "gas"
rate = 0.0025

options = uc.ChromeOptions()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--use-gl=desktop")
driver = uc.Chrome(options=options)

driver.get(f"https://www.weex.com/zh-TW/futures/{coin.upper()}-USDT")
input("login? : ")
time.sleep(5)
driver.find_element("xpath", "/html/body/div[5]/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div/div/div[2]/div[1]/div[2]/div/div[2]").click()
time.sleep(0.1)
driver.find_element("xpath", "/html/body/div[5]/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div/div/div[2]/div[1]/div[8]/div/div/div[5]/div").click()
time.sleep(0.1)


mode = 0
def on_message(ws, message):
    global mode
    global driver
    global weex_p
    try:
        data = json.loads(message)
        # For the bookTicker stream on Binance Futures:
        # "b" is best bid price, "B" is best bid quantity,
        # "a" is best ask price, "A" is best ask quantity.
        bid_price = data.get("b")
        ask_price = data.get("a")
        if bid_price and ask_price:
            bn_p = (float(bid_price)+float(ask_price))/2
            weex_p = float(driver.title.split()[0])
            
            if mode == 0 and bn_p > weex_p*(1+rate):
                driver.find_element("xpath", "/html/body/div[5]/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div/div/div[2]/div[1]/div[12]/div/div[1]/div").click()
                print("buy", weex_p)
                mode = 1
                
            elif mode == 0 and bn_p < weex_p*(1-rate):
                driver.find_element("xpath", "/html/body/div[5]/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div/div/div[2]/div[1]/div[12]/div/div[2]/div").click()
                print("sell", weex_p)
                mode = 2

            elif mode == 1 and bn_p < weex_p:
                driver.find_element("xpath", "//*[text()='闪电平仓']").click()
                print(f"sell {weex_p}\n------------------------------")
                driver.find_element("xpath", "/html/body/div[5]/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div/div/div[2]/div[1]/div[8]/div/div/div[5]/div").click()
                mode = 0
                
            elif mode == 2 and bn_p > weex_p:
                driver.find_element("xpath", "//*[text()='闪电平仓']").click()
                print(f"buy {weex_p}\n-------------------------------")
                driver.find_element("xpath", "/html/body/div[5]/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div/div/div[2]/div[1]/div[8]/div/div/div[5]/div").click()
                mode = 0
                
            # print(f"Bid: {bid_price}, Ask: {ask_price}")
        else:
            # In case the message format is different
            print("Received message:", data)
    except Exception as e:
        print("Error processing message:", e)

# Callback: when an error occurs
def on_error(ws, error):
    print("Error:", error)

# Callback: when the connection is closed
def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed", close_status_code, close_msg)

# Callback: when connection is opened
def on_open(ws):
    print("WebSocket connection opened")

# This function runs the websocket and automatically reconnects on disconnect
def run_websocket():
    # Binance Futures base URL for websockets
    # The "bookTicker" stream returns real-time best bid/ask for one symbol.
    # Here we subscribe to "btcusdt@bookTicker".
    ws_url = f"wss://fstream.binance.com/ws/{coin.lower()}usdt@bookTicker"
    
    # Loop forever: if the connection closes, wait a few seconds and reconnect.
    while True:
        print("Connecting to:", ws_url)
        ws = websocket.WebSocketApp(ws_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        # The run_forever() call will block.
        # ping_interval and ping_timeout help keep the connection alive.
        ws.run_forever(ping_interval=60, ping_timeout=10)
        
        print("Connection lost. Reconnecting in 5 seconds...")
        time.sleep(5)
            
if __name__ == "__main__":
    run_websocket()
