from threading import Thread


class Timer(Thread):
    time = 0
    func = None

    def __init__(self, event, time, func):
        Thread.__init__(self)
        self.stopped = event
        self.time = time
        self.func = func

    def run(self):
        self.func()
        while not self.stopped.wait(self.time):
            self.func()
