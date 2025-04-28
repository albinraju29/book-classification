from .utils import model_components
import logging

logger = logging.getLogger(__name__)

try:
    # This will trigger the model loading when the package is imported
    from .utils import model_components
except Exception as e:
    logger.error(f"Failed to load model components: {str(e)}")
    raise