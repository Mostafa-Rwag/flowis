from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)

# إنشاء مجلد لتخزين الصور إذا لم يكن موجوداً
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# تحديد المكان الذي سيتم فيه تخزين الملفات المرفوعة
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return "Welcome to the Image Upload and Quality Check API!"

# فحص جودة الصورة
def analyze_image_quality(image_path, sharpness_threshold=100.0, brightness_threshold=(50, 200), min_resolution=(256, 256)):
    try:
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
            "sharpness": {"value": laplacian_var, "ok": bool(sharpness_ok)},  # تحويل القيمة إلى bool
            "brightness": {"value": brightness, "ok": bool(brightness_ok)},  # تحويل القيمة إلى bool
            "resolution": {"value": (height, width), "ok": bool(resolution_ok)},  # تحويل القيمة إلى bool
            "noise": {"value": noise_level, "ok": bool(noise_ok)},  # تحويل القيمة إلى bool
            "format": {"value": img_format, "ok": bool(format_ok)},  # تحويل القيمة إلى bool
            "overall": bool(sharpness_ok and brightness_ok and resolution_ok and noise_ok and format_ok),  # تحويل القيمة إلى bool
        }
        
        return results
    except Exception as e:
        return {"error": "Error processing the image", "details": str(e)}

# تعريف مسار رفع الصورة
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part", "files": request.files}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # حفظ الملف في المجلد المحدد
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # هنا يمكن إضافة فحص الجودة
        quality_check_results = analyze_image_quality(file_path)

        # إرجاع النتيجة بعد الفحص
        return jsonify({"message": "File uploaded successfully", "file_path": file_path, "quality_check": quality_check_results}), 200
    
    except Exception as e:
        print(f"Error during image processing: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
