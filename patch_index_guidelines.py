from pathlib import Path

index_html = Path(r"C:\Users\sirok\MoCKA\index.html")
txt = index_html.read_text(encoding="utf-8")

if "guidelines" in txt:
    print("[SKIP] 既にパッチ適用済み")
    exit()

PANEL = """
<!-- ================================================================ -->
<!-- GUIDELINES PANEL (2026-05-10)                                     -->
<!-- ================================================================ -->
<div class="panel" style="grid-column:span 2;margin-top:12px;">
  <div class="panel-header" style="display:flex;align-items:center;">
    <span>&#128203; &#34892;&#21205;&#25351;&#37341; (Guidelines Engine)</span>
    <button id="gl-run-btn" onclick="runGuidelines()"
      style="margin-left:auto;padding:3px 12px;font-size:11px;
             background:#1a3a1a;border:1px solid #2a6a2a;
             color:#7fff7f;border-radius:4px;cursor:pointer;">
      &#9654; &#20170;&#12377;&#12368;&#29983;&#25104;
    </button>
  </div>
  <div class="panel-body">
    <div style="display:flex;gap:16px;margin-bottom:8px;font-size:12px;">
      <span>&#21512;&#35336;: <b id="gl-total">-</b>&#20214;</span>
      <span>&#26356;&#26032;: <span id="gl-updated" style="color:#888;">-</span></span>
    </div>
    <div id="gl-cats" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;"></div>
    <div style="font-size:11px;color:#aaa;margin-bottom:4px;">&#12473;&#12467;&#12450;&#19978;&#20301;&#34892;&#21205;&#25351;&#37341;:</div>
    <div id="gl-top5" style="display:flex;flex-direction:column;gap:4px;"></div>
  </div>
</div>

<script>
var GL_CAT_COLORS = {
  INCIDENT:"#ff4444",MATAKA:"#ff8800",DECISION:"#4488ff",
  INSIGHT:"#44cc44",CHALLENGE:"#ffcc00",GENERAL:"#888888"
};

function refreshGuidelines() {
  fetch("/guidelines/status").then(function(r){return r.json();}).then(function(d){
    document.getElementById("gl-total").textContent = d.total || 0;
    var upd = (d.last_updated || "").slice(0,16).replace("T"," ");
    document.getElementById("gl-updated").textContent = upd || "-";

    var cats = document.getElementById("gl-cats");
    cats.innerHTML = "";
    var bc = d.by_category || {};
    Object.keys(bc).forEach(function(cat){
      var color = GL_CAT_COLORS[cat] || "#888";
      cats.innerHTML += '<span style="background:'+color+'22;border:1px solid '+color+
        ';color:'+color+';padding:2px 8px;border-radius:10px;font-size:11px;">'+
        cat+': '+bc[cat]+'</span> ';
    });

    var top5 = document.getElementById("gl-top5");
    top5.innerHTML = "";
    var items = d.top5 || [];
    if(items.length === 0){
      top5.innerHTML = '<div style="color:#555;font-size:11px;">&#12300;&#9654; &#20170;&#12377;&#12368;&#29983;&#25104;&#12301;&#12434;&#12463;&#12522;&#12483;&#12463;&#12375;&#12390;&#12367;&#12384;&#12373;&#12356;</div>';
    } else {
      items.forEach(function(g){
        var color = GL_CAT_COLORS[g.category] || "#888";
        var dir = (g.directive || "").slice(0,100);
        top5.innerHTML += '<div style="background:#111;border-left:3px solid '+color+
          ';padding:5px 8px;border-radius:3px;margin-bottom:2px;">'+
          '<span style="color:'+color+';font-size:10px;font-weight:bold;">'+g.category+'</span>'+
          '<span style="color:#ccc;font-size:11px;margin-left:6px;">'+dir+'</span>'+
          '<span style="float:right;color:#555;font-size:10px;">'+(g.score*100).toFixed(0)+'pt</span>'+
          '</div>';
      });
    }
  }).catch(function(e){ console.warn("[GL]",e); });
}

function runGuidelines() {
  var btn = document.getElementById("gl-run-btn");
  btn.textContent = "&#9203; &#29983;&#25104;&#20013;...";
  btn.disabled = true;
  fetch("/guidelines/run", {method:"POST"}).then(function(r){return r.json();})
  .then(function(d){
    btn.textContent = "&#10003; &#23436;&#20102; ("+d.total+"&#20214;)";
    setTimeout(function(){ btn.textContent="&#9654; &#20170;&#12377;&#12368;&#29983;&#25104;"; btn.disabled=false; }, 3000);
    refreshGuidelines();
  }).catch(function(){
    btn.textContent = "&#10007; &#12456;&#12521;&#12540;";
    setTimeout(function(){ btn.textContent="&#9654; &#20170;&#12377;&#12368;&#29983;&#25104;"; btn.disabled=false; }, 3000);
  });
}

setInterval(refreshGuidelines, 60000);
refreshGuidelines();
</script>
"""

# </body>の直前に挿入
if "</body>" in txt:
    patched = txt.replace("</body>", PANEL + "\n</body>")
    index_html.write_text(patched, encoding="utf-8")
    print("[OK] index.html 行動指針パネル追加完了")
else:
    print("[ERROR] </body>が見つかりません")
    print("末尾50文字:", repr(txt[-50:]))
