from flask import Flask, request, jsonify
import cv2
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# دالة لتحليل الصورة (يمكنك إضافة تحليل أكثر تعقيدًا حسب الحاجة)
def process_image(image_file):
    # تحويل الصورة إلى صيغة OpenCV
    img = Image.open(image_file)
    img = np.array(img)

    # تحويل الصورة إلى اللون الرمادي
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # يمكن إضافة المزيد من العمليات على الصورة هنا (مثل الكشف عن الأشياء أو الأمراض)
    
    # إرجاع نتائج معالجة الصورة (هنا كمثال فقط)
    return gray_img.tolist()  # تحويل الصورة إلى قائمة يمكن إرسالها عبر JSON

@app.route('/process', methods=['POST'])
def process_image_api():
    # التحقق من أن الملف تم إرساله
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # التحقق من امتداد الملف (اختياري: تأكد أنه صورة)
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # معالجة الصورة باستخدام دالة process_image
    try:
        result = process_image(file)
        return jsonify({"processed_image": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # تأكد من أن التطبيق يعمل على جميع العناوين وليس فقط 127.0.0.1
    app.run(host='0.0.0.0', port=8080, debug=False)
