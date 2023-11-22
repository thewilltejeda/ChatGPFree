import os
from ctransformers import AutoModelForCausalLM


USERNAME = "Will"
AI_NAME = "Robot"
model_path = "LLM_Models/mistral-7b-instruct-v0.1.Q2_K.gguf"
model_type = "mistral"


llm = AutoModelForCausalLM.from_pretrained(model_path, model_type=model_type)

os.system("clear")  
convo = []

settings = {
    "max_new_tokens": 256,
    "repetition_penalty": 1.2,
    "temperature": .4,
    "top_k": 30,
    "stop_words": [f"{AI_NAME}:", f"{USERNAME}:", "</s>"]
}

while True:
    user_input = input(f"\{USERNAME}: ")
    convo.append(f"{USERNAME}: {user_input}\n")

    message = f"{AI_NAME}: "
    for word in llm(user_input, **settings):
        message += word

        os.system("clear")  
        print("\n".join(convo))
        print(message)

    convo.append(message + "\n")