import collections
import datetime
import math
import os
import threading

import mxklabs.data

HOUR_VIEW = 'hour'
DAY_VIEW = 'day'
WEEK_VIEW = 'week'
MONTH_VIEW = 'month'
YEAR_VIEW = 'year'

TIMESTAMP_FMT = "%Y/%m/%d %H:%M:%S"

HUMIDITY_MIN_FILENAME = os.path.join('..', 'data', 'humidity.minutes')
TEMPERATURE_MIN_FILENAME = os.path.join('..', 'data', 'temperature.minutes')

def minute_aggr(dt):
    return dt.replace(second=0, microsecond=0)

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
            self._handler(self._timestamp, aggregated_data)

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

    def records(self):
        result = []
        record_bytes_list = super(SimpleBuffer, self).records()
        for record_bytes in record_bytes_list:
            timestamp_str = record_bytes[:19].decode('utf-8')
            #print(timestamp_str)
            timestamp = datetime.datetime.strptime(timestamp_str, TIMESTAMP_FMT)
            #print(timestamp)
            data_str = record_bytes[20:25].decode('utf-8')
            #print(data_str)
            data = float(data_str)
            #print(data)
            result.append((timestamp, data))
        return result

class Core(object):

    def __init__(self):
        self._gui = None
        self._mode = HOUR_VIEW

        self._thread = threading.Thread(target=self._run)
        self._stop_event = threading.Event()

        self._thread.start()

        self._buf_hum_min = SimpleBuffer(data_fmt="{:.02f}",
                                         filename=HUMIDITY_MIN_FILENAME,
                                         max_number_of_records=5000,
                                         record_size=26)

        def aggr_hum_min_add_input(timestamp, data):
            self._buf_hum_min.add_input(timestamp, data)
            self._update()

        self._aggr_hum_min = Aggregator(aggr_fun=minute_aggr,
                                        handler=aggr_hum_min_add_input)

        self._buf_temp_min = SimpleBuffer(data_fmt="{:.02f}",
                                         filename=TEMPERATURE_MIN_FILENAME,
                                         max_number_of_records=5000,
                                         record_size=26)

        def aggr_temp_min_add_input(timestamp, data):
            self._buf_temp_min.add_input(timestamp, data)
            self._update()

        self._aggr_temp_min = Aggregator(aggr_fun=minute_aggr,
                                         handler=aggr_temp_min_add_input)

        self._update()

    def add_input(self, humidity, temperature):
        #print("humidity={}, temperature={}".format(humidity, temperature))
        timestamp = datetime.datetime.utcnow()

        self._aggr_hum_min.add_input(timestamp, humidity)
        self._aggr_temp_min.add_input(timestamp, temperature)

    def stop(self):
        self._stop_event.set()

    def set_mode(self, mode):
        self._mode = mode
        self._update()

    def set_gui(self, gui):
        self._gui = gui
        self._update()

    def _run(self):
        while not self._stop_event.isSet():
            #??
            self._stop_event.wait(1)

    def _add_timeouts(self, records, timeout):
        result = []
        last_timestamp = None
        for timestamp, data in records:
            if last_timestamp != None and (timestamp - last_timestamp) > timeout:
                result.append((timestamp + timeout / 2, None))
            result.append((timestamp, data))
            last_timestamp = timestamp
        return result

    def _update(self):
        if self._gui:
            now = datetime.datetime.utcnow()

            if self._mode == HOUR_VIEW:
                start = now.replace(minute=0, second=0, microsecond=0)
                end = start + datetime.timedelta(hours=1)
                title = start.strftime("%d/%m/%y %H:00") + " - " + \
                        end.strftime("%H:00")
                timeout = datetime.timedelta(minutes=1)
                x_ticks = [start + datetime.timedelta(minutes=m) for m in range(0,65,5)]
                x_ticklabels = [dt.strftime("%H:%M") for dt in x_ticks]

            humidity_records = self._buf_hum_min.records()
            humidity_records = [r for r in humidity_records if r[0] >= start and r[0] < end]
            humidity_records = self._add_timeouts(humidity_records, timeout)

            temperature_records = self._buf_temp_min.records()
            temperature_records = [r for r in temperature_records if r[0] >= start and r[0] < end]
            temperature_records = self._add_timeouts(temperature_records, timeout)

            self._gui.update_plot(**{
                'now' : now,
                'x_humidity' : [r[0] for r in humidity_records],
                'y_humidity' : [r[1] for r in humidity_records],
                'x_temperature' : [r[0] for r in temperature_records],
                'y_temperature' : [r[1] for r in temperature_records],
                'title' : title,
                'x_lim' : (start, end),
                'x_ticks' : x_ticks,
                'x_ticklabels': x_ticklabels
            })


