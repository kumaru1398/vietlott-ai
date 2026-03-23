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
def monte_carlo_generate(history, simulations=500):
    scores, pairs = score_numbers(history)

    results = []

    for _ in range(simulations):
        s = smart_pick(scores, pairs)

        fitness = sum(scores[n] for n in s)

        pair_bonus = 0
        for i in range(len(s)):
            for j in range(i+1,len(s)):
                pair_bonus += pairs.get(tuple(sorted((s[i],s[j]))),0)

        fitness += pair_bonus * 2

        results.append((tuple(sorted(s)), fitness))  # 👈 dùng tuple để loại trùng

    # ===== REMOVE DUPLICATE =====
    unique = {}
    for s, f in results:
        if s not in unique or f > unique[s]:
            unique[s] = f

    # ===== SORT =====
    sorted_sets = sorted(unique.items(), key=lambda x: x[1], reverse=True)

    # ===== LẤY 2 BỘ KHÁC NHAU =====
    set1 = list(sorted_sets[0][0])

    set2 = None
    for s, _ in sorted_sets[1:]:
        if len(set(s) & set(set1)) < 4:  # 👈 không trùng quá nhiều
            set2 = list(s)
            break

    # fallback nếu không tìm được
    if not set2:
        set2 = list(sorted_sets[1][0])

    return [set1, set2]

# ===== API =====
@app.route('/api')
def api():
    history = update_history()

    if len(history) < 10:
        nums = sorted(random.sample(range(1,56),6))
        return jsonify({
            "set1": nums,
            "set2": nums
        })

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
body {
  background: radial-gradient(circle, #0f2027, #203a43, #2c5364);
  color: white;
  text-align: center;
  font-family: sans-serif;
}

h2 {
  margin-top: 20px;
}

.container {
  margin-top: 30px;
}

.ball {
  display:inline-block;
  width:60px;
  height:60px;
  line-height:60px;
  border-radius:50%;
  margin:8px;
  font-weight:bold;
  font-size:20px;
  background:#222;
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
  transition: all 0.3s ease;
}

.low { background:#6ec6ff; }
.mid { background:#ffd166; color:black; }
.high { background:#ff6b6b; }

.spin {
  animation: spin 0.2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg) scale(1.1); }
  50% { transform: rotate(180deg) scale(1.2); }
  100% { transform: rotate(360deg) scale(1.1); }
}

.glow {
  box-shadow: 0 0 20px #fff, 0 0 40px #0ff;
}

button {
  padding:15px;
  width:80%;
  font-size:18px;
  border:none;
  border-radius:12px;
  background: linear-gradient(45deg, #00c9ff, #92fe9d);
  color:black;
  margin-top:30px;
}
</style>
</head>

<body>

<h2>🎰 Vietlott Casino</h2>

<div class="container" id="set1"></div>
<div class="container" id="set2"></div>

<button onclick="run()">🎲 SPIN NOW</button>

<script>
function color(n){
 if(n<=18) return 'low';
 if(n<=36) return 'mid';
 return 'high';
}

function createBalls(id){
 let el = document.getElementById(id);
 el.innerHTML = "";
 let balls = [];

 for(let i=0;i<6;i++){
   let b = document.createElement('div');
   b.className = 'ball spin';
   b.innerText = Math.floor(Math.random()*55)+1;
   el.appendChild(b);
   balls.push(b);
 }
 return balls;
}

function animateResult(balls, nums){
 if(!nums) return;

 nums.forEach((num, i)=>{
   setTimeout(()=>{
     let b = balls[i];
     b.classList.remove('spin');
     b.innerText = num;
     b.className = 'ball ' + color(num) + ' glow';
   }, i * 400);
 });
}

function run(){
 let balls1 = createBalls('set1');
 let balls2 = createBalls('set2');

 fetch('/api')
 .then(r=>r.json())
 .then(d=>{
   console.log("API DATA:", d);

   if(!d.set1 || !d.set2){
     alert("API lỗi hoặc chưa có dữ liệu!");
     return;
   }

   setTimeout(()=>{
     animateResult(balls1, d.set1);
     animateResult(balls2, d.set2);
   }, 1500);
 })
 .catch(err=>{
   console.error(err);
   alert("Không gọi được API!");
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
