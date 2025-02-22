import base64
import requests
from flask import Flask, request, jsonify
from mistralai import Mistral

app = Flask(__name__)

# Set your API key and model
API_KEY = "6pdlTRLqX2GhuEjgrtNJqwAhBWm8Yy6M"
MODEL = "pixtral-12b-2409"
client = Mistral(api_key=API_KEY)

def process_base64_image(base64_image):
    """Ensure the image string has only one 'data:image/jpeg;base64,' prefix."""
    try:
        # Only add the prefix if it's not already there
        if not base64_image.startswith('data:image/jpeg;base64,'):
            base64_image = f"data:image/jpeg;base64,{base64_image}"
        return base64_image
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

@app.route('/classify', methods=['POST'])
def classify_image():
    data = request.json
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    # Process the image URL and ensure it's correctly formatted
    base64_image = process_base64_image(image_url)
    if not base64_image:
        return jsonify({"error": "Failed to process image"}), 500

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "is it food or recyclable plastic or none of the above?"},
                {"type": "image_url", "image_url": base64_image}
            ]
        }
    ]

    try:
        # Send the image data to the model for classification
        chat_response = client.chat.complete(model=MODEL, messages=messages)
        response_text = chat_response.choices[0].message.content
        response = {"response": response_text}
        
        # Log the response for debugging
        print("Raw Response:", response)
        
        return jsonify(response)
    except Exception as e:
        # Log the error for debugging
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
