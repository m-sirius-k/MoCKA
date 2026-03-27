import json

LEDGER=r"runtime\main\ledger.json"

def load():
    with open(LEDGER,"r",encoding="utf-8") as f:
        return json.load(f)

def diff(local,remote):

    lset=set([e["event_hash"] for e in local])
    rset=set([e["event_hash"] for e in remote])

    missing=lset-rset
    extra=rset-lset

    return missing,extra

def main():

    local=load()

    try:
        with open(r"runtime\remote_ledger.json","r",encoding="utf-8") as f:
            remote=json.load(f)
    except:
        print("REMOTE LEDGER NOT FOUND")
        return

    m,e=diff(local,remote)

    print("LOCAL EVENTS NOT IN REMOTE",len(m))
    print("REMOTE EVENTS NOT IN LOCAL",len(e))

if __name__=="__main__":
    main()
