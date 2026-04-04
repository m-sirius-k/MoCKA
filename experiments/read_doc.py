import docx
src = r'G:\現在担当物件など\常松スピンフロー\15 認定申請関連\一般説明資料とプレゼン資料\スピン一般説明資料　07年2月22日\00 スピンフロー(19.2.22)一般Ａ.docx'
dst = r'C:\Users\sirok\MoCKA\experiments\plant_doc_A.txt'
doc = docx.Document(src)
text = '\n'.join([p.text for p in doc.paragraphs])
with open(dst, 'w', encoding='utf-8') as f:
    f.write(text)
print('OK: ' + str(len(text)) + ' chars')
print(text[:300])
