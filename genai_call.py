from openai import OpenAI

# Initialize client with your own base URL (not OpenAI's cloud)
client = OpenAI(
    base_url="http://your-server/v1",  # your Qwen model API base
    api_key="none"  # required param, but can be dummy if endpoint doesn’t need auth
)

# Call the model endpoint
response = client.chat.completions.create(
    model="qwen2.5-7b-instruct",  # your model name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain AI in simple terms."}
    ],
    temperature=0.7,
    max_tokens=512
)

print(response.choices[0].message.content)