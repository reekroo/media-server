class DisplaySoCCalculator:
    def __init__(self, voltage_min: float, voltage_max: float):
        self._voltage_min = voltage_min
        self._voltage_max = voltage_max
        self._last_display_soc = 101.0

    def calculate(self, voltage: float, ac_present: bool) -> float:
        voltage_clamped = max(self._voltage_min, min(self._voltage_max, voltage))
        percentage_raw = ((voltage_clamped - self._voltage_min) / 
                          (self._voltage_max - self._voltage_min)) * 100

        if not ac_present and percentage_raw < self._last_display_soc:
            self._last_display_soc = percentage_raw
        elif ac_present:
            self._last_display_soc = percentage_raw
            
        return self._last_display_soc