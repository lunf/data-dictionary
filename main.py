"""
Main entry point for the Business Term Extraction pipeline.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routes import glossary_router, domain_router, process_router


app = FastAPI(title="Business Glossary API")

app.include_router(glossary_router.router, prefix="/api")
app.include_router(domain_router.router, prefix="/api")
app.include_router(process_router.router, prefix="/api")


# Allow frontend (Vite) to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the Business Glossary API"}

def main():
    print("🚀 Starting Business Term Extraction Pipeline...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
