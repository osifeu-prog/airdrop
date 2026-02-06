from PIL import Image, ImageDraw, ImageFont
import os

def generate_certificate(name, user_id):
    # יצירת תמונה ריקה (רקע כחול כהה של SLH)
    img = Image.new('RGB', (800, 500), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # הוספת מסגרת צינית (Cyan)
    draw.rectangle([20, 20, 780, 480], outline=(34, 211, 238), width=5)
    
    # טקסט (כאן נשתמש בפונט ברירת מחדל, בפרודקשן כדאי להעלות קובץ .ttf)
    try:
        # נסיון להשתמש בפונט מערכת, אם לא קיים נשתמש בברירת מחדל
        text = f"Expert Candidate: {name}"
        draw.text((400, 200), text, fill=(255, 255, 255), anchor="mm")
        draw.text((400, 250), "SLH Socionomics Network", fill=(34, 211, 238), anchor="mm")
    except:
        draw.text((100, 200), f"Expert: {name}", fill=(255, 255, 255))

    path = f"webapp/certificates/cert_{user_id}.png"
    img.save(path)
    return path
