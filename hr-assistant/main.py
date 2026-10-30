from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/chat")
async def chat(message: str):
    # Here you would implement the logic to handle the chat message
    # For demonstration purposes, we'll just echo the message back
    return {"response": f"You said: {message
                                     }"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
