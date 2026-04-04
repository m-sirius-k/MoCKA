import docx
src = r'C:\Users\sirok\Desktop\KARUMANNRYUU.docx'
dst = r'C:\Users\sirok\MoCKA\experiments\karumannryuu.txt'
doc = docx.Document(src)
text = '\n'.join([p.text for p in doc.paragraphs])
with open(dst, 'w', encoding='utf-8') as f:
    f.write(text)
print('OK: ' + str(len(text)) + ' chars')
print(text[:200])
