from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import flask


model_dir = "../model/pretrained/Qwen3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_dir, trust_remote_code=True, torch_dtype=torch.float16, device_map="auto")
model.eval()
global_count = 0

def chat(messages, **kwargs):
    text = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.7
    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=4096,
            **kwargs
        )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0
    
    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    print(f"Messages: {messages}\nResponse: {content}\n\n")
    return content



app = flask.Flask(__name__)
@app.route('/chat', methods=['POST'])
def chat_api():
    global global_count
    global_count += 1
    if global_count % 100 == 0:
        torch.cuda.empty_cache()
    if global_count % 10000 == 0:
        exit(0)
    data = flask.request.json
    messages = data['messages']
    kwargs = data.get('kwargs', {})
    response = chat(messages, **kwargs)
    return {'response': response}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3334)