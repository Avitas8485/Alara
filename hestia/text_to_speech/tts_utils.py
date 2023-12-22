import nltk
from transformers import T5Tokenizer, T5ForConditionalGeneration


nltk.download('punkt', quiet=True)
model = T5ForConditionalGeneration.from_pretrained('google/flan-t5-base')
tokenizer = T5Tokenizer.from_pretrained('google/flan-t5-base')

def count_tokens(text):
    tokens = nltk.word_tokenize(text)
    return len(tokens)


