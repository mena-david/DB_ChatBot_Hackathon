import openai

model = "gpt-3.5-turbo"
max_tokens = 170
n = 1
stop = None
temperature = 0.5

def stream_gpt_response(prompt, context):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": context},
                      {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            temperature=temperature,
            stream=True
        )
        for line in response:
            if 'delta' in line['choices'][0] and 'content' in line['choices'][0]['delta']:
                yield line['choices'][0]['delta']['content']
    except Exception as e:
        print(f"Error in stream_gpt_response: {e}")
        return "I'm sorry, but I couldn't complete your request. Please try again later."

def generate_gpt_response(prompt, context):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": context},
                      {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            temperature=temperature,
        )
        # print(response)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in generate_gpt_response: {e}")
        return "I'm sorry, but I couldn't complete your request. Please try again later."
