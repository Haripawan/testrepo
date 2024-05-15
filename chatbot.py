oimport tensorflow as tf
from transformers import TFBertTokenizer, TFBertForQuestionAnswering

# Load pre-trained BERT model and tokenizer
tokenizer = TFBertTokenizer.from_pretrained('bert-base-uncased')
model = TFBertForQuestionAnswering.from_pretrained('bert-base-uncased')

# Define your context and question
context = "This is a sample sentence to demonstrate context extraction usig BERT."
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



####processing docs######



import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize the lemmatizer and stop words
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_document(doc):
    # Tokenize the document
    tokens = nltk.word_tokenize(doc)
    
    # Convert to lower case
    tokens = [word.lower() for word in tokens]
    
    # Remove punctuation from each word
    table = str.maketrans('', '', string.punctuation)
    stripped = [word.translate(table) for word in tokens]
    
    # Remove remaining tokens that are not alphabetic
    words = [word for word in stripped if word.isalpha()]
    
    # Filter out stop words
    words = [word for word in words if not word in stop_words]
    
    # Lemmatize words
    lemmatized = [lemmatizer.lemmatize(word) for word in words]
    
    return lemmatized

# Example document (list of strings)
docs = [
    "Cats are playing in the garden",
    "A man is walking his dog in the park",
    "The new movie is a thrilling adventure"
]

# Preprocess each document
processed_docs = [preprocess_document(doc) for doc in docs]

print(processed_docs)



##### preprocessy######


import spacy

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Function to preprocess documents
def preprocess_docs(doc):
    # Parse the document with spaCy
    parsed_doc = nlp(doc)
    
    # Tokenize and process the text
    tokens = [token.lemma_.lower() for token in parsed_doc if not token.is_stop and not token.is_punct and not token.is_space]
    
    return tokens

# Example list of documents
docs = [
    "Cats are playing in the garden.",
    "A man is walking his dog in the park.",
    "The new movie is a thrilling adventure."
]

# Preprocess each document
processed_docs = [preprocess_docs(doc) for doc in docs]

print(processed_docs)

