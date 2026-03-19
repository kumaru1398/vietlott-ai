from flask import Flask, render_template_string
import random

app = Flask(__name__)

# ===== GENERATOR =====
def generate():
    nums = random.sample(range(1,56),6)
    return sorted(nums)

# ===== UI WITH ANIMATION =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { background:#0d0d0d; color:white; font-family:sans-serif; text-align:center; }
.container { max-width:400px; margin:auto; }
.ball { display:inline-block; width:50px; height:50px; line-height:50px;
        border-radius:50%; margin:6px; font-weight:bold; font-size:18px;
        transition: transform 0.3s, background 0.3s; }
.low { background:#3498db; }
.mid { background:#f1c40f; color:black; }
.high { background:#e74c3c; }
button { padding:15px; width:100%; margin-top:20px; font-size:18px; border:none; border-radius:10px; background:#2ecc71; }

.spin { animation: spin 0.5s linear infinite; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
</head>
<body>
<div class="container">
<h2>🎯 Vietlott AI Animation</h2>

<div id="result"></div>

<button onclick="spinNumbers()">QUAY SỐ</button>
</div>

<script>
function getColor(n){
  if(n<=20) return 'low';
  if(n<=40) return 'mid';
  return 'high';
}

function spinNumbers(){
  let container = document.getElementById('result');
  container.innerHTML = '';

  let balls = [];

  for(let i=0;i<6;i++){
    let b = document.createElement('span');
    b.className = 'ball spin';
    b.innerText = Math.floor(Math.random()*55)+1;
    container.appendChild(b);
    balls.push(b);
  }

  setTimeout(()=>{
    fetch('/api')
    .then(res=>res.json())
    .then(data=>{
      balls.forEach((b,i)=>{
        b.classList.remove('spin');
        b.innerText = data[i];
        b.classList.add(getColor(data[i]));
      });
    });
  },1500);
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api')
def api():
    return generate()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
