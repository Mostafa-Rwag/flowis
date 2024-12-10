import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    # معالجة الصورة
    return jsonify({'message': 'Image analyzed successfully'})

if __name__ == '__main__':
    # التأكد من أنه يستخدم المنفذ الذي يقدمه Railway (من خلال متغير البيئة PORT)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
