##Code Maarten Wachters ##
##Samenwerking Tim de Nooier
##Button receiver , state sender
import RPi.GPIO as IO
import time
from datetime import datetime as dt
import paho.mqtt.client as mqtt

#Set pinmode to BCM
IO.setmode(IO.BCM)
#Leds
IO.setup(21, IO.OUT)
IO.setup(20, IO.OUT)
#Afstandsensor
    #TRIG is 23
    #ECHO is 24
IO.setup(23, IO.OUT)
IO.setup(24, IO.IN)
#Buttons
    #Button 1 : Alarm status (aan/uit)
IO.setup(22, IO.IN, pull_up_down=IO.PUD_UP)
    #Button 2 : Alarm afzetten als het afgaat
IO.setup(27, IO.IN, pull_up_down=IO.PUD_UP)
    #Button 3 : Distance measuren
IO.setup(17, IO.IN, pull_up_down=IO.PUD_UP)
#Button event detecten
IO.add_event_detect(22, IO.FALLING, bouncetime=200)
IO.add_event_detect(27, IO.FALLING, bouncetime=200)
IO.add_event_detect(17, IO.FALLING, bouncetime=200)

def on_message(mqttc, obj, msg):
    global alarmstate, alarmring
    #Alarm state aan : led aanzetten
    if msg.payload.decode() == 'alarmAan':
        io.output(21,1)
        alarmstate = True
        print('Alarm staat aan')
    #Alarm state uit : led uitzetten
    elif msg.payload.decode() == 'alarmUit':
        io.output(21,0)
        alarmstate = False
        print('Alarm staat uit')

    #Blink alarm als getriggerd wordt
    if msg.payload.decode() == 'alarmTrig':
        alarmring = True
        try:
            print('Alarm is triggered')
            file = open("alarmlog.txt", 'a')
        except IOError:
            print("Unable to create")
            file.close()
        finally:
            file.write(time.strftime("%d-%m-%y %H-%M-%S")+'\n')
            file.close()
            time.sleep(0.2)

    #Zet led uit als gestopt wordt
    elif msg.payload.decode() == 'alarmStop':
        alarmring = False
        print('Alarm is gestopt')
print(msg.topic)
print(msg.payload.decode())

def led():
    #Blink alarm led wanneer triggered
    if alarmring == True:
        io.output(20,1)
        time.sleep(0.2)
        io.output(20,0)
        time.sleep(0.2)
    elif alarmring == False:
        io.output(20, 0)

#Log message in console
#print(msg.topic)
#print(msg.payload.decode())


def main():
    try:
        mqttc = mqtt.Client()
        mqttc.on_message = on_message
        mqttc.connect("broker.hivemq.com")
        mqttc.subscribe("home/alarm/system/#")

        while True:
            #Start shit
            led()
            #Start Alarm button
            if io.event_detected(22):
                if alarmstate == False:
                    mqttc.publish('home/alarm/system', payload='alarmAan', qos=0, retain=False)
                    print('Alarm aan zetten')
                elif alarmstate == True:
                    mqttc.publish('home/alarm/system', payload='alarmUit', qos=0, retain=False)
                    print('Alarm uit zetten')
            #Stop Alarm trigger button
            if io.event_detected(27):
                mqttc.publish('home/alarm/system', payload='alarmStop', qos=0, retain=False)
            #Ask Distance button
            if io.event_detected(17):
                mqttc.publish('home/alarm/system', payload='askDistance', qos=0, retain=False)

    except KeyboardInterrupt:
        print('Interrupted')
        pass

    finally:
        IO.cleanup()
if __name__ == "__main__":
    main()
