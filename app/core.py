import collections
import datetime
import math
import os
import threading
import time

import mxklabs.data

HOUR_VIEW = 'hour'
DAY_VIEW = 'day'
WEEK_VIEW = 'week'
MONTH_VIEW = 'month'
YEAR_VIEW = 'year'

TIMESTAMP_FMT = "%Y/%m/%d %H:%M:%S"

TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'

SERIES = [TEMPERATURE, HUMIDITY]

MINUTE = 'min'
QUARTER_OF_HOUR = 'min15'
HOUR = 'hour'
DAY = 'day'

TIMEBASES = [MINUTE, QUARTER_OF_HOUR, HOUR, DAY]

TIMEBASE_CONFIG = \
{
    MINUTE:
    {
        'aggregation' : 'avg',
        'data_fmt': "{:.02f}",
        'max_number_of_records': 120,
        'bucket_fun': lambda dt: dt.replace(second=0, microsecond=0),
        'timeout': datetime.timedelta(minutes=2)
    },
    QUARTER_OF_HOUR:
    {
        'aggregation' : 'minmax',
        'data_fmt': "{0[0]:.02f} {0[1]:.02f}",
        'max_number_of_records': 192,
        'bucket_fun': lambda dt: dt.replace(minute=(dt.minute // 15) * 15, second=0, microsecond=0),
        'timeout': datetime.timedelta(minutes=20)
    },
    HOUR:
    {
        'aggregation' : 'minmax',
        'data_fmt': "{0[0]:.02f} {0[1]:.02f}",
        'max_number_of_records': 336,
        'bucket_fun': lambda dt: dt.replace(minute=0, second=0, microsecond=0),
        'timeout': datetime.timedelta(minutes=70)
    },
    DAY:
    {
        'aggregation' : 'minmax',
        'data_fmt': "{0[0]:.02f} {0[1]:.02f}",
        'max_number_of_records': 400,
        'bucket_fun': lambda dt: dt.replace(hour=0, second=0, microsecond=0),
        'timeout': datetime.timedelta(days=1, minutes=10)
    }
}

def make_filename(serie, timebase):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), '..',
                        'data', '{}.{}'.format(serie, timebase))

def aggregate_avg(data):
    return sum(data) / len(data)

def aggregate_minmax(data):
    if isinstance(data[0], float):
        return (min(data), max(data))
    else:
        return (min([d[0] for d in data]), max([d[0] for d in data]))


class Aggregator(object):

    def __init__(self, bucket_fun, aggregate_fun, handler):
        self._bucket_fun = bucket_fun
        self._handler = handler
        self._aggregate_fun = aggregate_fun
        self._timestamp = None
        self._data = []

    def add_input(self, timestamp, data):
        aggregated = False
        if self._timestamp != None:
            if self._timestamp != self._bucket_fun(timestamp):
                self._aggregate_data()
                aggregated = True
        self._timestamp = self._bucket_fun(timestamp)
        self._data.append(data)

        return aggregated

    def _aggregate_data(self):
        if self._timestamp != None:
            aggregated_data = self._aggregate_fun(self._data)
            self._handler(self._timestamp, aggregated_data)

        self._data = []

class AvgBuffer(mxklabs.data.FileBackedCircularBuffer):

    def __init__(self, data_fmt, **kwargs):
        super(AvgBuffer, self).__init__(record_size=26, **kwargs)
        self._data_fmt = data_fmt
        self._handler = None

    def add_input(self, timestamp, data):
        print("AvgBuffer: Adding {} {}".format(str(timestamp), str(data)))

        timestamp_str = timestamp.strftime(TIMESTAMP_FMT)
        data_str = self._data_fmt.format(data)
        record_str = "{} {}\n".format(timestamp_str, data_str)
        record_bytes = record_str.encode('utf-8')
        self.add_record(record_bytes)

        if self._handler:
            self._handler.add_input(timestamp, (data,data))

    def set_handler(self, handler):
        self._handler = handler

    def records(self):
        result = []
        record_bytes_list = super(AvgBuffer, self).records()
        for record_bytes in record_bytes_list:
            timestamp_str = record_bytes[:19].decode('utf-8')
            timestamp = datetime.datetime.strptime(timestamp_str, TIMESTAMP_FMT)
            data_str = record_bytes[20:25].decode('utf-8')
            data = float(data_str)
            result.append((timestamp, data))
        return result

class MinMaxBuffer(mxklabs.data.FileBackedCircularBuffer):

    def __init__(self, data_fmt, **kwargs):
        super(MinMaxBuffer, self).__init__(record_size=32, **kwargs)
        self._data_fmt = data_fmt
        self._handler = None

    def add_input(self, timestamp, data):

        print("MinMaxBuffer: Adding {} {}".format(str(timestamp), str(data)))

        timestamp_str = timestamp.strftime(TIMESTAMP_FMT)
        data_str = self._data_fmt.format(data)
        record_str = "{} {}\n".format(timestamp_str, data_str)
        record_bytes = record_str.encode('utf-8')
        self.add_record(record_bytes)

        if self._handler:
            self._handler.add_input(timestamp, data)

    def set_handler(self, handler):
        self._handler = handler

    def records(self):
        result = []
        record_bytes_list = super(MinMaxBuffer, self).records()
        for record_bytes in record_bytes_list:
            timestamp_str = record_bytes[:19].decode('utf-8')
            timestamp = datetime.datetime.strptime(timestamp_str, TIMESTAMP_FMT)
            data1_str = record_bytes[20:25].decode('utf-8')
            data1 = float(data1_str)
            data2_str = record_bytes[26:31].decode('utf-8')
            data2 = float(data2_str)
            result.append((timestamp, (data1,data2)))
        return result

