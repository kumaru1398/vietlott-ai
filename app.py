from flask import Flask, render_template_string, jsonify, send_from_directory
import random, os

app = Flask(__name__)

# ===== ICON =====
@app.route('/icon.png')
def icon():
    return send_from_directory('static', 'icon.png')

# ===== GENERATOR (NO OVERLAP) =====
def generate():
    set1 = sorted(random.sample(range(1,56),6))
    remaining = [n for n in range(1,56) if n not in set1]
    set2 = sorted(random.sample(remaining,6))
    return [set1, set2]

@app.route('/api')
def api():
    return jsonify({"numbers": generate()})

# ===== PRO CASINO UI =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="apple-touch-icon" href="/icon.png">

<style>
body {
  background: radial-gradient(circle, #000000, #0f2027);
  color: white;
  text-align: center;
  font-family: sans-serif;
}

h2 {
  margin-top:20px;
  text-shadow: 0 0 10px #0ff;
}

.slot { display:flex; justify-content:center; margin:10px; }

.reel {
  width:65px;
  height:65px;
  overflow:hidden;
  border-radius:50%;
  margin:6px;
  background:#111;
  border:2px solid #0ff;
  box-shadow: 0 0 10px #0ff;
}

.inner {
  display:flex;
  flex-direction:column;
  animation: spin 0.08s linear infinite;
}

.ball {
  width:65px;
  height:65px;
  line-height:65px;
  font-weight:bold;
  font-size:20px;
}

@keyframes spin {
  0% { transform: translateY(0); }
  100% { transform: translateY(-65px); }
}

.stop { animation:none !important; }

.win {
  animation: glow 0.5s infinite alternate;
}

@keyframes glow {
  from { box-shadow:0 0 10px #fff; }
  to { box-shadow:0 0 25px #0ff; }
}

button {
  padding:15px;
  width:80%;
  font-size:18px;
  border:none;
  border-radius:12px;
  background: linear-gradient(45deg, #00c9ff, #92fe9d);
  color:black;
  margin-top:20px;
}

</style>
</head>

<body>
<h2>🎰 CASINO 2.0</h2>

<div id="set1" class="slot"></div>
<div id="set2" class="slot"></div>

<button onclick="run()">🎲 SPIN NOW</button>

<audio id="tick" src="https://www.soundjay.com/machine/slot-machine-1.mp3"></audio>
<audio id="win" src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"></audio>

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
  let tick = document.getElementById('tick');
  let win = document.getElementById('win');

  numbers.forEach((num, i)=>{
    setTimeout(()=>{
      tick.currentTime = 0;
      tick.play();

      let r = reels[i];
      r.classList.add('stop');
      r.innerHTML = '<div class="ball">'+num+'</div>';

      if(i === numbers.length-1){
        setTimeout(()=>{
          win.play();
          r.parentElement.classList.add('win');
        },300);
      }

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
