from flask import Flask, request, jsonify
import cv2
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

def analyze_image_quality(image_path, sharpness_threshold=100.0, brightness_threshold=(50, 200), min_resolution=(256, 256)):
    # قراءة الصورة
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        return {"overall": False, "message": "الصورة غير موجودة أو المسار غير صحيح."}
    
    # تحويل الصورة إلى الأبيض والأسود
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # --- 1. وضوح الصورة ---
    laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
    sharpness_ok = laplacian_var >= sharpness_threshold
    
    # --- 2. الإضاءة (السطوع والتباين) ---
    brightness = np.mean(gray_image)
    brightness_ok = brightness_threshold[0] <= brightness <= brightness_threshold[1]
    
    # --- 3. حجم وأبعاد الصورة ---
    height, width = gray_image.shape
    resolution_ok = height >= min_resolution[0] and width >= min_resolution[1]
    
    # --- 4. التشويش ---
    noise_level = np.std(gray_image)
    noise_ok = noise_level < 50  # يمكن تعديل هذه القيمة حسب الحاجة
    
    # --- 5. تنسيق الصورة ---
    try:
        img_format = Image.open(image_path).format
        format_ok = img_format.lower() in ["jpeg", "jpg", "png"]
    except Exception:
        format_ok = False
        img_format = "unknown"
    
    # النتائج
    results = {
        "sharpness": {"value": laplacian_var, "ok": sharpness_ok},
        "brightness": {"value": brightness, "ok": brightness_ok},
        "resolution": {"value": (height, width), "ok": resolution_ok},
        "noise": {"value": noise_level, "ok": noise_ok},
        "format": {"value": img_format, "ok": format_ok},
        "overall": sharpness_ok and brightness_ok and resolution_ok and noise_ok and format_ok,
    }
    
    return results

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "ملف غير موجود"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "اختار ملفاً"}), 400
    
    # حفظ الملف في المجلد المؤقت
    image_path = os.path.join("uploads", file.filename)
    file.save(image_path)

    # تحليل جودة الصورة
    quality_report = analyze_image_quality(image_path)

    # حذف الصورة من السيرفر بعد المعالجة
    os.remove(image_path)
    
    # إرسال النتيجة للمستخدم
    if not quality_report["overall"]:
        return jsonify({"message": "الصورة لا تلبي معايير الجودة", "details": quality_report}), 400
    else:
        return jsonify({"message": "الصورة تلبي معايير الجودة", "details": quality_report}), 200

if __name__ == '__main__':
    app.run(debug=True)
