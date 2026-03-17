<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Alarm Panel</title>

<style>

body{
font-family:sans-serif;
margin:20px;
}

.container{
display:flex;
gap:40px;
align-items:flex-start;
}

.panel{
width:320px;
text-align:center;
}

.camera{
text-align:center;
}

#status{
font-size:26px;
margin-bottom:10px;
}

.armed{color:red;}
.disarmed{color:green;}

#pad{
display:grid;
grid-template-columns:repeat(3,80px);
gap:10px;
justify-content:center;
margin-top:10px;
}

button{
font-size:20px;
padding:15px;
}

#pin{
font-size:24px;
letter-spacing:10px;
margin:15px;
}

#alarm{
color:red;
font-weight:bold;
}

img{
border:1px solid #ccc;
}

</style>
</head>

<body>

<h2>Security Panel</h2>

<div class="container">

<div class="panel">

<div id="status">Loading...</div>
<div id="alarm"></div>
<div id="countdown"></div>

<div id="pin">----</div>

<div id="pad">

<button onclick="press(1)">1</button>
<button onclick="press(2)">2</button>
<button onclick="press(3)">3</button>

<button onclick="press(4)">4</button>
<button onclick="press(5)">5</button>
<button onclick="press(6)">6</button>

<button onclick="press(7)">7</button>
<button onclick="press(8)">8</button>
<button onclick="press(9)">9</button>

<button onclick="clearPin()">C</button>
<button onclick="press(0)">0</button>

</div>

<br>

<button id="armbtn" onclick="toggleArm()">...</button>

</div>


<div class="camera">

<h3>Last Capture</h3>

<div id="captureTime">None</div>

<img id="lastimg" width="480"/>

</div>

</div>

<script>

let entered=""
let lastTimestamp=null
let armed=false

function updatePin(){
document.getElementById("pin").innerText=entered.padEnd(4,"-")
}

function press(n){
if(entered.length<4){
entered+=n
updatePin()
}
}

function clearPin(){
entered=""
updatePin()
}

function toggleArm(){

if(armed){
disarm()
}else{
fetch("/arm",{method:"POST"})
}
}

function disarm(){

fetch("/disarm",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({pin:entered})
}).then(r=>{
if(r.status!=200){
alert("Invalid PIN")
}
clearPin()
})
}

function updateUI(data){

armed=data.armed

let status=document.getElementById("status")
let button=document.getElementById("armbtn")

if(armed){
status.innerText="Status: ARMED"
status.className="armed"
button.innerText="DISARM"
}else{
status.innerText="Status: DISARMED"
status.className="disarmed"
button.innerText="ARM"
}

if(data.entry_delay){
document.getElementById("countdown").innerText=
"Entry Timeout: "+data.entry_delay+"s"
}else{
document.getElementById("countdown").innerText=""
}

if(data.alarm){
document.getElementById("alarm").innerText="ALARM TRIGGERED"
}else{
document.getElementById("alarm").innerText=""
}

if(data.has_image){

document.getElementById("captureTime").innerText=
"Captured: "+data.last_time

if(lastTimestamp!==data.last_time){
lastTimestamp=data.last_time
document.getElementById("lastimg").src="/image?t="+Date.now()
}

}

}

function poll(){
fetch("/status")
.then(r=>r.json())
.then(updateUI)
}

setInterval(poll,1000)

updatePin()
poll()

</script>

</body>
</html>