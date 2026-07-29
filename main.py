from fastapi import FastAPI
from src.api.v1.analyze import router as analyze_router

app = FastAPI(
    title="ECG Arrhythmia Detection Microservice",
    description="IEC 62304 Class B Medical Software Microservice",
    version="0.1.0",
)

app.include_router(analyze_router, prefix="/api/v1", tags=["ECG Analysis"])


@app.get("/")
def health_check():
    return {"status": "healthy", "service": "ECG Arrhythmia Detection"}
