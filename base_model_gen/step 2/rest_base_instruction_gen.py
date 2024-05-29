import transformers
import torch
import pandas as pd
from tqdm import tqdm
from huggingface_hub import login
import argparse
import datasets
from datasets import Dataset
import os
from transformers.pipelines.pt_utils import KeyDataset

parser = argparse.ArgumentParser()
parser.add_argument('--output_dir', type=str, required=True)
args = parser.parse_args()

login(token="")

model_id = "meta-llama/Meta-Llama-3-70B"
model_save_dir = "/dev/shm/models"

pipeline = transformers.pipeline(
    "text-generation", 
    model=model_id, 
    model_kwargs={"torch_dtype": torch.bfloat16, "cache_dir": model_save_dir}, 
    device_map="auto"
)

pipeline.tokenizer.pad_token_id = pipeline.model.config.eos_token_id
pipeline.tokenizer.padding_side = "left"

def token_length(text):
    return pipeline.tokenizer(text, return_tensors='pt')['input_ids'].shape[1]

output_dir = args.output_dir
print("output_directory: " + str(output_dir))
# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv("combined_raw_rest_base.csv")
df = df.sort_values(by='api_call', key=lambda x: x.map(token_length))
df_len = len(df)  # Define df_len

df["model_input"] = df["api_call"].apply(lambda x: f"""Boss: <verbal instruction>
Worker: Ok, I will do that by running this curl command `{x}`

What is the instruction that could replace the placeholder <verbal instruction>? 
Hint: the Boss is asking the Worker to achieve something by running a curl command, not asking for a curl command
A: The instruction the boss gave was \"""")

dataset = Dataset.from_pandas(df)
temp_dataset = {"instructions": [], "api_calls": []}
call_key = 0
shard_count = 134

for output in tqdm(pipeline(KeyDataset(dataset, key="model_input"), batch_size=10, max_new_tokens=100)):
    output = [out['generated_text'].split("A: The instruction the boss gave was \"")[1].split("\"")[0] for out in output]
    temp_dataset["instructions"].extend(output)
    temp_dataset["api_calls"].extend(df["api_call"].iloc[call_key:call_key+len(output)])
    call_key += len(output)

    if len(temp_dataset["instructions"]) >= 100:
        print("Writing shard " + str(shard_count))
        temp_df = pd.DataFrame(temp_dataset)
        temp_df.to_csv(os.path.join(output_dir, f"shard_{shard_count}.csv"), index=False)
        temp_dataset = {"instructions": [], "api_calls": []}
        shard_count += 1

if len(temp_dataset["instructions"]) > 0:
    temp_df = pd.DataFrame(temp_dataset)
    temp_df.to_csv(os.path.join(output_dir, f"shard_{shard_count}.csv"), index=False)