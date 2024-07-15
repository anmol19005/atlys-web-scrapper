import logging


class Notifier:
    def notify(self, message: str):
        raise NotImplementedError("Subclasses should implement this method")


class ConsoleNotifier(Notifier):
    def notify(self, message: str):
        #print(message)
        logging.info(message)
