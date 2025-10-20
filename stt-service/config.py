import os
import logging

logger = logging.getLogger(__name__)

# The device to run the STT model on ('cpu' or 'cuda').
# Injected by docker-compose.yml and docker-compose.gpu.yml.
DEVICE = os.getenv("STT_DEVICE", "cpu")

# Set the compute type based on the selected device for optimal performance.
if DEVICE == "cuda":
    COMPUTE_TYPE = "auto"
    logger.info("STT Service: Configured for GPU (CUDA) execution.")
else:
    COMPUTE_TYPE = "int8"
    logger.info("STT Service: Configured for CPU execution.")
