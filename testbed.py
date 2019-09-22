#!/usr/bin/python3
""" testbed for temperature, humidity, pressure and gas sensors """

# MIT License
#
# Copyright (c) 2019 Dave Wilson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import time

from si7021 import Si7021

import Adafruit_DHT

import bme680

import board
import busio
import adafruit_mpl115a2

# Import Adafruit IO REST client.
from Adafruit_IO import Client, RequestError, Feed

# Import the device driver stuff
from smbus import SMBus

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = 'xxxxx'

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'xxxxx'

# Create an instance of the REST client.
AIO = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Access or create the data feeds to adafruit.io
try:
    TEMPERATURE_SI7021_FEED = AIO.feeds("testsi7021temperature")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testsi7021temperature")
    TEMPERATURE_SI7021_FEED = AIO.create_feed(FEED)

try:
    HUMIDITY_SI7021_FEED = AIO.feeds("testsi7021humidity")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testsi7021humidity")
    HUMIDITY_SI7021_FEED = AIO.create_feed(FEED)

try:
    TEMPERATURE_DHT22_FEED = AIO.feeds("testdht22temperature")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testdht22temperature")
    TEMPERATURE_DHT22_FEED = AIO.create_feed(FEED)

try:
    HUMIDITY_DHT22_FEED = AIO.feeds("testdht22humidity")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testdht22humidity")
    HUMIDITY_DHT22_FEED = AIO.create_feed(FEED)

try:
    TEMPERATURE_MPL115A2_FEED = AIO.feeds("testmpl115a2temperature")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testmpl115a2temperature")
    TEMPERATURE_MPL115A2_FEED = AIO.create_feed(FEED)

try:
    PRESSURE_MPL115A2_FEED = AIO.feeds("testmpl115a2pressure")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testmpl115a2pressure")
    PRESSURE_MPL115A2_FEED = AIO.create_feed(FEED)

try:
    TEMPERATURE_BME680_FEED = AIO.feeds("testbme680temperature")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testbme680temperature")
    TEMPERATURE_BME680_FEED = AIO.create_feed(FEED)

try:
    PRESSURE_BME680_FEED = AIO.feeds("testbme680pressure")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testbme680pressure")
    PRESSURE_BME680_FEED = AIO.create_feed(FEED)

try:
    HUMIDITY_BME680_FEED = AIO.feeds("testbme680humidity")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testbme680humidity")
    HUMIDITY_BME680_FEED = AIO.create_feed(FEED)

try:
    GAS_BME680_FEED = AIO.feeds("testbme680gas")
except RequestError: # Doesn't exist, create a new feed
    FEED = Feed(name="testbme680gas")
    GAS_BME680_FEED = AIO.create_feed(FEED)

# Access the Si7021 sensor
SI7021_SENSOR = Si7021(SMBus(1))

# Access the DHT22 device driver using pin 4
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

# Access the MPL115A2 device driver using I2C bus
I2C = busio.I2C(board.SCL, board.SDA)
MPL_SENSOR = adafruit_mpl115a2.MPL115A2(I2C)

# Access and setup the BME680 sensor
try:
    BME680_SENSOR = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    BME680_SENSOR = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

BME680_SENSOR.set_humidity_oversample(bme680.OS_2X)
BME680_SENSOR.set_pressure_oversample(bme680.OS_4X)
BME680_SENSOR.set_temperature_oversample(bme680.OS_8X)
BME680_SENSOR.set_filter(bme680.FILTER_SIZE_3)
BME680_SENSOR.set_gas_status(bme680.ENABLE_GAS_MEAS)
BME680_SENSOR.set_gas_heater_temperature(320)
BME680_SENSOR.set_gas_heater_duration(150)
BME680_SENSOR.select_gas_heater_profile(0)

def celsius_to_fahrenheit(celsius):
    """ convert celsius to fahrenheit """
    fahrenheit = (celsius * (9.0/5.0)) + 32.0
    return fahrenheit

def pressure_to_kpa(pressure):
    """ convert 1000 Pa to kpi """
    kpa = pressure / 10.0
    return kpa

# send temperature and humidity to adafruit.io
while True:

    # collect and post data once per minute
    time.sleep(45.0)

    # SI7021 sensor data
    HUMIDITY, CELSIUS = SI7021_SENSOR.read()
    VALUE = celsius_to_fahrenheit(CELSIUS)
    AIO.send_data(TEMPERATURE_SI7021_FEED.key, VALUE)
    AIO.send_data(HUMIDITY_SI7021_FEED.key, HUMIDITY)

    time.sleep(5.0) # delay between posts
    # DHT22 sensor data
    HUMIDITY, CELSIUS = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if HUMIDITY is not None and CELSIUS is not None:
        VALUE = celsius_to_fahrenheit(CELSIUS)
        AIO.send_data(TEMPERATURE_DHT22_FEED.key, VALUE)
        AIO.send_data(HUMIDITY_DHT22_FEED.key, HUMIDITY)

    time.sleep(5.0) # delay between posts
    # MPL115A2 sensor data
    CELSIUS = MPL_SENSOR.temperature
    VALUE = celsius_to_fahrenheit(CELSIUS)
    AIO.send_data(TEMPERATURE_MPL115A2_FEED.key, VALUE)
    PRESSURE = MPL_SENSOR.pressure
    VALUE = pressure_to_kpa(PRESSURE)
    AIO.send_data(PRESSURE_MPL115A2_FEED.key, VALUE)

    time.sleep(5.0) # delay between posts
    # BME680 sensor data
    if BME680_SENSOR.get_sensor_data():
        CELSIUS = BME680_SENSOR.data.temperature
        VALUE = celsius_to_fahrenheit(CELSIUS)
        AIO.send_data(TEMPERATURE_BME680_FEED.key, VALUE)
        PRESSURE = BME680_SENSOR.data.pressure
        VALUE = pressure_to_kpa(PRESSURE)
        AIO.send_data(PRESSURE_BME680_FEED.key, VALUE)
        HUMIDITY = BME680_SENSOR.data.humidity
        AIO.send_data(HUMIDITY_BME680_FEED.key, HUMIDITY)
        if BME680_SENSOR.data.heat_stable:
            GAS = BME680_SENSOR.data.gas_resistance
            AIO.send_data(GAS_BME680_FEED.key, GAS)
