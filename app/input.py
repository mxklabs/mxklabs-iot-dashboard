import threading

class SensorInput(object):

    def __init__(self, input_handler):
        self.input_handler = input_handler

        self.thread = threading.Thread(target=self.run)
        self.stop_event = threading.Event()

        self.thread.start()

    def run(self):
        while not self.stop_event.isSet():
            self.input_handler.add_input(humidity=30, temperature=60)
            self.stop_event.wait(1)

    def stop(self):
        self.stop_event.set()

