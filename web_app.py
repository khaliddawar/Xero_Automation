from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from services.monitor_service import MonitorService
from utils.logger import app_logger
from datetime import datetime
import threading
import time

app = FastAPI(title="Xero Invoice Automation")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables for service status
service_status = {
    "running": False,
    "last_check": None,
    "processed_count": 0,
    "last_error": None,
    "service_thread": None
}

monitor_service = MonitorService()

def run_service():
    """Background service runner"""
    while service_status["running"]:
        try:
            monitor_service.process_emails()
            service_status["last_check"] = datetime.now()
            time.sleep(300)  # 5 minutes between checks
        except Exception as e:
            service_status["last_error"] = str(e)
            app_logger.error(f"Service error: {e}")
            time.sleep(60)  # Wait 1 minute on error

@app.get("/")
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "status": service_status
        }
    )

@app.post("/start")
async def start_service():
    """Start the monitoring service"""
    if not service_status["running"]:
        service_status["running"] = True
        service_status["last_error"] = None
        # Start service in background thread
        service_status["service_thread"] = threading.Thread(target=run_service)
        service_status["service_thread"].daemon = True
        service_status["service_thread"].start()
        return {"status": "Service started"}
    return {"status": "Service already running"}

@app.post("/stop")
async def stop_service():
    """Stop the monitoring service"""
    if service_status["running"]:
        service_status["running"] = False
        if service_status["service_thread"]:
            service_status["service_thread"].join(timeout=1)
        return {"status": "Service stopped"}
    return {"status": "Service not running"}

@app.get("/status")
async def get_status():
    """Get current service status"""
    return {
        "running": service_status["running"],
        "last_check": service_status["last_check"].isoformat() if service_status["last_check"] else None,
        "processed_count": service_status["processed_count"],
        "last_error": service_status["last_error"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
