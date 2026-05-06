from fastapi import FastAPI, UploadFile
import io
from PIL import Image
import pytesseract

app = FastAPI()

@app.post("/detect-text")
async def detect_text(files: list[UploadFile]):
    pred_list = []
    for file in files:
        bytes_str = io.BytesIO(await file.read())
        try:
            image = Image.open(bytes_str)
        except:
            raise HTTPException(status_code=400, detail="Invalid image")
        preds = pytesseract.image_to_string(image)
        preds_list += [x for x in preds.split("\n")]
    return {"results": preds_list }