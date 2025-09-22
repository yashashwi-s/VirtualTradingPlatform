from fastapi import FastAPI

# Simple test app to verify basic functionality
app = FastAPI(title="Virtual Trading Platform Test")

@app.get("/")
async def root():
    return {"message": "Virtual Trading Platform API - Test OK"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)