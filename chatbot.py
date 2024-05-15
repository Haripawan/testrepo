import tensorflow as tf
from transformers import TFBertTokenizer, TFBertForQuestionAnswering

# Load pre-trained BERT model and tokenizer
tokenizer = TFBertTokenizer.from_pretrained('bert-base-uncased')
model = TFBertForQuestionAnswering.from_pretrained('bert-base-uncased')

# Define your context and question
context = "This is a sample sentence to demonstrate context extraction using BERT."
question = "What is the context about?"

# Tokenize the inputs
tokenized_context = tokenizer.encode(context, add_special_tokens=True, return_tensors='tf')

# Use the model to predict start and end logits for the answer
outputs = model(tokenized_context)
start_logits, end_logits = outputs.start_logits, outputs.end_logits

# Predict the answer span based on logits
predicted_start = tf.argmax(start_logits, axis=-1).numpy()[0]
predicted_end = tf.argmax(end_logits, axis=-1).numpy()[0]

# Extract the answer from the context
answer = context[predicted_start:predicted_end+1]

print("Answer:", answer)
