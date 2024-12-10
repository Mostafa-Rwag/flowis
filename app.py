import os
from flask import Flask, request, jsonify
import cv2
import numpy as np
from PIL import Image

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
    
    # --- 2. الإضاءة (السطوع والتباين) ---from flask import Flask, request, jsonify
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    # التحقق من وجود الملف في الطلب
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    # التحقق من أن الملف غير فارغ
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # قراءة الصورة باستخدام OpenCV
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'Invalid image file'}), 400
    
    # تنفيذ المعالجة على الصورة (مثلاً فحص الصورة أو عمليات أخرى)
    # هنا يمكن إضافة أي منطق خاص بك لمعالجة الصورة
    
    # على سبيل المثال، نقوم بحفظ الصورة التي تم استلامها (لأغراض تجريبية)
    cv2.imwrite('uploaded_image.jpg', img)

    return jsonify({'message': 'Image received and processed successfully'}), 200

if __name__ == '__main__':
    # تشغيل الخادم على جميع العناوين (0.0.0.0) و المنفذ 8080
    app.run(host='0.0.0.0', port=8080)

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

@app.route('/analyze', methods=['POST'])
def analyze():
    # التحقق من وجود صورة في الطلب
    if 'file' not in request.files:
        return jsonify({"message": "لم يتم إرسال صورة"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "لم يتم إرسال صورة"}), 400
    
    # حفظ الصورة مؤقتًا
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    
    # تحليل الصورة
    quality_report = analyze_image_quality(file_path)
    
    # طباعة النتائج
    if not quality_report["overall"]:
        if "message" in quality_report:
            return jsonify(quality_report), 400
        else:
            return jsonify(quality_report), 400
    else:
        return jsonify(quality_report)

if __name__ == '__main__':
    # تشغيل التطبيق على Railway (المنفذ سيكون محدد من Railway)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
