from openai import OpenAI
import os
import json

PERPLEXITY_API_KEY = os.getenv("perplexity_api_key")

def get_sources(tag_line, num_cards):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a researcher. Prioritize high-quality sources."
            ),
        },
        {
            "role": "user",
            "content": (
                f"""Find {num_cards} sources supporting this argument: {tag_line}. Return your response as a JSON in this form:
    {{
        "Source 1 URL": "10-word summary of main argument in source 1",
        "Source 2 URL": "10-word summary of main argument in source 2"
    }}"""
            ),
        },
    ]

    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = client.chat.completions.create(
        model="llama-3-sonar-large-32k-online",
        messages=messages,
    )
    # print(response.choices[0].message.content)
    try:
        result = json.loads(response.choices[0].message.content)
        print(result)
        return result
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        # Handle the error or return a default value
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors
        return {}
    
if __name__ == '__main__':
    get_sources("Fiscal redistribution is good")