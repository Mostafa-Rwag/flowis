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
def analyze_image_quality(image_path, sharpness_threshold=100.0, brightness_threshold=(50, 200), min_resolution=(256, 256), noise_threshold=50.0, saturation_threshold=0.5):
    try:
        # قراءة الصورة
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            return {"overall": False, "message": "الصورة غير موجودة أو المسار غير صحيح."}
        
        # تحويل الصورة إلى الأبيض والأسود
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # --- 1. وضوح الصورة (Sharpness) ---
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        sharpness_ok = laplacian_var >= sharpness_threshold
        
        # --- 2. الإضاءة (Brightness) ---
        brightness = np.mean(gray_image)
        brightness_ok = brightness_threshold[0] <= brightness <= brightness_threshold[1]
        
        # --- 3. حجم وأبعاد الصورة (Resolution) ---
        height, width = gray_image.shape
        resolution_ok = height >= min_resolution[0] and width >= min_resolution[1]
        
        # --- 4. التشويش (Noise) ---
        noise_level = np.std(gray_image)
        noise_ok = noise_level < noise_threshold
        
        # --- 5. تنسيق الصورة (Format) ---
        try:
            img_format = Image.open(image_path).format
            format_ok = img_format.lower() in ["jpeg", "jpg", "png"]
        except Exception:
            format_ok = False
            img_format = "unknown"
        
        # --- 6. التشبع (Saturation) ---
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv_image[:,:,1]) / 255  # مستوى التشبع في نطاق 0 إلى 1
        saturation_ok = saturation >= saturation_threshold
        
        # --- 7. توازن اللون الأبيض (White Balance) ---
        avg_b = np.mean(image[:,:,0])
        avg_g = np.mean(image[:,:,1])
        avg_r = np.mean(image[:,:,2])
        white_balance_ok = (avg_r - avg_g) < 10 and (avg_g - avg_b) < 10  # يمكن تعديل القيم حسب الحاجة
        
        # --- 8. التشوهات الهندسية (Distortion) ---
        # يمكن استخدام تحليل الوجوه أو الأشكال للكشف عن التشوهات.
        distortion_ok = True  # يمكن إضافة تقنيات فحص للتشوهات مثل كشف الزوايا والتشوهات الهندسية
        
        # النتائج
        results = {
            "sharpness": {"value": laplacian_var, "ok": bool(sharpness_ok)},
            "brightness": {"value": brightness, "ok": bool(brightness_ok)},
            "resolution": {"value": (height, width), "ok": bool(resolution_ok)},
            "noise": {"value": noise_level, "ok": bool(noise_ok)},
            "format": {"value": img_format, "ok": bool(format_ok)},
            "saturation": {"value": saturation, "ok": bool(saturation_ok)},
            "white_balance": {"value": (avg_r, avg_g, avg_b), "ok": bool(white_balance_ok)},
            "distortion": {"value": distortion_ok, "ok": bool(distortion_ok)},
            "overall": bool(sharpness_ok and brightness_ok and resolution_ok and noise_ok and format_ok and saturation_ok and white_balance_ok and distortion_ok),
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
