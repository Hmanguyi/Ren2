import base64
import requests
import os
from flask import Flask, request, jsonify
from mistralai import Mistral

app = Flask(__name__)

# Set your API key
API_KEY = "6pdlTRLqX2GhuEjgrtNJqwAhBWm8Yy6M"
MODEL = "pixtral-12b-2409"
client = Mistral(api_key=API_KEY)

def encode_image_from_url(image_url):
    """Download and encode the image to base64."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for bad responses
        return base64.b64encode(response.content).decode('utf-8')
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

@app.route('/classify', methods=['POST'])
def classify_image():
    data = request.json
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    base64_image = encode_image_from_url(image_url)
    if not base64_image:
        return jsonify({"error": "Failed to process image"}), 500

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "is it food or recyclable plastic or none of the above?"},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
            ]
        }
    ]

    try:
        chat_response = client.chat.complete(model=MODEL, messages=messages)
        response_text = chat_response.choices[0].message.content
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
