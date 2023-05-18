import time

class CircuitBreaker:
    def __init__(self, maxFaults=3, waitTimeToReset=10):
        self.maxFaults = maxFaults                  # my threshold
        self.waitTimeToReset = waitTimeToReset      # time in seconds before reset the circuit to closed state
        self.faultsCount = 0                        # current number of faults
        self.isOpen = False                         # circuit state default is closed (call external API)
        self.lastTimeFault = None                   # last time when circuit was opened (used to reset the circuit)

    def callExternalAPI(self, func):
        if self.isOpen:
            return None         # Circuit is open
        # Circuit is closed, so call the external service
        try:
            result = func()
            self.reset()
            return result
        except Exception as e:
            self.handleFault()
            raise e

    def halfOpenTryOneCall(self, func):
        try:
            result = func()
            self.reset()
            return result
        except Exception as e:
            self.lastTimeFault = time.time()
            raise e

    def handleFault(self):
        self.faultsCount += 1
        if self.faultsCount >= self.maxFaults:
            self.isOpen = True
            self.lastTimeFault = time.time()

    def reset(self):
        self.faultsCount = 0
        self.isOpen = False
        self.lastTimeFault = None
