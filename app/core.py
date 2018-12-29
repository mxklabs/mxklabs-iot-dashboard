import collections
import datetime
import math
import os
import threading

import mxklabs.data

THIS_HOUR = 'this-hour'
PREV_HOUR = 'prev-hour'

TIMESTAMP_FMT = "%Y/%m/%d %H:%M:%S"

HUMIDITY_MIN_FILENAME = os.path.join('..', 'data', 'humidity.minutes')

class Aggregator(object):

    def __init__(self, aggr_fun, handler):
        self._aggr_fun = aggr_fun
        self._handler = handler
        self._timestamp = None
        self._data = []

    def add_input(self, timestamp, data):
        if self._timestamp != None:
            if self._timestamp != self._aggr_fun(timestamp):
                self._aggregate_data()

        self._timestamp = self._aggr_fun(timestamp)
        self._data.append(data)

    def _aggregate_data(self):
        if self._timestamp != None:

            aggregated_data = sum([d for d in self._data]) / len(self._data)
            self._handler.add_input(self._timestamp, aggregated_data)

        self._data = []

class SimpleBuffer(mxklabs.data.FileBackedCircularBuffer):

    def __init__(self, data_fmt, **kwargs):
        super(SimpleBuffer, self).__init__(**kwargs)
        self._data_fmt = data_fmt

    def add_input(self, timestamp, data):
        timestamp_str = timestamp.strftime(TIMESTAMP_FMT)

        data_str = self._data_fmt.format(data)

        record_str = "{} {}\n".format(timestamp_str, data_str)
        record_bytes = record_str.encode('utf-8')

        self.add_record(record_bytes)

class Core(object):
    def __init__(self):

        #self._gui = gui

        self._thread = threading.Thread(target=self._run)
        self._stop_event = threading.Event()

        self._thread.start()

        minute_aggr = lambda dt: dt.replace(second=0, microsecond=0)

        self._buf_hum_min = SimpleBuffer(data_fmt="{:.02f}",
                                         filename=HUMIDITY_MIN_FILENAME,
                                         max_number_of_records=5000,
                                         record_size=26)

        self._aggr_hum_min = Aggregator(aggr_fun=minute_aggr,
                                        handler=self._buf_hum_min)




    def add_input(self, humidity, temperature):
        #print("humidity={}, temperature={}".format(humidity, temperature))
        timestamp = datetime.datetime.utcnow()

        self._aggr_hum_min.add_input(timestamp, humidity)

    def stop(self):
        self._stop_event.set()

    def set_mode(self, mode):
        pass

    def _run(self):
        while not self._stop_event.isSet():
            #??
            self._stop_event.wait(1)


