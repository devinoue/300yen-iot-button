#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 300yen IoT Button
# version 0.0.1
# Author: Masaharu Inoue
# Licence: MIT Licence. 

"""Python IoT Button"""


import evdev
from evdev import InputDevice, categorize, ecodes
import datetime
from time import time, sleep
from urllib import request, error
import settings



url_iOS_push = settings.url_iOS_push
url_iOS_hold = settings.url_iOS_hold
url_Android_push=settings.url_Android_push
url_Android_hold=settings.url_Android_hold
hold_time_sec = settings.hold_time_sec



def main():
    print("Waiting for device to become ready...")
    dev_path = ""
    while(True):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if("Shutter" in device.name):
                dev_path = device.path
        if (dev_path == "") :
            sleep(1)
        else : break

    dev = InputDevice(dev_path)
    print("IoT Button is ready.")
    old = 0
    iOS_flag=0
    is_android = 0
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == 28:  # when android button pushed
                    is_android=1

            # key upが始まったら
            if event.value == 0:
                if iOS_flag==1 : 
                    iOS_flag=0
                    continue
                
                # 長押し終わり
                if old != 0 and time() - old > hold_time_sec:
                    if is_android :
                        ConnectServer(url_Android_hold,"Android hold")
                        is_android=0
                        iOS_flag=1
                    else:
                        ConnectServer(url_iOS_hold,"iOS hold")

                    old = 0
                    continue
                if is_android:
                    ConnectServer(url_Android_push,"Android push")
                    is_android=0
                    iOS_flag=1
                else:
                    ConnectServer(url_iOS_push,"iOS push")

            # 長押しスタート
            if event.value == 2 and old == 0:
                old = time()


def ConnectServer(url,style):
    req = request.Request(url)
    try:
        with request.urlopen(req) as res:
            print("Success : {} {}".format(style,res.read(100).decode('utf-8')))
    except error.HTTPError as err:
        print(err.code)
    except error.URLError as err:
        print(err.reason)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
print("\n")
