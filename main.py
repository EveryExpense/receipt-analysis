import io
import json
import urllib.request
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from PIL import Image
import pytesseract

app = FastAPI()

@app.post("/detect-text")
async def detect_text(
    files: list[UploadFile] = File(...),
    categories: str = Form(...),
    payment_methods: str = Form(...)
):
    cats = json.loads(categories)
    methods = json.loads(payment_methods)
    results = []
    
    for file in files:
        img_bytes = await file.read()
        try:
            image = Image.open(io.BytesIO(img_bytes))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        ocr_text = pytesseract.image_to_string(image)
        
        prompt = f"""
        Extract expense data from this OCR text into a single JSON object.
        You MUST use this EXACT structure and absolutely no other keys. Do NOT include 'transactions', 'keys', or 'total_amount'.
        
        {{
            "description": "string or null",
            "location": {{
                "lat": "float or null",
                "lng": "float or null",
                "city": "string or null"
            }},
            "amount": "float or null",
            "category": "must be strictly one of {cats} or null",
            "payment_method": "must be strictly one of {methods} or null"
        }}

        Respond ONLY with the JSON object.
        Text: {ocr_text}
        """

        req = urllib.request.Request(
            "http://llm-server:11434/api/generate",
            data=json.dumps({
                "model": "qwen2.5:0.5b",
                "prompt": prompt,
                "format": "json",
                "stream": False
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as response:
                llm_data = json.loads(response.read().decode("utf-8"))
                results.append(json.loads(llm_data["response"]))
        except Exception as e:
            results.append({"error": str(e), "raw": ocr_text})
            
    return {"results": results}