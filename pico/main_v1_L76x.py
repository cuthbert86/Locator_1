# This code does work with my L76x GNSS gps module but not very well, I'm getting wildly innacuate locations.
# It is possible that my gps module isn't very good and it may need to be outside to get a good signal. 
# -*- coding:utf-8 -*-
from micropython import const
from lib.DFRobot_GNSS_I2C import DFRobot_GNSS_I2C, MODE_GPS
from time import sleep, localtime
import network
import usocket
import socket
import network
import machine
from machine import Pin, I2C, 
import micropython
import ustruct as struct


import time
from pico import l76x
import math
import hashlib
from pico.micropyGPS.micropyGPS import MicropyGPS
from MyHelperCode import connect_to_wifi, WifiServer, timestamp, write_to_csv
# define the UART number and its baudrate , when UARTx is 1 please solder the UART1 0R resistor on Pico-GPS-L76B board
# UARTx = 1
Self_Name = "Cuthbert"
SSID = ''  # wifi username
PASSWORD = '' # wifi password
ssidRouter     = ''    #Enter the router name
passwordRouter = '' #Enter the router password
ssidAP         = 'Pico W'      #Enter the AP name
passwordAP     = '12345678'    #Enter the AP password
local_IP       = '192.168.4.150'
gateway        = '192.168.4.1'
subnet         = '255.255.255.0'
dns            = '8.8.8.8'
adcpin = 4
sensor = machine.ADC(adcpin)
sock = usocket

ip = connect_to_wifi()

UARTx = 0

# define the rp2040 uart baudrate , the default baudrate is 9600 of L76B 
BAUDRATE = 9600

# make an object of gnss device , the default uart is UART0 and its baudrate is 9600bps
gnss_l76b=l76x.L76X(uartx=UARTx,_baudrate = BAUDRATE)

# exit the backup mode when start
gnss_l76b.l76x_exit_backup_mode()

# enable/disable sync PPS when NMEA output
'''
optional:
SET_SYNC_PPS_NMEA_ON
SET_SYNC_PPS_NMEA_OFF
'''
gnss_l76b.l76x_send_command(gnss_l76b.SET_SYNC_PPS_NMEA_ON)


# make an object of NMEA0183 sentence parser
"""
Setup GPS Object Status Flags, Internal Data Registers, etc
local_offset (int): Timzone Difference to UTC
location_formatting (str): Style For Presenting Longitude/Latitude:
                           Decimal Degree Minute (ddm) - 40° 26.767′ N
                           Degrees Minutes Seconds (dms) - 40° 26′ 46″ N
                           Decimal Degrees (dd) - 40.446° N
"""
parser = MicropyGPS(location_formatting='dd')

sentence = ''

while True:
    if gnss_l76b.uart_any():
        sentence = parser.update(chr(gnss_l76b.uart_receive_byte()[0]))
        if sentence:
            
            print('WGS84 Coordinate:Latitude(%c),Longitude(%c) %.9f,%.9f'%(parser.latitude[1],parser.longitude[1],parser.latitude[0],parser.longitude[0]))
            print('copy WGS84 coordinates and paste it on Google map web https://www.google.com/maps')

            gnss_l76b.wgs84_to_bd09(parser.longitude[0],parser.latitude[0])
            print('Baidu Coordinate: longitude(%c),latitudes(%c) %.9f,%.9f'%(parser.longitude[1],parser.latitude[1],gnss_l76b.Lon_Baidu,gnss_l76b.Lat_Baidu))
            print('copy Baidu Coordinate and paste it on the baidu map web https://api.map.baidu.com/lbsapi/getpoint/index.html')
            
            print('UTC Timestamp:%d:%d:%d'%(parser.timestamp[0],parser.timestamp[1],parser.timestamp[2]))
            
#           print fix status
            '''
            1 : NO FIX
            2 : FIX 2D
            3 : FIX_3D
            '''
            print('Fix Status:', parser.fix_stat)
            
            print('Altitude:%d m'%(parser.altitude))
            print('Height Above Geoid:', parser.geoid_height)
            print('Horizontal Dilution of Precision:', parser.hdop)
            print('Satellites in Use by Receiver:', parser.satellites_in_use)
            print('')
            write_to_csv('WGS84 Coordinate:Latitude(%c),Longitude(%c) %.9f,%.9f'%(parser.latitude[1],parser.longitude[1],parser.latitude[0],parser.longitude[0]))
            sleep(20)
