class PowerMonitor:
    def __init__(self, voltage, current) -> None:
        self.__voltage = voltage
        self.__current = current

    def read_voltage_current(self):
        return (self.__voltage, self.__current)

    def run_diagnostics(self):
        return []

    def get_flags(self) -> dict:
        return {}
