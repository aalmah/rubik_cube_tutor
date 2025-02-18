import os
import base64
from anthropic import Anthropic
import json
from PIL import Image
import io

def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_rubiks_cube(image_input):
    """
    Analyze a Rubik's cube image from a file path, PIL Image, or bytes object
    Args:
        image_input: Either a string path to an image file, PIL Image object, or bytes/BytesIO object
    """
    # Initialize Anthropic client
    client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    # Encode image based on input type
    if isinstance(image_input, str):
        # Input is a file path
        base64_image = encode_image_to_base64(image_input)
    elif isinstance(image_input, Image.Image):
        # Input is a PIL Image - convert to bytes using BytesIO
        buffered = io.BytesIO()
        image_input.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    else:
        # Input is already a bytes/BytesIO object
        base64_image = base64.b64encode(image_input).decode('utf-8')

    # Prepare the message with the image
    system_prompt = "Return ONLY a valid JSON object with no additional text. The response must contain exactly six possible color values: 'white', 'yellow', 'red', 'orange', 'blue', or 'green'."
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image
                    }
                },
                {
                    "type": "text",
                    "text": "Analyze this webcam-captured Rubik's cube image. Identify each square's color on the visible face, matching to only these allowed colors: white, yellow, red, orange, blue, green. Account for lighting variations and webcam distortion. Return a JSON with a 3x3 grid array of colors and confidence level."
                }
            ]
        }
    ]

    # Get Claude's response
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        system=system_prompt,
        messages=messages
    )

    # Parse the JSON response
    try:
        result = json.loads(response.content[0].text)
        if 'grid' in result:
            print_cube_colors(result['grid'])
            return result['grid']
        else:
            print("Error: Response doesn't contain a 'grid' field")
            print("Full response structure:", result)
            return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None

def print_cube_colors(colors):
    if not colors:
        return
    
    print("\nCube face colors:")
    print("-" * 13)
    for row in colors:
        print("| " + " | ".join(c.ljust(6) for c in row) + " |")
        print("-" * 13)

if __name__ == "__main__":
    # Make sure ANTHROPIC_API_KEY is set in your environment variables
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: Please set your ANTHROPIC_API_KEY environment variable")
        exit(1)

    analyze_rubiks_cube('captured_cube.jpg')
