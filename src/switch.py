from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import Adafruit_PCA9685
import os
import json
import logging
import time


# Set constants
virtualenv_root = os.path.dirname(__file__)
root_ca_path = os.path.abspath(os.path.join(virtualenv_root, 'certs', ''))
private_key_path = os.path.abspath(os.path.join(virtualenv_root, 'certs', ''))
cert_path = os.path.abspath(os.path.join(virtualenv_root, 'certs', ''))
iot_endpoint = ''
thing_name = ''
servo_channel = 0 
servo_freq = 50
servo_min = 230
servo_max = 310


class shadowCallbackContainer:
	def __init__(self, deviceShadowInstance):
		self.deviceShadowInstance = deviceShadowInstance

	def delta_callback(self, payload, responseStatus, token):
                
                payloadDict = json.loads(payload)
		use_sidetrack = payloadDict["state"]["use_sidetrack"]
		servo_pos = servo_min if use_sidetrack else servo_max
                pwm.set_pwm(servo_channel, 0, servo_pos)
                
                deltaMessage = json.dumps(payloadDict["state"])
		newPayload = '{"state":{"reported":' + deltaMessage + '}}'
		self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)


# Configure IoT client
shadow = AWSIoTMQTTShadowClient(thing_name)
shadow.configureEndpoint(iot_endpoint, 8883)
shadow.configureCredentials(root_ca_path, private_key_path, cert_path)
shadow.configureAutoReconnectBackoffTime(1, 32, 20)
shadow.configureConnectDisconnectTimeout(10)
shadow.configureMQTTOperationTimeout(5)

# Init servo
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(servo_freq)

# Connect
shadow.connect()

# Create shadow
shadow = shadow.createShadowHandlerWithName(thing_name, True)
callbackHandler = shadowCallbackContainer(shadow)

# Register callback
shadow.shadowRegisterDeltaCallback(callbackHandler.delta_callback)

# Loop forever
while True:
  time.sleep(1)

