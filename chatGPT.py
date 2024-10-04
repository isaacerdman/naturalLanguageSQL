from openai import OpenAI

def ask_chatgpt(question, key):
    client = OpenAI(api_key=key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # can also use "gpt-4"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        max_tokens=500  # tokens returned
    )
    return response.choices[0].message.content