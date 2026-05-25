import json
from collections import Counter
d = json.load(open('/Users/cosmic/Documents/funni/ib-maths-bank/recon/pestle_aa.json'))
print("total:", len(d))

sub = Counter()
for x in d:
    for s in x.get('subtopics', []) or []:
        sub[s] += 1
print(f"\nunique subtopics: {len(sub)}")
print("top 30 subtopics:")
for k, v in sub.most_common(30):
    print(f"  {v:5d}  {k}")

# check question_id format — to extract paper/year/level
ids = [x.get('question_id') for x in d[:30]]
print("\nfirst 30 question_ids:")
for i in ids:
    print(" ", i)
