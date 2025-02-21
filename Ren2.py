import base64
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from mistralai import Mistral

app = Flask(__name__)

# Set a folder where images will be stored
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Set the upload folder for Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if the file is an allowed type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def process_image(image_path):
    """Process the image and send it to the Mistral API."""
    if not os.path.exists(image_path):
        print(f"Error: The image {image_path} does not exist.")
        return

    base64_image = encode_image(image_path)

    if base64_image:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print("Error: Missing API key.")
            return

        model = "pixtral-12b-2409"
        client = Mistral(api_key=api_key)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Is it food or recyclable plastic or none of the above?"
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }
        ]

        try:
            chat_response = client.chat.complete(
                model=model,
                messages=messages
            )

            if chat_response and chat_response.choices:
                print(chat_response.choices[0].message.content)
            else:
                print("Error: No valid response from the API.")
        except Exception as e:
            print(f"Error during chat completion: {e}")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
        
        # Once image is saved, process it
        process_image(image_path)
        
        return jsonify({"message": "File uploaded and processed successfully"}), 200
    
    return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Get the port from the environment variable (for deployment on Render)
    port = int(os.getenv("PORT", 5000))  # Default to 5000 if the PORT variable isn't set
    app.run(debug=True, host='0.0.0.0', port=port)
