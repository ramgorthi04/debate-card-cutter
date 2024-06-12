import re

def split_string(text):
    # Regular expression pattern to match words, spaces, punctuation, numbers, and paragraph breaks
    pattern = r'\w+|[^\w\s]|\s+|\n\n+'
    
    # Split the text according to the pattern
    elements = re.findall(pattern, text)
    
    return elements

# Example usage
text = """This is the first sentence.

This is the second sentence!"""
elements = split_string(text)
print(elements)
