import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import uvicorn

# Import our schema
from .schema.schema import schema
from .seed_data import seed_database

# Create the FastAPI app
app = FastAPI(
    title="Supergraph API",
    description="A GraphQL API for managing leads, tasks, notes, appointments, and vehicles",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GraphQL endpoint
graphql_app = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])

# Seed the database with sample data on startup
@app.on_event("startup")
async def startup_event():
    if os.getenv("ENV") != "production":
        seed_database()
        print("Database seeded with sample data")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# For local development
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)