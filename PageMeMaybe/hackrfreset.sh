#!/bin/sh
hackrf=`lsusb|grep "1d50:6089"|awk '{print "/dev/bus/usb/" $2 "/" $4}'|sed -e 's/://'`
/home/krwightm/PageMe/usbreset $hackrf
