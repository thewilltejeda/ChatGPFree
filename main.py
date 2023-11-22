from flask import Flask, render_template, request, stream_with_context
import queue
from random import randint
from ctransformers import AutoModelForCausalLM
from prompts import AssistantPrompt


USERNAME = "Will"
AI_NAME = "Robot"
model_path = "LLM_Models/mistral-7b-instruct-v0.1.Q2_K.gguf"
model_type = "mistral"
message_queue = queue.Queue()
history = []


app = Flask(__name__)

print("Model Loading...")
llm = AutoModelForCausalLM.from_pretrained(model_path, model_type=model_type)
llm("hi", max_new_tokens=2)
print("Model Loaded!")

def chat_response(user_input):
    max_new_tokens = 256
    repetition_penalty = 1.2
    temperature = .4
    top_k = 50
    stop_words = [f"{AI_NAME}:", f"{USERNAME}:", "</s>"]
    

    try:
        message_window = 15
        history_string = "\n".join(history[-message_window:])
        prompt = AssistantPrompt.format(user_input=user_input, history=history_string, ai_name=AI_NAME, username=USERNAME)

        message = ""
        for word in llm(prompt, stream=True, max_new_tokens=max_new_tokens, repetition_penalty=repetition_penalty, temperature= temperature, top_k = top_k, stop=stop_words):     
            message += word
            print(word)
            yield(word)

        history.append(f"{USERNAME}: {user_input}")
        history.append(f"{AI_NAME}: {message}")

    except Exception as e:
        response = f"Could not process response.\n\n{e}"
        print("Error: ", e)
        return response

@app.route("/")
def index():
    history.clear()
    return render_template("index.html", username=USERNAME, ai_name=AI_NAME)

@app.route("/chat_submit/", methods=["POST"])
def chat_input():
    user_input = request.form.get("user_input")
    if not user_input:
        ai_response = "Error: Please Enter a Valid Input"
        current_response_id = f"gptblock{randint(67, 999999)}"
        return render_template("ai_response.html", ai_name=AI_NAME, ai_response=ai_response, hx_swap=False, current_response_id=current_response_id )
    
    message_queue.put(user_input)

    return "Success", 204 

@app.route('/stream')
def stream():
    def message_stream():
        global new_conversation

        while True:
            # If a message is present in the queue, send it to the clients
            if not message_queue.empty():
                user_message = message_queue.get()

                current_response_id = f"gptblock{randint(67, 999999)}"

                hx_swap = False

                message = ""
            
                for word in chat_response(user_message):
                    try:
                        message += word.replace("\n", "<br>")

                        ai_message = f"<p><strong>{ AI_NAME }</strong> : { message }</p>"

                        res = f"""data: <li class="text-white p-4 m-2 shadow-md rounded bg-gray-800 text-sm" id="{ current_response_id }" {"hx-swap-oob='true'" if hx_swap else ""}>{ai_message}</li>\n\n"""

                        hx_swap = True

                        print(f"{USERNAME}: {user_message}")
                        print(res)

                        yield res
        
                    except Exception as e:
                        print(e)
                        return(e)
                    
    return app.response_class(stream_with_context(message_stream()), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, port=9898)



