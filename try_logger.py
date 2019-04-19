import time
from inspect import getframeinfo, stack

class Logger:
  def __init__(self, name):
    self.name = name
    self.info = {}
    self.t_def = time.time()
    self.head = {}

  def set_header(self, category, header):
    self.head[category] = ",".join(["name", "category", "time(s)", "caller", "line"] + header)

  def add(self, category, message):
    caller = getframeinfo(stack()[1][0])
    if category not in self.info:
      self.info[category] = []
    self.info[category].append("{},{},{},{}".format(time.time(), caller.filename, caller.lineno, message))

  def __str__(self):
    s = ""
    for cat in self.info:
      for e in self.info[cat]:
        s += ",".join([self.name, cat, e]) + "\n"
    return s

  def save(self, filename=None):
    if filename is None:
      filename = "logs/logger_{}_{:0.2f}.csv".format(self.name, self.t_def)
    with open(filename, "w") as f:
      f.write(self.__str__())
      f.close()




if __name__=="__main__":
  l = Logger("try1")
  for e in range(10):
    l.add("one", e)
    l.add("two", e+5)
  for e in range(10):
    l.add("one", e)
  print(l)
  l.save()