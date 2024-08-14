import gc
import sys

from core import logger, setup_logger, state_manager
from core.states import STATES
from hal.configuration import SATELLITE
from sm_configuration import SM_CONFIGURATION, TASK_REGISTRY

for path in ["/hal", "/apps", "/core"]:
    if path not in sys.path:
        sys.path.append(path)

setup_logger(level="INFO")


gc.collect()
logger.info("Memory free: " + str(gc.mem_free()) + " bytes")


logger.info("Booting ARGUS-1...")
boot_errors = SATELLITE.boot_sequence()
logger.info("ARGUS-1 booted.")
logger.warning(f"Boot Errors: {boot_errors}")

"""print("Running system diagnostics...")
errors = SATELLITE.run_system_diagnostics()
print("System diagnostics complete")
print("Errors:", errors)
"""

gc.collect()
logger.info("Memory free: " + str(gc.mem_free()) + " bytes")

try:
    # Run forever

    logger.info("Starting state manager")
    state_manager.start(STATES.STARTUP, SM_CONFIGURATION, TASK_REGISTRY)

except Exception as e:
    logger.critical("ERROR:", e)
    # TODO Log the error
