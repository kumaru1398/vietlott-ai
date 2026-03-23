from flask import Flask, render_template_string, jsonify
import random, math, os
from collections import Counter
import requests

app = Flask(__name__)

# ===== ICON ROUTE (GIỮ NGUYÊN) =====
from flask import send_from_directory
@app.route('/icon.png')
def icon():
    return send_from_directory('static', 'icon.png')

# ===== FETCH REAL DATA =====
def fetch_vietlott():
    try:
        url = "https://api.xoso.me/vietlott/655"
        res = requests.get(url, timeout=5)
        data = res.json()

        results = []
        for draw in data.get("data", []):
            nums = list(map(int, draw["result"].split("-")))
            results.append(nums)

        return results
    except:
        return []

# ===== HISTORY =====
def load_history():
    try:
        with open("history.txt", "r") as f:
            return [list(map(int, l.strip().split(","))) for l in f if l.strip()]
    except:
        return []

def save_history(data):
    with open("history.txt", "w") as f:
        for row in data:
            f.write(",".join(map(str,row)) + "\n")

def update_history():
    new = fetch_vietlott()
    old = load_history()

    for draw in new:
        if draw not in old:
            old.append(draw)

    save_history(old)
    return old

# ===== ANALYSIS =====
def frequency_analysis(history):
    freq = Counter()
    for d in history:
        freq.update(d)
    return freq

def pair_analysis(history):
    pairs = Counter()
    for d in history:
        for i in range(len(d)):
            for j in range(i+1,len(d)):
                pairs[tuple(sorted((d[i],d[j])))] += 1
    return pairs

def cycle_analysis(history):
    last, cycles = {}, {}
    for i,d in enumerate(history):
        for n in d:
            if n in last:
                cycles.setdefault(n, []).append(i-last[n])
            last[n] = i
    avg = {n: sum(g)/len(g) for n,g in cycles.items() if g}
    return avg, last

def score_numbers(history):
    freq = frequency_analysis(history)
    pairs = pair_analysis(history)
    avg_cycle, last_seen = cycle_analysis(history)

    total = len(history)
    scores = {}

    for n in range(1,56):
        hot = freq.get(n,0)
        cold = total - last_seen.get(n,0)
        cycle = avg_cycle.get(n,10)

        scores[n] = hot*2 + cold*0.5 + cycle*1.5

    return scores, pairs

# ===== DIVERSITY =====
def enforce_diversity(nums):
    nums = sorted(set(nums))

    low = [n for n in nums if n<=18]
    high = [n for n in nums if n>36]

    while len(low)<2:
        low.append(random.randint(1,18))
    while len(high)<2:
        high.append(random.randint(37,55))

    result = list(set(nums + low + high))

    while len(result)<6:
        result.append(random.randint(1,55))

    return sorted(result[:6])

# ===== SMART PICK =====
def smart_pick(scores, pairs):
    nums = list(range(1,56))
    base = [scores[n] for n in nums]

    exp = [math.exp(s/10) for s in base]
    probs = [e/sum(exp) for e in exp]

    selected = [random.choices(nums, weights=probs, k=1)[0]]

    while len(selected)<6:
        weights = []
        for n in nums:
            boost = sum(pairs.get(tuple(sorted((n,s))),0)*2 for s in selected)
            weights.append(scores[n]+boost)

        exp_w = [math.exp(w/10) for w in weights]
        probs_w = [w/sum(exp_w) for w in exp_w]

        pick = random.choices(nums, weights=probs_w, k=1)[0]
        if pick not in selected:
            selected.append(pick)

    return enforce_diversity(selected)

# ===== MONTE CARLO =====
def monte_carlo_generate(history, simulations=300):
    scores, pairs = score_numbers(history)

    best_sets = []

    for _ in range(simulations):
        s = smart_pick(scores, pairs)

        # fitness = tổng score + pair strength
        fitness = sum(scores[n] for n in s)

        pair_bonus = 0
        for i in range(len(s)):
            for j in range(i+1,len(s)):
                pair_bonus += pairs.get(tuple(sorted((s[i],s[j]))),0)

        fitness += pair_bonus * 2

        best_sets.append((s, fitness))

    best_sets.sort(key=lambda x: x[1], reverse=True)

    return [best_sets[0][0], best_sets[1][0]]

# ===== API =====
@app.route('/api')
def api():
    history = update_history()

    if len(history)<10:
        nums = sorted(random.sample(range(1,56),6))
        return jsonify({"numbers": nums})

    top_sets = monte_carlo_generate(history)

    return jsonify({
        "set1": top_sets[0],
        "set2": top_sets[1]
    })

# ===== UI =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="apple-touch-icon" href="/icon.png">
<style>
body { background:#0d0d0d; color:white; text-align:center; font-family:sans-serif;}
.ball {display:inline-block;width:50px;height:50px;line-height:50px;
border-radius:50%;margin:5px;font-weight:bold}
.low{background:#6ec6ff}.mid{background:#ffd166;color:black}.high{background:#ff6b6b}
button{padding:15px;width:80%;font-size:18px;border-radius:10px;background:#2ecc71}
</style>
</head>
<body>
<h2>🎯 Vietlott AI PRO</h2>
<div id="set1"></div>
<div id="set2"></div>
<button onclick="run()">QUAY SIÊU AI</button>

<script>
function color(n){
 if(n<=18) return 'low';
 if(n<=36) return 'mid';
 return 'high';
}

function render(id, nums){
 let el = document.getElementById(id);
 el.innerHTML="";
 nums.forEach(n=>{
  let b=document.createElement('span');
  b.className='ball '+color(n);
  b.innerText=n;
  el.appendChild(b);
 });
}

function run(){
 fetch('/api')
 .then(r=>r.json())
 .then(d=>{
  render('set1', d.set1);
  render('set2', d.set2);
 });
}
</script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(HTML)

from flask import jsonify

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
