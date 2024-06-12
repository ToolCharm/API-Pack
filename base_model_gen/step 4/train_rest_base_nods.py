print("START OF CODE")
import transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration, TrainingArguments, Trainer, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer#, ORTSeq2SeqTrainer
from transformers.integrations import MLflowCallback
import evaluate # must install this on azure ml
import torch
import pandas as pd
from tqdm import tqdm
from huggingface_hub import login
import argparse
import datasets
from datasets import Dataset
import os
from transformers.pipelines.pt_utils import KeyDataset
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import numpy as np
import re
import validators
import json
import wandb
print("END OF IMPORTS")

wandb.login(key="932a31ddca8fc928ffb0817d8391c3d7be89518e")
os.environ['WANDB_LOG_MODEL'] = "True"

parser = argparse.ArgumentParser()
parser.add_argument('--output_dir', type=str, required=True)
args = parser.parse_args()

df = pd.read_csv("rest_base_model_dataset_tokenized_endpoints_allpayload.csv")

# train test split
dataset = Dataset.from_pandas(df)
dataset_split = dataset.train_test_split(test_size=0.2)
dataset_split['validation'] = dataset_split.pop('test')

print("END OF DS IMPORT")

model_id = "google/flan-t5-large"
model_save_dir = "/dev/shm/models"

tokenizer: transformers.PreTrainedTokenizer = T5Tokenizer.from_pretrained(model_id)
model = T5ForConditionalGeneration.from_pretrained(model_id, 
                                                   device_map="auto", 
                                                   use_cache=False)
tokenizer.add_tokens(["<GET>","<POST>", "<PUT>", "<DELETE>", "<PATCH>",
                                  "<ENDPOINTSTART>", "<ENDPOINTEND>",
                                  "<PAYLOADSTART>", "<PAYLOADEND>",
                                  "{","}",])

print("END OF MODEL_LOADING")

def tokenize_function(examples):
    prefixed_instructions = [f"translate: English to API call: {instruction}" for instruction in examples['instructions']]
    tokenized_examples = tokenizer(prefixed_instructions, text_target=examples['api_calls'], max_length=8192, truncation=True)
    
    filtered_examples = {
        "input_ids": [],
        "attention_mask": [],
        "labels": []
    }

    for record in zip(tokenized_examples["input_ids"], tokenized_examples["attention_mask"], tokenized_examples["labels"]):
        input_id, attn_mask, label = record
        if len(label) <= 2048 and len(input_id) < 2048:
            filtered_examples['input_ids'].append(input_id)
            filtered_examples['attention_mask'].append(attn_mask)
            filtered_examples['labels'].append(label)

    return filtered_examples
dataset_tokenized = dataset_split.map(tokenize_function, batched=True, remove_columns=dataset_split['train'].column_names)

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

metric = evaluate.load("sacrebleu")

def decompose_api_requests(requests):
    methods = [
        [*re.findall(r'<GET>|<POST>|<PUT>|<PATCH>|<DELETE>', apicall), "NONE"][0]
        for apicall in requests
    ]
    urls = [
        [*re.findall(r'<ENDPOINTSTART>(.*)<ENDPOINTEND>', apicall), "NONE"][0].strip()
        for apicall in requests
    ]
    payloads = [
        [*re.findall(r'<PAYLOADSTART>(.*)<PAYLOADEND>', apicall), "NONE"][0].strip()
        for apicall in requests
    ]
    return methods, urls, payloads

def check_payload_validity(payload, ground_truth):
    if ground_truth == payload:
        return 1
    
    try:
        json.loads(payload)
        return 1
    except:
        return 0

def compute_metrics(eval_preds):
    preds, labels = eval_preds

    if isinstance(preds, tuple):
        preds = preds[0]

    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    # Replace -100s in the labels as we can't decode them
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Some simple post-processing
    decoded_preds = [pred.strip() for pred in decoded_preds]
    decoded_labels = [label.strip() for label in decoded_labels]
    decoded_labels_encased = [[label.strip()] for label in decoded_labels]

    pred_methods, pred_urls, pred_payloads = decompose_api_requests(decoded_preds)
    label_methods, label_urls, label_payloads = decompose_api_requests(decoded_labels)

    method_score = np.mean(np.array([1 if pred == label else 0 for pred, label in zip(pred_methods, label_methods)]))
    url_score = np.mean(np.array([1 if validators.url(f"https://example.com{endpoint}") else 0 for endpoint in pred_urls]))
    payload_score = np.mean(np.array([check_payload_validity(payload, ground_truth) for payload, ground_truth in zip(pred_payloads, label_payloads)]))
    bleu_score = metric.compute(predictions=decoded_preds, references=decoded_labels_encased)

    return {"method_acc": method_score,
            "url_validity": url_score,
            "payload_validity": payload_score,
            "bleu": bleu_score['score']}

max_len = 0
for item in dataset_tokenized['validation']:
    item_length = len(item['input_ids']) + len(item['labels'])
    if item_length > max_len:
        max_len = item_length

max_len += 50 # just to be safe

train_args = Seq2SeqTrainingArguments(
    output_dir=args.output_dir,
    overwrite_output_dir=True,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_steps = 1,
    learning_rate=2e-5,
    auto_find_batch_size=True,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,
    predict_with_generate=True,
    fp16=False,
    bf16=True,
    push_to_hub=False,
    report_to="wandb"
)

trainer = Seq2SeqTrainer(
    model,
    train_args,
    train_dataset=dataset_tokenized["train"],
    eval_dataset=dataset_tokenized["validation"],
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.callback_handler.remove_callback(MLflowCallback)

trainer.train()