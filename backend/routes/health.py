import logging

from fastapi import APIRouter, HTTPException
from pymongo.errors import ConnectionFailure

from config.database import client

logger = logging.getLogger(__name__)
router = APIRouter()


async def perform_health_check():
    """
    Checks the database connection and raises an HTTPException on failure.
    This function is intended to be called by the health check endpoints.
    """
    try:
        await client.admin.command("ping")
    except ConnectionFailure as e:
        # A failure should always be logged, regardless of which endpoint was called.
        logger.error(f"HEALTH CHECK FAILED: Database connection error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Database connection is unhealthy.") from e


@router.get("", tags=["Health"])
async def verbose_health_check():
    """
    Provides a verbose health check for developers. It logs on both success and failure
    and gives a detailed response.
    """
    logger.info("Verbose health check initiated.")
    await perform_health_check()
    logger.info("Verbose health check successful: Database is connected.")
    return {"status": "ok", "database_status": "connected"}


@router.get("/silent", tags=["Health"])
async def silent_health_check():
    """
    Provides a silent health check for automated systems (e.g., Docker).
    It only logs on failure.
    """
    await perform_health_check()
    return {"status": "ok", "database_status": "connected"}