class Core(object):

    def __init__(self):
        self._gui = None
        self._mode = HOUR_VIEW

        self._thread = threading.Thread(target=self._run)
        self._stop_event = threading.Event()

        self._thread.start()
        self._buffers = {}
        self._aggregators = {}

        for serie in SERIES:

            for timebase in TIMEBASES:
                config = TIMEBASE_CONFIG[timebase]

                BufferType = AvgBuffer if config['aggregation'] == 'avg' else MinMaxBuffer
                aggregate_fun = aggregate_avg if config['aggregation'] == 'avg' else aggregate_minmax

                # The circular buffer to store this in.
                self._buffers[serie + timebase] = BufferType(data_fmt=config['data_fmt'],
                                                             filename=make_filename(serie, timebase),
                                                             max_number_of_records=config['max_number_of_records'])

                # An aggregator making sure the right information ends up in each bucket.
                self._aggregators[serie + timebase] = Aggregator(bucket_fun=config['bucket_fun'],
                                                                 aggregate_fun=aggregate_fun,
                                                                 handler=self._buffers[serie + timebase].add_input)

            for tb1, tb2 in zip(TIMEBASES, TIMEBASES[1:]):
                # Make sure each buffer feeds down to the next aggregator.
                self._buffers[serie + tb1].set_handler(self._aggregators[serie + tb2])

        self._update()

    def add_input(self, humidity, temperature):
        #print("humidity={}, temperature={}".format(humidity, temperature))
        timestamp = datetime.datetime.utcnow()

        aggr1 = self._aggregators[HUMIDITY + MINUTE].add_input(timestamp, humidity)
        aggr2 = self._aggregators[TEMPERATURE + MINUTE].add_input(timestamp, temperature)

        if aggr1 or aggr2:
            self._update()

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
                if isinstance(data, float):
                    result.append((timestamp + timeout / 2, None))
                else:
                    result.append((timestamp + timeout / 2, (None,None)))
            result.append((timestamp, data))
            last_timestamp = timestamp
        return result

    def _update(self):
        if self._gui:
            now = datetime.datetime.utcnow()

            if self._mode == HOUR_VIEW:
                start = now - datetime.timedelta(hours=1) #.replace(minute=0, second=0, microsecond=0)
                end = now
                tick_interval_fun = lambda dt: dt + datetime.timedelta(minutes=5)
                start_tick = start.replace(minute=(start.minute // 5) * 5, second=0, microsecond=0) + datetime.timedelta(minutes=5)
                tick_fmt = "%H:%M"
                timebase = MINUTE

            if self._mode == DAY_VIEW:
                start = now - datetime.timedelta(days=1) #.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
                tick_interval_fun = lambda dt: dt + datetime.timedelta(hours=2)
                start_tick = start.replace(hour=(start.hour // 2) * 2, minute=0, second=0, microsecond=0) + datetime.timedelta(hours=2)
                tick_fmt = "%H:%M"
                timebase = QUARTER_OF_HOUR

            if self._mode == WEEK_VIEW:
                start = now - datetime.timedelta(days=7) #.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
                tick_interval_fun = lambda dt: dt + datetime.timedelta(days=1)
                start_tick = start.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                tick_fmt = "%d/%m"
                timebase = HOUR

            if self._mode == MONTH_VIEW:
                start = now - datetime.timedelta(days=30) #.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
                tick_interval_fun = lambda dt: dt + datetime.timedelta(days=3)
                start_tick = start.replace(day=((start.day - 1) // 3) * 3 + 1, hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=3)
                tick_fmt = "%d/%m"
                timebase = DAY

            if self._mode == YEAR_VIEW:
                start = now - datetime.timedelta(days=366) #.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
                def tick_interval_fun(dt):
                    dt2 = dt + datetime.timedelta(days=1)
                    while dt2.day != 1:
                        dt2 = dt2 + datetime.timedelta(days=1)
                    return dt2

                start_tick = tick_interval_fun(start.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
                tick_fmt = "%b"
                timebase = DAY

            x_ticks = [start_tick]
            while tick_interval_fun(x_ticks[-1]) < end:
                x_ticks.append(tick_interval_fun(x_ticks[-1]))
            x_ticklabels = [dt.strftime(tick_fmt) for dt in x_ticks]

            timeout = TIMEBASE_CONFIG[timebase]['timeout']

            title = start.strftime("%d/%m/%y %H:%M") + " - " + \
                    end.strftime("%d/%m/%y %H:%M")

            humidity_records = self._buffers[HUMIDITY + timebase].records()
            humidity_records = [r for r in humidity_records if r[0] >= start and r[0] < end]
            humidity_records = self._add_timeouts(humidity_records, timeout)

            temperature_records = self._buffers[TEMPERATURE + timebase].records()
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


