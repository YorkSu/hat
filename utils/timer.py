import time


class Timer(object):

  def __init__(self, Log, *args, **kwargs):
    self.Log = Log
    return super().__init__(*args, **kwargs)

  @property
  def time(self):
    return time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())

  def mktime(self, timex):
    return time.mktime(time.strptime(timex, '%Y-%m-%d-%H-%M-%S'))

  def timer(self, text, func, *args, **kwargs):
    start_time = self.time
    self.Log(start_time, _T=f'{text} Start:')
    result = func(*args, **kwargs)
    stop_time = self.time
    self.Log(stop_time, _T=f'{text} Stop:')
    cost_time = self.mktime(stop_time) - self.mktime(start_time)
    self.Log(cost_time, _T=f'{text} cost time (second):')
    time_dict = {f'{text}_start_time'.upper(): start_time,
                 f'{text}_stop_time'.upper(): stop_time,
                 f'{text}_cost_time'.upper(): cost_time}
    return time_dict, result