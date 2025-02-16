import winsound
import requests
import json, os
from time import sleep
from time import time
import pywhatkit as kit
import datetime, pyautogui


def sendEvent(eventType, message, delay=0.0):
    if eventType == 'error':
        print(f'\033[31m[error]\033[0m', message)
    elif eventType == 'success':
        print(f'\033[34m[success]\033[0m', message)
    else:
        print(f'\033[32m[event]\033[0m', message)

    if delay > 0.0:
        sleep(delay)
    

def sendZap(msg, interval=2):
    phone = '+5522997815943'
    now   = datetime.datetime.now()

    hour = now.hour
    min  = now.minute + interval

    try:
        kit.sendwhatmsg(phone_no=phone, message=msg, time_hour=hour, time_min=min, tab_close=True)
        sendEvent('success', 'mensagem enviada')
    except Exception as error:
        sendEvent('error', error, delay=10)
        return sendZap(msg, interval=interval+1)
    
    sendEvent('event', 'saindo da função')


def getJson(filePath):
    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as error:
        print(error)
        return None

    
def saveJson(data, filePath):
    try:
        with open(filePath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        return True
    except Exception as error:
        print(error)
        return False


class BitcoinAlert:
    API = r'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    filePath = 'data.json'
    INTERVAL = None
    MIN_PERCENT_ALERT = None

    def __init__(self, interval=30.0, minPercent=2.0):
        self.startTime = time()
        self.lastValue = self.getSavedValue()
        self.INTERVAL  = interval
        self.MIN_PERCENT_ALERT = minPercent

    def getSavedValue(self):
        data = getJson(self.filePath)
        return data.get('value')
    
    def saveCurrentValue(self, value):
        data = {'value': value}
        return saveJson(data, self.filePath)
    
    def getCurrentValue(self):
        try:
            response = requests.get(self.API, timeout=2.0)
            data     = response.json()
            return data['bitcoin']['usd']
        except Exception as error:
            sendEvent('error', error, delay=2.0)
            return None
        
    def handle(self):
        if time() - self.startTime < self.INTERVAL:
            return

        self.startTime = time()
        bitcoin = self.getCurrentValue()

        if bitcoin is None or bitcoin < 1.0:
            return

        variation = (bitcoin - self.lastValue)/self.lastValue
        percent = round(variation*100, 2)
        sendEvent('event', f'${bitcoin:.2f} | {percent}% variation')

        if percent < self.MIN_PERCENT_ALERT:
            return
        
        self.saveCurrentValue(bitcoin)
        sendEvent('success', 'valor salvo')

        winsound.Beep(2000, duration=1000)
        sendZap(f'BITCOIN SUBIU! ${bitcoin:.2f}')


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__)) 
    os.chdir(script_dir) # AGORA EXECUTO O CÓDIGO DE QQ LUGAR

    bitcoin = BitcoinAlert(interval=30.0, minPercent=2.0)
    print('PYCOIN - API INICIADA')
    sleep(2.0)
    sendEvent('event', 'escutando API')
    print()

    while True:
        bitcoin.handle()
    
