import winsound
import urllib.request
import json, os
from time import sleep
from time import time
import pywhatkit as kit
import datetime

API  = r'http://api.coindesk.com/v1/bpi/currentprice.json'
path = r'data.json'
referenceBit = 0


def sendZap(msg):
    phone = '+5522997815943'
    now = datetime.datetime.now()
    hour = now.hour
    min  = now.minute + 1
    kit.sendwhatmsg(phone_no=phone, message=msg, time_hour=hour, time_min=min)


def getJsonData(path):
    data = None

    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as error:
        raise Exception(f'erro: {error}')
    
    return data


def saveJsonData(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        raise Exception(f"Ocorreu um erro ao salvar o arquivo JSON: {e}")


def getBitcoin():
    value = None

    try:
        with urllib.request.urlopen(API) as url:
            response = url.read()
            data  = json.loads(response.decode('utf-8'))
            value = float(data['bpi']['USD']['rate'].replace(",", ""))
    except:
        sleep(2)
        print('erro ao obter dados do bitcoin, tentando novamente...')
        return getBitcoin()

    return value


def handleBitcoin(value):
    global referenceBit
    
    variation = (value - referenceBit)/referenceBit * 100
    print(f'valor: {value:.0f}$ | variação a partir de {referenceBit:.0f}: {variation:.2f}%')

    if variation < 1:
        return

    referenceBit = value
    saveJsonData(path, {'reference': value})

    winsound.Beep(1000, 5000)
    print('comprar!!')
    sendZap('compre!! imediatamente')
    print()


def setup():
    global startTime, referenceBit
    data = getJsonData(path)
    referenceBit = data.get('reference')

    if referenceBit == 0:
        value = getBitcoin()
        referenceBit = value
        saveJsonData(path, {'reference': value})
    


def loop():
    value = getBitcoin()
    handleBitcoin(value)
    sleep(30)
    

if __name__ == '__main__':
    setup()

    while True:
        loop()
    
