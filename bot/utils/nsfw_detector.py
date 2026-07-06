"""
Thin wrapper around NudeNet so the rest of the bot doesn't need to know
about label names or thresholds. Runs fully locally/offline - the model
weights are downloaded automatically by the nudenet package on first use
and cached on disk, no external API calls are made afterwards.
"""
import asyncio
import logging

from nudenet import NudeDetector

from bot.config import NSFW_THRESHOLD

logger = logging.getLogger(__name__)

# Labels NudeNet can return that we consider actual nudity worth acting on.
# (Covered body parts / faces / feet etc are intentionally NOT in this set
# so the filter doesn't nuke normal selfies or beach photos.)
UNSAFE_LABELS = {
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "BUTTOCKS_EXPOSED",
    "ANUS_EXPOSED",
}

_detector = None
_detector_lock = asyncio.Lock()


def _load_detector() -> NudeDetector:
    global _detector
    if _detector is None:
        logger.info("Loading NudeNet model (first run may download weights)...")
        _detector = NudeDetector()
    return _detector


async def is_image_nsfw(image_path: str) -> bool:
    """
    Returns True if the image at image_path is classified as containing
    exposed nudity above the configured confidence threshold.
    Runs the (blocking, CPU-bound) model call in a thread so it doesn't
    block the asyncio event loop.
    """
    async with _detector_lock:
        detector = _load_detector()

    loop = asyncio.get_running_loop()
    try:
        detections = await loop.run_in_executor(None, detector.detect, image_path)
    except Exception:
        logger.exception("NudeNet detection failed for %s", image_path)
        return False

    for det in detections:
        label = det.get("class") or det.get("label")
        score = det.get("score", 0)
        if label in UNSAFE_LABELS and score >= NSFW_THRESHOLD:
            return True
    return False
