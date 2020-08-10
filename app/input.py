import re
import serial
import serial.tools.list_ports
import threading

import Adafruit_DHT

REGEX = "^Humidity=(\d{2})\%, Temperature=(\d{2})C\r\n$"

class SensorInput(object):

    def __init__(self, input_handler):
        self.input_handler = input_handler
        self._serial = None
        self.thread = threading.Thread(target=self.run)
        self.stop_event = threading.Event()
        self.thread.start()
        self._re = re.compile(REGEX)

    def run(self):
        while not self.stop_event.isSet():

          # Set sensor type : Options are DHT11,DHT22 or AM2302
          sensor=Adafruit_DHT.DHT11
   
          # Set GPIO sensor is connected to
          gpio=17
      
          # Use read_retry method. This will retry up to 15 times to
          # get a sensor reading (waiting 2 seconds between each retry).
          humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
          
          # Reading the DHT11 is very sensitive to timings and occasionally
          # the Pi might fail to get a valid reading. So check if readings are valid.
          if humidity is not None and temperature is not None:
            humidity = int(humidity)
            temperature = int(temperature)
            print('humidity {} temperature={}', humidity, temperature)
            self.input_handler.add_input(humidity=humidity, temperature=temperature)
            
          """
          if self._serial != None:
            try:
              line = self._serial.readline()
              line = line.decode('utf-8')

              match = self._re.match(line)
              if match:
                humidity = int(match.group(1))
                temperature = int(match.group(2))
                self.input_handler.add_input(humidity=humidity, temperature=temperature)
              except Exception as e:
                print(e)
                self._serial = None
          else:
            self._try_to_open_serial()
          """

          self.stop_event.wait(0.25)

    def stop(self):
        self.stop_event.set()

    def _try_to_open_serial(self):

        ports = list(serial.tools.list_ports.grep(regexp='^/dev/ttyUSB\d$'))

        if len(ports) > 0:
            try:
                self._serial = serial.Serial(
                    port=ports[0].device, \
                    baudrate=115200, \
                    parity=serial.PARITY_NONE, \
                    stopbits=serial.STOPBITS_ONE, \
                    bytesize=serial.EIGHTBITS, \
                    timeout=0)
                print("opened port: {}".format(str(ports[0].device)))
            except:
                pass
