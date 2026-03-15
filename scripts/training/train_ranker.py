from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import config
import torch
import os

df = pd.read_csv(
    os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv'),
    sep=';',
    encoding='utf-8'
)

train_df = df[df['quality_score'].notna()]

texts = train_df['full_text'].tolist()
scores = train_df['quality_score'].astype(float).tolist()

tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")
model = AutoModelForSequenceClassification.from_pretrained("cointegrated/rubert-tiny2", num_labels=1)

class SimpleDataset:
    def __init__(self, texts, scores, tokenizer):
        self.texts = texts
        self.scores = scores
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        inputs = self.tokenizer(text, truncation=True, padding='max_length', max_length=256, return_tensors='pt')
        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': torch.tensor(self.scores[idx], dtype=torch.float)
        }

dataset = SimpleDataset(texts, scores, tokenizer)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

model.train()
for epoch in range(3):
    total_loss = 0
    for i in range(0, len(texts), 8):
        batch_texts = texts[i:i + 8]
        batch_scores = scores[i:i + 8]

        inputs = tokenizer(batch_texts, truncation=True, padding=True, max_length=256, return_tensors='pt')
        labels = torch.tensor(batch_scores, dtype=torch.float)

        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(**inputs, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()

    print(f'Эпоха {epoch + 1}, Потери: {total_loss / (len(texts) / 8)}')

os.makedirs(os.path.join(config.PROJECT_ROOT, 'models', 'llm', 'ranker'), exist_ok=True)
model.save_pretrained(os.path.join(config.PROJECT_ROOT, 'models', 'llm', 'ranker'))
tokenizer.save_pretrained(os.path.join(config.PROJECT_ROOT, 'models', 'llm', 'ranker'))