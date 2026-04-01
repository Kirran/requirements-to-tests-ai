from openai import OpenAI
client = OpenAI()

def call_openai_api(prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text