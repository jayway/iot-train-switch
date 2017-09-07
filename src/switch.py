#!/usr/bin/python
#
# Copyright 2017 Tomas Nilsson
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the standard MIT license.  See COPYING for more details.

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import Adafruit_PCA9685
import os
import json
import time
import argparse


class shadowCallbackContainer:
	def __init__(self, deviceShadowInstance, servoChannel, servoFreq, servoMin, servoMax):
		self.deviceShadowInstance = deviceShadowInstance
    self.servoChannel = servoChannel
    self.servoMin = servoMin
    self.servoMax = servoMax
    self.pwm = Adafruit_PCA9685.PCA9685()
    self.pwm.set_pwm_freq(servoFreq)

	def delta_callback(self, payload, responseStatus, token):
    payloadDict = json.loads(payload)
		use_sidetrack = payloadDict["state"]["use_sidetrack"]
		servo_pos = self.servo_min if use_sidetrack else self.servo_max
    pwm.set_pwm(self.servo_channel, 0, servo_pos)
    deltaMessage = json.dumps(payloadDict["state"])
		newPayload = '{"state":{"reported":' + deltaMessage + '}}'
		self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)


def main(endpoint, rootCAPath, certPath, keyPath, thingName, useWebsocket, servoChannel, servoFreq, servoMin, servoMax):
  
  # Configure IoT client
  shadow = AWSIoTMQTTShadowClient(thingName)
  shadow.configureEndpoint(endpoint, 8883)
  shadow.configureCredentials(rootCAPath, keyPath, certPath)

  # Connect
  shadow.connect()

  # Create shadow
  shadow = shadow.createShadowHandlerWithName(thingName, True)
  callbackHandler = shadowCallbackContainer(shadow, servoChannel, servoFreq, servoMin, servoMax)

  # Register callback
  shadow.shadowRegisterDeltaCallback(callbackHandler.delta_callback)
  
  #Loop until we get AWS IoT events
  while True:
    time.sleep(1)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--endpoint", action="store", required=True, dest="endpoint", help="Your AWS IoT custom endpoint")
  parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
  parser.add_argument("-c", "--cert", action="store", required=True, dest="certPath", help="Certificate file path")
  parser.add_argument("-k", "--key", action="store", required=True, dest="keyPath", help="Private key file path")
  parser.add_argument("-n", "--thingName", action="store", required=True, dest="thingName", help="Targeted thing name")
  parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False, help="Use MQTT over WebSocket")
  parser.add_argument("-s", "--servoChannel", action="store", required=True, dest="servoChannel", help="The i2c channel the servo is connected to")
  parser.add_argument("-f", "--servoFrequency", action="store", dest="servoFreq", default=50, help="The servo frequency")
  parser.add_argument("-m", "--servoMin", action="store", dest="servoMin", default=230, help="The servo min value")
  parser.add_argument("-x", "--servoMax", action="store", dest="servoMax", default=310, help="The servo max value")
  args = parser.parse_args()
  
  main(args.endpoint, args.rootCAPath, args.certPath, args.keyPath, args.thingName, args.useWebsocket, args.servoChannel, args.servoFreq, args.servoMin, args.servoMax)