import base64
import os
from mistralai import Mistral

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

# Get the image path from environment or configuration
image_path = "/path/to/your/image.jpg"  # Make sure this path is correct

# Check if the file exists
if not os.path.exists(image_path):
    print(f"Error: The image {image_path} does not exist.")
else:
    # Encode the image to base64
    base64_image = encode_image(image_path)

    if base64_image:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print("Error: Missing API key.")
        else:
            model = "pixtral-12b-2409"
            client = Mistral(api_key=api_key)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "is it food or recyclable plastic or none of the above?"
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ]

            try:
                # Send the request to Mistral API
                chat_response = client.chat.complete(
                    model=model,
                    messages=messages
                )

                # Ensure the response is valid before accessing
                if chat_response and chat_response.choices:
                    print(chat_response.choices[0].message.content)
                else:
                    print("Error: No valid response from the API.")

            except Exception as e:
                print(f"Error during chat completion: {e}")
