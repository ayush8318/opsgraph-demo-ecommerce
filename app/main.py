from fastapi import FastAPI
import logging
from pathlib import Path
from prometheus_client import Gauge
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import os
import psutil
from prometheus_client import Counter
from prometheus_client import Histogram
import time

# ------------------------------------------------
# Application logging configuration
# Assume this is configured by the Ecommerce team
# ------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "ecommerce.log"


# Common format for our application logs
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


# One file handler
file_handler = logging.FileHandler(
    LOG_FILE,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)


# -------------------------
# Application logger
# -------------------------

logger = logging.getLogger("ecommerce")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)


# -------------------------
# Uvicorn access logger
# -------------------------

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.addHandler(file_handler)


# -------------------------
# Uvicorn error logger
# -------------------------

uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.addHandler(file_handler)
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
# )

logger = logging.getLogger("ecommerce")

app = FastAPI(
    title="OpsGraph Demo Ecommerce",
    version="1.0.0",
)

db_active_connections = Gauge(
    "db_active_connections",
    "Current number of active database connections"
)
process = psutil.Process(os.getpid())

process_cpu_percent = Gauge(
    "process_cpu_percent",
    "CPU usage percentage of the Ecommerce process"
)

process_memory_bytes = Gauge(
    "process_memory_bytes",
    "Memory used by the Ecommerce process in bytes"
)
 

 

payment_requests_total = Counter(
    "payment_requests_total",
    "Total payment requests"
)

payment_errors_total = Counter(
    "payment_errors_total",
    "Total failed payment requests"
)

payment_request_duration_seconds = Histogram(
    "payment_request_duration_seconds",
    "Time spent processing payment requests"
)

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/products")
async def get_products():
    logger.info("Product list requested")
    return {
        "products": [
            {"id": 1, "name": "Laptop", "price": 65000},
            {"id": 2, "name": "Headphones", "price": 3000},
            {"id": 3, "name": "Keyboard", "price": 1500}
        ]
    }

@app.get("/payment-test")
async def payment_test():
    payment_requests_total.inc()

    start_time = time.perf_counter()

    logger.info("Payment request received")

    db_active_connections.set(100)

    try:
        raise RuntimeError("Database connection pool exhausted")

    except Exception:
        payment_errors_total.inc()
        logger.exception("Payment processing failed")
        raise

    finally:
        duration = time.perf_counter() - start_time
        payment_request_duration_seconds.observe(duration)
@app.get("/metrics")
async def metrics():

    process_cpu_percent.set(
        process.cpu_percent(interval=None)
    )

    process_memory_bytes.set(
        process.memory_info().rss
    )
    

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )