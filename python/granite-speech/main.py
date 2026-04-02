import torch
import torchaudio
from huggingface_hub import hf_hub_download
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

device = "cuda" if torch.cuda.is_available() else "cpu"

model_name = "ibm-granite/granite-4.0-1b-speech"
processor = AutoProcessor.from_pretrained(model_name)
tokenizer = processor.tokenizer
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_name, device_map=device, torch_dtype=torch.bfloat16
)

file_name = "sample.wav"

wav, sr = torchaudio.load(file_name, normalize=True)
assert wav.shape[0] == 1 and sr == 16000  # mono, 16kHz

# Create text prompt
user_prompt = "<|audio|>can you transcribe the speech into a written format?"
chat = [
    {"role": "user", "content": user_prompt},
]
prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

# Run the processor + model
model_inputs = processor(prompt, wav, device=device, return_tensors="pt").to(device)
model_outputs = model.generate(
    **model_inputs, max_new_tokens=200, do_sample=False, num_beams=1
)

# Transformers includes the input IDs in the response
num_input_tokens = model_inputs["input_ids"].shape[-1]
new_tokens = model_outputs[0, num_input_tokens:].unsqueeze(0)
output_text = tokenizer.batch_decode(
    new_tokens, add_special_tokens=False, skip_special_tokens=True
)
print(f"STT output = {output_text[0]}")
