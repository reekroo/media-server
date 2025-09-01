import logging
import sys

from . import configs
from .ups_service import UpsService
from .shutdown_policy import ShutdownPolicy, ShutdownConfig
from .status_writer import StatusWriter
from .providers.geekworm_x1200 import GeekwormX1200
from .display_soc_calculator import DisplaySoCCalculator

def main():
    file_handler = logging.FileHandler(configs.UPS_LOG_FILE, mode='a')
    stdout_handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - UpsService - %(levelname)s - %(message)s',
        handlers=[file_handler, stdout_handler]
    )
    logger = logging.getLogger(__name__)

    try:
        provider = GeekwormX1200(
            i2c_bus=configs.I2C_BUS,
            i2c_addr=configs.I2C_ADDR,
            gpio_ac_pin=configs.GPIO_AC_PIN,
            ac_active_high=configs.AC_ACTIVE_HIGH
        )
        
        shutdown_config = ShutdownConfig(
            low_battery_percent=configs.LOW_BATTERY_PERCENT,
            critical_voltage_v=configs.CRITICAL_VOLTAGE_V,
            debounce_sec=configs.LOW_BATT_DEBOUNCE_SEC,
            shutdown_cmd=configs.SHUTDOWN_CMD,
            dry_run=configs.DRY_RUN
        )
        
        shutdown_policy = ShutdownPolicy(shutdown_config, logger)
        status_writer = StatusWriter(configs.UPS_STATUS_PATH)        
        soc_calculator = DisplaySoCCalculator(configs.VOLTAGE_MIN, configs.VOLTAGE_MAX)

        service = UpsService(
            provider=provider,
            policy=shutdown_policy,
            writer=status_writer,
            soc_calc=soc_calculator,
            logger=logger,
            poll_interval=configs.POLL_INTERVAL_SEC
        )
        
        service.loop()

    except KeyboardInterrupt:
        logger.info("Service stopped by user.")
    except Exception as e:
        logger.critical(f"Service failed to start or run: {e}", exc_info=True)

if __name__ == '__main__':
    main()