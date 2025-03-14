"""
Given a file containing text. Complete using only default collections:
    1) Find 10 longest words consisting from largest amount of unique symbols
    2) Find rarest symbol for document
    3) Count every punctuation char
    4) Count every non ascii char
    5) Find most common non ascii char for document
"""
from typing import List
import chardet
import unicodedata


def get_longest_diverse_words(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
      text = file.read()

    words = text.split()
    uniq_words_coll = []

    for word in words:
      uniq = len(set(word))
      uniq_words_coll.append((word,uniq,len(word)))

    uniq_words_coll.sort(key=lambda x:(x[1], x[2]), reverse = True)
    return(uniq_words_coll[:10])


def get_rarest_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
      text = file.read()

    chars = {}

    for char in text:
      if char in chars:
        chars[char]+=1
      else:
        chars[char] = 1

    return min(chars, key=chars.get)

def count_punctuation_chars(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as file:
      text = file.read()

    punct = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    count = 0

    for char in text:
      if char in punct:
        count+=1
    return count


def count_non_ascii_chars(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as file:
      raw_text = file.read()
      text = raw_text.encode().decode("unicode_escape") 

    count = 0;

    for char in text:
      if ord(char) > 127:
        count+=1
    return count


def get_most_common_non_ascii_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
      raw_text = file.read()
      text = raw_text.encode().decode("unicode_escape") 

    chars = {}

    for char in text:
        if ord(char) > 127:
            if char in chars:
                chars[char] += 1
            else:
                chars[char] = 1

    if not chars:  
        return None  
    return max(chars, key=chars.get)  

file_path = 'data.txt'

print(get_longest_diverse_words(file_path))
print(get_rarest_char(file_path))
print(count_punctuation_chars(file_path))
print(count_non_ascii_chars(file_path))
print(get_most_common_non_ascii_char(file_path))
