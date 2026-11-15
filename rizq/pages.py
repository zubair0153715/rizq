# -*- coding: utf-8 -*-
"""Rizq page — single-file app. Diary lives in the user's browser
(localStorage); nothing is stored server-side."""

RIZQ_HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rizq رزق — Free AI Nutrition Tracker (Pakistan-first)</title>
<style>
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;max-width:860px;margin:0 auto;padding:16px;line-height:1.5;color:#1a1a1a;background:#fffdf7}
h1{font-size:28px;margin:4px 0} h2{font-size:20px;margin:22px 0 8px;border-bottom:2px solid #2e7d32;padding-bottom:4px}
.card{border:1px solid #ddd;border-radius:10px;padding:14px;margin:10px 0;background:#fff}
input,select,button{font-size:15px;padding:8px;border-radius:8px;border:1px solid #bbb}
button{background:#2e7d32;color:#fff;border:none;cursor:pointer;padding:8px 14px}
button.sec{background:#eee;color:#222} button.warn{background:#b3261e}
input[type=file]{border:none}
.food{border:1px solid #e0e0e0;border-radius:8px;padding:10px;margin:8px 0}
.food b{font-size:16px} .ur{color:#555} .muted{color:#666;font-size:13px}
.badge{display:inline-block;background:#e8f5e9;border-radius:6px;padding:1px 7px;font-size:12px;margin-right:4px}
.badge.warn{background:#fff3e0}.badge.bad{background:#fce4ec}
.bar{height:14px;background:#eee;border-radius:7px;overflow:hidden}.bar>div{height:100%;background:#2e7d32}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.grid label{font-size:13px;color:#555;display:block}
.grid input,.grid select{width:100%;box-sizing:border-box}
table{width:100%;border-collapse:collapse;font-size:14px}
td,th{border-bottom:1px solid #eee;padding:6px 4px;text-align:left}
.err{color:#b3261e}.ok{color:#2e7d32}
@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style></head><body>
<h1>🍽️ Rizq <span class="ur">رزق</span></h1>
<p><b>Free AI nutrition tracker — Pakistan-first.</b> Biryani, nihari,
daal, roti — search in English, Roman-Urdu ya Urdu. No account, no
card, no trial, no paywall, <b>no ads</b>. Aapka diary sirf aapke
browser mein rehta hai.</p>
<p class="muted">Cal AI ($29.99/year, 3-day trial) ke muqable mein Rizq
free hai — aur photo estimate ek fake-precise number ki bajaye
<b>range + confidence</b> deta hai, taake aap dekh sakein ke andaza
kitna pakka hai.</p>
<p id="aiStatus" class="muted">AI status check ho raha hai…</p>

<h2>🎯 Aapka daily target</h2>
<div class="card"><div class="grid">
<label>Sex <select id="sex"><option value="male">Male</option><option value="female">Female</option></select></label>
<label>Age (years) <input id="age" type="number" value="25" min="10" max="100"></label>
<label>Weight (kg) <input id="weight" type="number" value="70" min="30" max="300"></label>
<label>Height (cm) <input id="height" type="number" value="175" min="120" max="230"></label>
<label>Activity <select id="activity">
<option value="sedentary">Sedentary — little/no exercise</option>
<option value="light">Light — 1–3 days/week</option>
<option value="moderate" selected>Moderate — 3–5 days/week</option>
<option value="active">Active — 6–7 days/week</option>
<option value="athlete">Athlete — very hard, physical job</option></select></label>
<label>Goal <select id="goal">
<option value="lose">Lose weight (−500 kcal/day)</option>
<option value="maintain" selected>Maintain weight</option>
<option value="gain">Gain weight (+300 kcal/day)</option></select></label>
</div>
<p><button onclick="calcTargets()">Calculate target</button>
<label style="margin-left:12px"><input type="checkbox" id="ramadan" onchange="renderDiary()"> Ramadan mode (Suhoor / Iftar)</label></p>
<div id="targetOut"></div></div>

<h2>📸 AI photo / text estimate</h2>
<div class="card">
<p class="muted">Photo khinchiye ya khana likhiye — AI har cheez alag
pehchanega, grams aur macros batayega, aur <b>range</b> dega (jaise
450–620 kcal). Log karne se pehle koi bhi item edit kar sakte hain.
Camera chhupa hua oil, cheeni ya namak nahi dekh sakta — is liye
yeh andaza hai, measurement nahi.</p>
<p><input type="file" id="photo" accept="image/jpeg,image/png,image/webp">
<input id="mealText" placeholder="masalan: 1 plate chicken biryani with raita" style="width:60%">
<button onclick="estimateMeal()">Estimate</button></p>
<p><label>Meal <select id="estMeal"><option>breakfast</option><option selected>lunch</option><option>dinner</option><option>snacks</option></select></label></p>
<div id="estOut"></div></div>

<h2>🔍 Khana search karein</h2>
<div class="card">
<p><input id="q" placeholder="biryani, daal, roti, egg…" style="width:55%" oninput="loadFoods()">
<select id="cat" onchange="loadFoods()"><option value="">All categories</option></select>
<label><input type="checkbox" id="veg" onchange="loadFoods()"> Veg only</label>
<label><input type="checkbox" id="dia" onchange="loadFoods()"> Diabetes-friendly</label></p>
<div id="foodList" class="muted">Loading foods…</div></div>

<h2>📓 Aaj ki diary</h2>
<div class="card">
<p><span id="diaryDate"></span> · <span id="streak"></span>
<button class="sec" onclick="loadDemo()">Demo day dekhein</button>
<button class="sec" onclick="exportDiary()">Export JSON</button>
<button class="sec" onclick="document.getElementById('imp').click()">Import JSON</button>
<input type="file" id="imp" accept="application/json" style="display:none" onchange="importDiary(event)">
<button class="warn" onclick="clearToday()">Aaj clear karein</button></p>
<div id="diaryOut"></div></div>

<h2>⚠️ Honest limits</h2>
<div class="card muted" style="font-size:14px">
<ul>
<li>Photo estimates <b>andaze</b> hain — camera chhupa oil/cheeni/namak nahi dekh sakta. Range aur confidence dekhein, portion correct karein, phir log karein.</li>
<li>Food values USDA FoodData Central ke generic values + documented standard recipes se compute hoti hain. Aapke ghar ki recipe mukhtalif hogi — zyada/kam oil sab badal deta hai.</li>
<li>BMR/TDEE Mifflin-St Jeor formula se hain — starting point, medical prescription nahi. Diabetes, kidney disease, pregnancy ya kisi bhi medical condition mein doctor ya dietitian se mashwara karein. Rizq general nutrition information hai — medical advice nahi.</li>
<li>Glycaemic load published GI values se hai; mixed dishes ke liye yeh approximation hai.</li>
<li>AI estimates ke liye owner ki Gemini key (GEMINI_API_KEY) chahiye. Bina key ke bhi food database, diary, targets aur flags poore kaam karte hain.</li>
</ul></div>

<script>
const API="/rizq/api";
let store=JSON.parse(localStorage.getItem("rizq-v1")||"{}");
if(!store.diary)store.diary={}; if(!store.days)store.days=[];
function save(){localStorage.setItem("rizq-v1",JSON.stringify(store));}
function today(){return new Date().toISOString().slice(0,10);}
const MEALS=()=>document.getElementById("ramadan").checked?["suhoor","iftar"]:["breakfast","lunch","dinner","snacks"];
function targets(){return store.targets||null;}

async function aiStatus(){try{const r=await fetch(API+"/ai-status");const j=await r.json();
document.getElementById("aiStatus").textContent=j.ai_available?"✅ AI available (owner key set) — photo aur text estimates kaam karte hain.":"ℹ️ AI key set nahi hai — photo/text estimate band hai, baaki sab (database, diary, targets) poora kaam karta hai.";
}catch(e){document.getElementById("aiStatus").textContent="AI status nahi mil saka.";}}

async function calcTargets(){const b={sex:sex.value,age:age.value,weight_kg:weight.value,height_cm:height.value,activity:activity.value,goal:goal.value};
const r=await fetch(API+"/targets",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});
const j=await r.json();
if(!j.ok){targetOut.innerHTML="<p class='err'>"+j.error+"</p>";return;}
store.targets=j.targets;save();renderTargets();}
function renderTargets(){const t=targets();if(!t)return;
targetOut.innerHTML="<p><b>Daily target: "+t.target_kcal+" kcal</b> · BMR "+t.bmr+" · TDEE "+t.tdee+" · Protein target ~"+t.protein_target+" g/day</p><p class='muted'>"+t.formula+"</p>";
renderDiary();}

async function loadFoods(){const u=new URL(API+"/foods",location.origin);
u.searchParams.set("q",q.value);u.searchParams.set("cat",cat.value);
u.searchParams.set("veg",veg.checked?1:0);u.searchParams.set("diabetes",dia.checked?1:0);
const r=await fetch(u);const j=await r.json();
if(!j.ok){foodList.innerHTML="<p class='err'>"+j.error+"</p>";return;}
if(!cat.options.length||cat.options.length<2){for(const [k,v] of Object.entries(j.categories)){const o=document.createElement("option");o.value=k;o.textContent=v;cat.appendChild(o);}}
foodList.innerHTML=j.count?j.foods.map(f=>"<div class='food'><b>"+f.en+"</b> <span class='ur'>"+f.ur+"</span> <span class='muted'>("+f.roman+")</span><br>"+
"<span class='badge'>"+f.serving+" · "+f.grams+" g</span><span class='badge'><b>"+f.kcal+" kcal</b></span>"+
"<span class='badge'>P "+f.protein+" g</span><span class='badge'>C "+f.carbs+" g</span><span class='badge'>F "+f.fat+" g</span>"+
"<span class='badge'>GL "+f.gl+"</span>"+
(f.veg?"<span class='badge'>🌱 Veg</span>":"")+(f.high_protein?"<span class='badge'>💪 High protein</span>":"")+
(f.diabetes_friendly?"<span class='badge warn'>🩸 Diabetes-friendly (GL ≤ 10)</span>":"")+
"<br><span class='muted'>"+f.cat_label+" · "+f.source+"</span><br>"+
"Qty <input type='number' id='qty-"+f.id+"' value='1' min='0.25' step='0.25' style='width:64px'> "+
"<select id='meal-"+f.id+"'>"+MEALS().map(m=>"<option>"+m+"</option>").join("")+"</select> "+
"<button onclick=\"addFood('"+f.id+"')\">+ Log karein</button></div>").join(""):"<p>Is search mein kuch nahi mila.</p>";}

function addFood(fid,qty,meal,label,vals){const day=today();if(!store.diary[day])store.diary[day]=[];
if(!vals){const f=window._foods&&window._foods[fid];if(!f)return;
qty=parseFloat(document.getElementById("qty-"+fid).value)||1;
meal=document.getElementById("meal-"+fid).value;label=f.en+" ("+f.serving+")";
vals={kcal:f.kcal,protein:f.protein,carbs:f.carbs,fat:f.fat};}
store.diary[day].push({meal,label,qty,kcal:+(vals.kcal*qty).toFixed(1),protein:+(vals.protein*qty).toFixed(1),carbs:+(vals.carbs*qty).toFixed(1),fat:+(vals.fat*qty).toFixed(1)});
if(!store.days.includes(day))store.days.push(day);
save();renderDiary();}

async function estimateMeal(){const file=photo.files[0];const txt=mealText.value.trim();
estOut.innerHTML="<p>AI soch raha hai…</p>";
let body;const lang="roman";
if(file){const b64=await new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result.split(",")[1]);r.onerror=rej;r.readAsDataURL(file);});
body={kind:"photo",image_b64:b64,mime:file.type,language:lang};}
else if(txt){body={kind:"text",description:txt,language:lang};}
else{estOut.innerHTML="<p class='err'>Photo chunein ya khana likhein.</p>";return;}
const r=await fetch(API+"/estimate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
const j=await r.json();
if(!j.ok){estOut.innerHTML="<p class='err'>"+j.error+"</p>";return;}
const e=j.estimate;
window._est=e;
estOut.innerHTML="<p><b>Estimate: "+e.low+"–"+e.high+" kcal</b> (best guess "+e.total.kcal+" kcal) · confidence: <b>"+e.confidence+"</b></p>"+
(e.note?"<p class='muted'>AI note: "+e.note+"</p>":"")+
"<table><tr><th>Item</th><th>Grams</th><th>kcal</th><th>P</th><th>C</th><th>F</th><th>Conf.</th><th>Qty</th></tr>"+
e.items.map((it,i)=>"<tr><td>"+it.name+"</td><td>"+it.grams+" g</td><td>"+it.kcal+"</td><td>"+it.protein+"</td><td>"+it.carbs+"</td><td>"+it.fat+"</td><td>"+it.confidence+"</td>"+
"<td><input type='number' id='eqty-"+i+"' value='1' min='0.25' step='0.25' style='width:60px'></td></tr>").join("")+"</table>"+
"<p class='muted'>Portion ghalat lage to qty badal kar log karein — range hi asal sach hai, single number nahi.</p>"+
"<button onclick='logEstimate()'>✓ Ye items diary mein log karein</button>";
}
function logEstimate(){const e=window._est;if(!e)return;const meal=estMeal.value;
e.items.forEach((it,i)=>{const q=parseFloat(document.getElementById("eqty-"+i).value)||1;
addFood(null,q,meal,it.name+" (~"+it.grams+" g)",{kcal:it.kcal,protein:it.protein,carbs:it.carbs,fat:it.fat});});
estOut.innerHTML="<p class='ok'>✓ Logged — "+e.items.length+" items ("+e.low+"–"+e.high+" kcal range).</p>";}

function renderDiary(){const day=today();document.getElementById("diaryDate").textContent="Aaj: "+day;
document.getElementById("streak").textContent="🔥 Streak: "+store.days.length+" din logged";
const entries=store.diary[day]||[];
if(!entries.length){diaryOut.innerHTML="<p class='muted'>Aaj abhi kuch log nahi hua — upar se khana search karein ya photo estimate karein.</p>";return;}
let tot={kcal:0,protein:0,carbs:0,fat:0};entries.forEach(e=>{tot.kcal+=e.kcal;tot.protein+=e.protein;tot.carbs+=e.carbs;tot.fat+=e.fat;});
const t=targets();const pct=t?Math.min(100,Math.round(tot.kcal/t.target_kcal*100)):0;
diaryOut.innerHTML="<table><tr><th>Meal</th><th>Khana</th><th>Qty</th><th>kcal</th><th>P</th><th>C</th><th>F</th><th></th></tr>"+
entries.map((e,i)=>"<tr><td>"+e.meal+"</td><td>"+e.label+"</td><td>"+e.qty+"</td><td>"+e.kcal+"</td><td>"+e.protein+"</td><td>"+e.carbs+"</td><td>"+e.fat+"</td><td><button class='sec' onclick='delEntry("+i+")'>✕</button></td></tr>").join("")+
"<tr><td colspan='3'><b>Total</b></td><td><b>"+tot.kcal.toFixed(0)+"</b></td><td>"+tot.protein.toFixed(0)+"</td><td>"+tot.carbs.toFixed(0)+"</td><td>"+tot.fat.toFixed(0)+"</td><td></td></tr></table>"+
(t?"<p>Target "+t.target_kcal+" kcal — <b>"+tot.kcal.toFixed(0)+" / "+t.target_kcal+"</b> ("+pct+"%) · Protein "+tot.protein.toFixed(0)+" / "+t.protein_target+" g</p><div class='bar'><div style='width:"+pct+"%'></div></div>":"<p class='muted'>Target set karein (upar) to progress dekhein.</p>")+
(MEALS().includes("suhoor")&&t?"<p class='muted'>Ramadan split: Suhoor ~"+Math.round(t.target_kcal*0.4)+" kcal · Iftar ~"+Math.round(t.target_kcal*0.6)+" kcal</p>":"");}
function delEntry(i){store.diary[today()].splice(i,1);save();renderDiary();}
function clearToday(){if(confirm("Aaj ki diary clear karein?")){store.diary[today()]=[];save();renderDiary();}}
async function loadDemo(){const r=await fetch(API+"/demo");const j=await r.json();
if(!j.ok)return;store.diary[today()]=j.entries.map(e=>({meal:e.meal,label:e.label,qty:e.qty,kcal:e.kcal,protein:e.protein,carbs:e.carbs,fat:e.fat}));
if(!store.days.includes(today()))store.days.push(today());save();renderDiary();}
function exportDiary(){const blob=new Blob([JSON.stringify(store,null,2)],{type:"application/json"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="rizq-diary.json";a.click();}
function importDiary(ev){const f=ev.target.files[0];if(!f)return;const r=new FileReader();
r.onload=()=>{try{const d=JSON.parse(r.result);if(d.diary){store=d;save();renderTargets();renderDiary();alert("Import ho gaya.");}}catch(e){alert("JSON samajh nahi aaya.");}};
r.readAsText(f);}

// cache food lookup for addFood
const _origLoad=loadFoods;
loadFoods=async function(){await _origLoad();window._foods={};
const u=new URL(API+"/foods",location.origin);u.searchParams.set("q",q.value);
u.searchParams.set("cat",cat.value);u.searchParams.set("veg",veg.checked?1:0);u.searchParams.set("diabetes",dia.checked?1:0);
const r=await fetch(u);const j=await r.json();if(j.ok)j.foods.forEach(f=>window._foods[f.id]=f);};

aiStatus();loadFoods();renderTargets();renderDiary();
</script></body></html>
"""
