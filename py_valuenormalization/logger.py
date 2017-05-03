# Creates log for all messages
# print_on_log flag to decide if log message needs to be printed or not

class Logger():
    def __init__(self, name="", print_on_log=False):
        self._name = name
        self._log_entries = []
        self._print_on_log = print_on_log
        
    def log(self, entry):
        self._log_entries.append(entry)
        if self._print_on_log:
            print("[%s] %s"%(self._name, str(entry)))

