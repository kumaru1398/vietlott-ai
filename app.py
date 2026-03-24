from flask import Flask, render_template_string, jsonify
import random, math, os
from collections import Counter
import requests

app = Flask(__name__)

# ===== ICON ROUTE =====
from flask import send_from_directory
@app.route('/icon.png')
def icon():
    return send_from_directory('static', 'icon.png')

# ===== SIMPLE GENERATOR (KEEP STABLE) =====
def generate():
    set1 = sorted(random.sample(range(1,56),6))
    remaining = [n for n in range(1,56) if n not in set1]
    set2 = sorted(random.sample(remaining,6))
    return [set1, set2]

# ===== API =====
@app.route('/api')
def api():
    return jsonify({"numbers": generate()})

# ===== SLOT MACHINE UI =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="apple-touch-icon" href="/icon.png">

<style>
body {
  background: black;
  color: white;
  text-align: center;
  font-family: sans-serif;
}

h2 { margin-top:20px; }

.slot {
  display:flex;
  justify-content:center;
  margin:10px;
}

.reel {
  width:60px;
  height:60px;
  overflow:hidden;
  border-radius:50%;
  margin:6px;
  background:#111;
  border:2px solid #333;
}

.inner {
  display:flex;
  flex-direction:column;
  animation: spin 0.1s linear infinite;
}

.ball {
  width:60px;
  height:60px;
  line-height:60px;
  text-align:center;
  font-weight:bold;
}

@keyframes spin {
  0% { transform: translateY(0); }
  100% { transform: translateY(-60px); }
}

.stop {
  animation:none !important;
}

button {
  padding:15px;
  width:80%;
  font-size:18px;
  border:none;
  border-radius:10px;
  background:#00ffcc;
  margin-top:20px;
}
</style>
</head>

<body>
<h2>🎰 SLOT VIETLOTT</h2>

<div id="set1" class="slot"></div>
<div id="set2" class="slot"></div>

<button onclick="run()">SPIN</button>

<script>

function createReels(id){
  let container = document.getElementById(id);
  container.innerHTML = '';

  let reels = [];

  for(let i=0;i<6;i++){
    let reel = document.createElement('div');
    reel.className = 'reel';

    let inner = document.createElement('div');
    inner.className = 'inner';

    for(let j=0;j<20;j++){
      let num = document.createElement('div');
      num.className = 'ball';
      num.innerText = Math.floor(Math.random()*55)+1;
      inner.appendChild(num);
    }

    reel.appendChild(inner);
    container.appendChild(reel);
    reels.push(inner);
  }

  return reels;
}

function stopReels(reels, numbers){
  numbers.forEach((num, i)=>{
    setTimeout(()=>{
      let r = reels[i];
      r.classList.add('stop');
      r.innerHTML = '<div class="ball">'+num+'</div>';
    }, i*500);
  });
}

function run(){
  let reels1 = createReels('set1');
  let reels2 = createReels('set2');

  fetch('/api')
  .then(res=>res.json())
  .then(data=>{
    stopReels(reels1, data.numbers[0]);
    stopReels(reels2, data.numbers[1]);
  });
}

</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
