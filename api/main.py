from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from collections import Counter
import os
import socket
import time



# Add metrics storage
request_counter = Counter()
start_time = time.time()

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    uptime = time.time() - start_time
    metrics_text = f"""# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{{method="GET",endpoint="/user"}} {request_counter['/user']}
http_requests_total{{method="GET",endpoint="/container"}} {request_counter['/container']}
http_requests_total{{method="GET",endpoint="/health"}} {request_counter['/health']}

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime}

# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="1.0.0",container_id="{socket.gethostname()}"}} 1
"""
    return Response(content=metrics_text, media_type="text/plain")

# Update existing endpoints to count requests
@app.get("/user")
async def get_user():
    request_counter['/user'] += 1
    # ... rest of your code

@app.get("/container")
async def get_container_id():
    request_counter['/container'] += 1
    # ... rest of your code

@app.get("/health")
async def health_check():
    request_counter['/health'] += 1


app = FastAPI(
    title="Milestone 2 API",
    description="API for Jeron's Kubernetes project",
    version="1.0.0"
)

# CORS configuration to allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection parameters from environment variables
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "milestone2")

# Create MongoDB client (connection pooling handled automatically)
mongo_client = None

def get_mongo_client():
    """Get or create MongoDB client"""
    global mongo_client
    if mongo_client is None:
        try:
            mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
            mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            mongo_client.admin.command('ping')
            print(f"✓ Connected to MongoDB at {mongo_uri}")
        except ConnectionFailure as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise
    return mongo_client

def get_db():
    """Get database instance"""
    client = get_mongo_client()
    return client[MONGO_DB]

@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection and create initial data"""
    try:
        db = get_db()
        users_collection = db.users
        
        # Create initial user if collection is empty
        if users_collection.count_documents({}) == 0:
            users_collection.insert_one({
                "user_id": 1,
                "name": "Jeron"
            })
            print("✓ Initial user created")
        
        print("✓ Application startup complete")
    except Exception as e:
        print(f"✗ Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("✓ MongoDB connection closed")

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Milestone 2 API is running",
        "status": "healthy",
        "container_id": socket.gethostname(),
        "database": "MongoDB"
    }

@app.get("/user")
async def get_user():
    """Get user name from database"""
    try:
        db = get_db()
        users_collection = db.users
        
        # Query to get the user name
        user = users_collection.find_one({"user_id": 1})
        
        if user:
            return {"name": user.get("name", "Unknown User")}
        else:
            return {"name": "No User Found"}
            
    except Exception as e:
        print(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@app.get("/container")
async def get_container_id():
    """Get the container ID (hostname)"""
    try:
        container_id = socket.gethostname()
        return {
            "container_id": container_id,
            "message": "Container ID retrieved successfully"
        }
    except Exception as e:
        print(f"Error getting container ID: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes"""
    try:
        # Test database connection
        db = get_db()
        db.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "container_id": socket.gethostname()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)