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

def process_image(image_path):
    """Process the image and send it to the Mistral API."""
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: The image {image_path} does not exist.")
        return

    # Encode the image to base64
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

# Main function that handles the image path and API call
if __name__ == "__main__":
    # Get the image path from environment variable
    image_path = os.getenv("IMAGE_PATH")  # Make sure to set this environment variable

    if not image_path:
        print("Error: IMAGE_PATH environment variable is missing.")
    else:
        process_image(image_path)
