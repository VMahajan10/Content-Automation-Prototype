from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import tempfile
import shutil
from pathlib import Path
import uvicorn
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="File Upload Backend")

# Configure CORS to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "http://localhost:8502", "http://127.0.0.1:8502"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Log when the server starts"""
    logger.info("🚀 File Upload Backend starting...")
    logger.info(f"📁 Upload directory: {UPLOAD_DIR.absolute()}")
    logger.info("✅ File Upload Backend is ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "File Upload Backend is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check if upload directory is accessible
        if not UPLOAD_DIR.exists():
            UPLOAD_DIR.mkdir(exist_ok=True)
        
        return {
            "status": "healthy",
            "upload_directory": str(UPLOAD_DIR.absolute()),
            "directory_writable": os.access(UPLOAD_DIR, os.W_OK)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"📤 Uploading file: {file.filename}")
        
        # Create a temporary file to handle large uploads
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            # Copy uploaded file to temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Move to final location
        final_path = UPLOAD_DIR / file.filename
        shutil.move(temp_path, final_path)
        
        file_size = os.path.getsize(final_path)
        logger.info(f"✅ File uploaded successfully: {file.filename} ({file_size} bytes)")
        
        return JSONResponse({
            "filename": file.filename,
            "size": file_size,
            "path": str(final_path),
            "status": "success",
            "message": "File uploaded successfully"
        })
    
    except Exception as e:
        logger.error(f"❌ Upload failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files/")
async def list_files():
    """List all uploaded files"""
    try:
        files = []
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "path": str(file_path)
                })
        logger.info(f"📋 Listed {len(files)} files")
        return {"files": files}
    except Exception as e:
        logger.error(f"❌ Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a specific file"""
    try:
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f"🗑️ Deleted file: {filename}")
            return {"message": f"File {filename} deleted successfully"}
        else:
            logger.warning(f"⚠️ File not found for deletion: {filename}")
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"❌ Failed to delete file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.get("/files/{filename}/download")
async def download_file(filename: str):
    """Download a specific file"""
    try:
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            logger.info(f"📥 Downloading file: {filename}")
            return FileResponse(
                path=str(file_path),
                filename=filename,
                media_type='application/octet-stream'
            )
        else:
            logger.warning(f"⚠️ File not found for download: {filename}")
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"❌ Failed to download file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

if __name__ == "__main__":
    try:
        logger.info("🎯 Starting File Upload Backend Server...")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1) 