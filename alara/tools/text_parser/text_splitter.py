from typing import Any, Generator
from nltk.tokenize import sent_tokenize

def split_text(text: str, max_length: int=4000) -> Generator[str, None, None]: 
    chunks =  sent_tokenize(text)
    current_length = 0
    current_chunk = []
    for chunk in chunks:
        if current_length + len(chunk) + 1 <= max_length:
            current_chunk.append(chunk)
            current_length += len(chunk) + 1
        else:
            yield " ".join(current_chunk)
            current_chunk = [chunk]
            current_length = len(chunk) + 1
    if current_chunk:
        yield " ".join(current_chunk)
            

if __name__ == "__main__":
    text = """It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.
    The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.
    A lot of desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy.
    lorem ipsum is a dummy text used in the printing and typesetting industry."""
    chunks = split_text(text)   
    print(list(chunks))