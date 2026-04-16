import csv
import os
import json

CSV_PATH = "runtime/record/event_log.csv"
DOC_PATH = "docs/incidents"

def search_csv(keyword):
    results = []

    if not os.path.exists(CSV_PATH):
        return results

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if keyword in row["summary"]:
                results.append(row)

    return results

def search_docs(keyword):
    results = []

    if not os.path.exists(DOC_PATH):
        return results

    for file in os.listdir(DOC_PATH):
        if file.endswith(".json"):
            path = os.path.join(DOC_PATH, file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                text = json.dumps(data, ensure_ascii=False)

                if keyword in text:
                    results.append({
                        "file": file,
                        "content": data
                    })

    return results

def unified_search(keyword):
    return {
        "csv_hits": search_csv(keyword),
        "doc_hits": search_docs(keyword)
    }

if __name__ == "__main__":
    keyword = "CSV再生成"

    result = unified_search(keyword)

    print("RESULT:", result)
