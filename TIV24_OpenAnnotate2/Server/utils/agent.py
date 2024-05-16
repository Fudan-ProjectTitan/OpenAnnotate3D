import os
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

import openai
model_name = "gpt-4-1106-preview"
request_timeout = 60
temperature = 0

def _run(message):
    response = openai.ChatCompletion.create(
        model=model_name,
        temperature=temperature,
        request_timeout=request_timeout,
        messages=message
    )
    
    return response.choices[0].message.content

def translate(question):
    messages=[
            {"role": "system", "content": """
                You are TranslateGPT, a professional agent who translate user input to English for users. Generate the answer as best you can.
                Follow the following rules:
                Always translate the input to English, if it is already English, output as is.

                Begin! Remember to Keep the description as concise as possible. 
            """},
            {"role": "user", "content": question},
    ]
    
    return _run(messages)