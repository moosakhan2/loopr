"""
watsonx_client.py

Wrapper around the watsonx.ai text generation REST API.
Reads credentials from .env and exposes a simple complete() function.
"""

import os
import requests
from dotenv import load_dotenv


def _get_iam_token(api_key: str) -> str:
    """Exchange IBM Cloud API key for an IAM access token."""
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}",
        timeout=30
    )
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get IAM token: {response.text}")
    return response.json()["access_token"]


def complete(prompt: str) -> str:
    """Send a prompt to watsonx.ai and return the raw text response."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get required credentials
    api_key = os.getenv("WATSONX_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    base_url = os.getenv("WATSONX_URL")
    
    # Validate credentials
    if not api_key:
        raise RuntimeError("WATSONX_API_KEY not found in .env file")
    if not project_id:
        raise RuntimeError("WATSONX_PROJECT_ID not found in .env file")
    if not base_url:
        raise RuntimeError("WATSONX_URL not found in .env file")
    
    # Construct the API endpoint
    endpoint = f"{base_url}/ml/v1/text/generation?version=2023-05-29"
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {_get_iam_token(api_key)}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Prepare request body
    # Using granite-13b-chat-v2 as a good balance of performance and quality
    payload = {
        "model_id": "ibm/granite-3-8b-instruct",
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 2000,
            "min_new_tokens": 0,
            "stop_sequences": [],
            "repetition_penalty": 1.0
        },
        "project_id": project_id
    }
    
    try:
        # Make the API request
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
        # Check for HTTP errors
        if response.status_code != 200:
            error_detail = response.text
            raise RuntimeError(
                f"watsonx.ai API request failed with status {response.status_code}: {error_detail}"
            )
        
        # Parse the response
        response_data = response.json()
        
        # Extract the generated text
        if "results" in response_data and len(response_data["results"]) > 0:
            generated_text = response_data["results"][0].get("generated_text", "")
            return generated_text.strip()
        else:
            raise RuntimeError(
                f"Unexpected response format from watsonx.ai: {response_data}"
            )
    
    except requests.exceptions.Timeout:
        raise RuntimeError("watsonx.ai API request timed out after 60 seconds")
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Failed to connect to watsonx.ai API: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"watsonx.ai API request failed: {str(e)}")
    except ValueError as e:
        raise RuntimeError(f"Failed to parse watsonx.ai API response as JSON: {str(e)}")


if __name__ == "__main__":
    # Simple test to verify the client works
    print("Testing watsonx_client.py...")
    print("-" * 50)
    
    try:
        test_prompt = "Write a simple Python function that adds two numbers."
        print(f"Prompt: {test_prompt}\n")
        
        result = complete(test_prompt)
        print(f"Response:\n{result}")
        print("-" * 50)
        print("✓ watsonx_client.py is working correctly!")
        
    except RuntimeError as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have a .env file with:")
        print("  WATSONX_API_KEY=your_key_here")
        print("  WATSONX_PROJECT_ID=your_project_id_here")
        print("  WATSONX_URL=https://us-south.ml.cloud.ibm.com")

# Made with Bob
