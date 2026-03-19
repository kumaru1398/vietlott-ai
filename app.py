from flask import Flask, render_template_string
import random
from collections import Counter, defaultdict

app = Flask(__name__)

# ===== DATA =====
raw_data = [
[12,26,28,43,50,54,52],[7,16,27,29,47,52,26],[12,28,36,40,53,55,54],
[3,26,31,39,47,54,20],[4,32,41,45,50,52,29],[14,16,35,38,43,51,37],
[7,13,27,29,43,50,25],[22,25,31,44,51,54,36],[1,7,10,21,44,51,46],
[5,8,18,30,39,54,51],[5,7,26,30,41,45,12],[1,27,30,43,45,46,48],
[8,17,19,31,32,46,26],[13,21,22,26,32,55,20],[3,5,13,15,29,46,1],
[7,13,16,25,26,55,9],[12,15,18,22,48,53,45],[10,11,14,17,49,53,4],
[11,15,22,32,34,54,28],[13,22,32,42,53,54,29],[14,24,25,30,35,53,18],
[2,20,21,29,36,50,5],[4,20,26,28,37,41,32],[14,21,23,25,46,48,54],
[13,21,31,34,48,55,27],[3,21,31,34,48,55,27],[3,12,25,51,52,55,43]
]

main_counter = Counter()
pair_counter = Counter()

for row in raw_data:
    nums = row[:6]
    for n in nums:
        main_counter[n] += 1
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            pair_counter[tuple(sorted((nums[i], nums[j])))] += 1

# ===== GENERATOR =====
def generate():
    nums = list(range(1,56))
    weights = [main_counter[n]+1 for n in nums]

    picked = sorted(set(random.choices(nums, weights=weights, k=10)))[:6]
    return picked

# ===== UI HTML (APP-LIKE) =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { background:#0d0d0d; color:white; font-family:sans-serif; text-align:center; }
.container { max-width:400px; margin:auto; }
.ball { display:inline-block; width:45px; height:45px; line-height:45px;
        border-radius:50%; margin:5px; font-weight:bold; }
.low { background:#3498db; }
.mid { background:#f1c40f; color:black; }
.high { background:#e74c3c; }
button { padding:15px; width:100%; margin-top:20px; font-size:18px; border:none; border-radius:10px; background:#2ecc71; }
</style>
</head>
<body>
<div class="container">
<h2>🎯 Vietlott AI Pro</h2>
<form method="post">
<button>QUAY SỐ</button>
</form>
{% for row in sets %}
<div>
{% for n in row %}
<span class="ball {{ 'low' if n<=20 else 'mid' if n<=40 else 'high' }}">{{n}}</span>
{% endfor %}
</div>
{% endfor %}
</div>
</body>
</html>
"""

@app.route('/', methods=['GET','POST'])
def home():
    sets = [generate() for _ in range(3)]
    return render_template_string(HTML, sets=sets)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
