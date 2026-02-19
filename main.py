@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("🔥🔥🔥 PAYLOAD COMPLETO RECEBIDO:")
    print(data)

    return {"status": "ok"}
