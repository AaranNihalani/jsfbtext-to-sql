import json
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import torch

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder-7b-2")
model = AutoModelForCausalLM.from_pretrained("defog/sqlcoder-7b-2")

# Load the training data
with open("training_data.json", "r") as f:
    training_data = json.load(f)

# Prepare the dataset
class SQLDataset(torch.utils.data.Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        question = item["question"]
        query = item["query"]
        
        # Format the input and output for the model
        input_text = f"### Task\nGenerate a SQL query to answer the following question.\n\n### Question\n{question}\n\n### Answer\n{query}"
        
        # Tokenize the input and output
        encoding = self.tokenizer(input_text, truncation=True, padding="max_length", max_length=512, return_tensors="pt")
        
        return {"input_ids": encoding["input_ids"].squeeze(), "attention_mask": encoding["attention_mask"].squeeze()}

train_dataset = SQLDataset(training_data, tokenizer)

# Set up the training arguments
training_args = TrainingArguments(
    output_dir="./sqlcoder-fine-tuned",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
)

# Create the trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# Train the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./sqlcoder-fine-tuned")
tokenizer.save_pretrained("./sqlcoder-fine-tuned")