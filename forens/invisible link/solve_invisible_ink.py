from pathlib import Path
import re

path = Path('/Users/ridwankusumahani/tools_cyber/SCTF/forens/invisible_ink.txt')
text = path.read_text()
block = re.search(r'messages\.(.+?)\nHave a nice day!', text, re.S).group(1)

tokens = [''.join(block[i:i+3]) for i in range(0, len(block), 3)]
unique = sorted(set(tokens))
mapping = {unique[0]: '1', unique[1]: '0'}
bits = ''.join(mapping[token] for token in tokens)
flag = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8)).decode()

print('Unique tokens:', unique)
print('Bit mapping:', {repr(k): v for k, v in mapping.items()})
print('Token count:', len(tokens))
print('Bits:', bits)
print('Flag:', flag)
