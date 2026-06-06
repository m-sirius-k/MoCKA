# inject_js.py
# orchestra_lp_v4_base.html に setLang JS を注入する
# 出力: orchestra_lp_v4.html

from pathlib import Path
import json

base = Path("orchestra_lp_v4_base.html").read_text(encoding="utf-8")

import importlib.util, sys
spec = importlib.util.spec_from_file_location("lang_data", "lang_data.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
LANGS = mod.LANGS

js_lines = ["<script>"]
js_lines.append("function kwTab(id,el){document.querySelectorAll('.kw-tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.kw-pane').forEach(p=>p.classList.remove('active'));el.classList.add('active');document.getElementById('kw-'+id).classList.add('active');}")
js_lines.append(f"const T={json.dumps(LANGS, ensure_ascii=False)};")
js_lines.append("""
function s(id,v,html){const e=document.getElementById(id);if(!e)return;html?e.innerHTML=v:e.textContent=v;}
function setLang(lang){
  const t=T[lang];
  document.documentElement.lang=t.html_lang;
  document.getElementById('doc-title').textContent=t.title;
  document.querySelectorAll('.lb').forEach(b=>{
    const map={ja:'日',en:'EN',zh:'中',ko:'한',es:'ES'};
    b.style.background=map[lang]===b.textContent.trim()?'#c9a84c':'transparent';
    b.style.color=map[lang]===b.textContent.trim()?'#1a1a1a':'rgba(255,255,255,.5)';
  });
  s('t-eyebrow',t.eyebrow);s('t-h1',t.h1,true);s('t-hero-sub',t.hero_sub);
  s('t-btn-free',`<i class="ti ti-brand-chrome" aria-hidden="true"></i> ${t.btn_free}`,true);
  s('t-btn-plan',t.btn_plan);
  s('t-badge1',t.badge1);s('t-badge2',t.badge2);s('t-badge3',t.badge3);
  s('t-lbl-save',t.lbl_save);s('t-h-save',t.h_save);s('t-p-save',t.p_save);
  s('t-saved',t.saved);s('t-thismonth',t.thismonth);s('t-search-ph',t.search_ph);
  s('t-today',t.today);s('t-yesterday',t.yesterday);s('t-3days',t.days3);
  s('t-flylink',t.flylink);s('t-flylink2',t.flylink);s('t-flylink3',t.flylink);
  s('t-pf1h',t.pf1h);s('t-pf1p',t.pf1p);s('t-pf2h',t.pf2h);s('t-pf2p',t.pf2p);
  s('t-pf3h',t.pf3h);s('t-pf3p',t.pf3p);
  s('t-lbl-rclick',t.lbl_rclick);s('t-h-rclick',t.h_rclick);s('t-p-rclick',t.p_rclick);
  s('t-step1pin',t.step1pin);s('t-step2pin',t.step2pin);
  s('t-sel-text',t.sel_text);
  s('t-ctx-feat',t.ctx_feat);s('t-ctx-copy',t.ctx_copy);
  s('t-ctx-search',t.ctx_search);s('t-ctx-link',t.ctx_link);
  s('t-rclick-pre',t.rclick_pre,true);s('t-rclick-post',t.rclick_post);
  s('t-lbl-parallel',t.lbl_parallel);s('t-h-parallel',t.h_parallel);s('t-p-parallel',t.p_parallel);
  s('t-kwtab1',t.kwtab1);s('t-kwtab2',t.kwtab2);
  s('t-kwq',t.kwq);s('t-kw-lbl-send',t.kw_lbl_send);s('t-kw-lbl-merge',t.kw_lbl_merge);
  s('t-kw-result-lbl',t.kw_result_lbl);s('t-kw-result-txt',t.kw_result_txt,true);
  s('t-inno-tag',t.inno_tag);s('t-inno-h',t.inno_h);s('t-inno-p',t.inno_p,true);
  s('t-ab-claude',t.ab_claude,true);s('t-ab-chatgpt',t.ab_chatgpt,true);
  s('t-ab-gemini',t.ab_gemini,true);s('t-ab-copilot',t.ab_copilot,true);
  s('t-ab-perplexity',t.ab_perplexity,true);
  s('t-em-lib',t.em_lib);s('t-em-set',t.em_set);
  s('t-em-notice',t.em_notice,true);s('t-em-dest-title',t.em_dest_title);
  s('t-em-hint',t.em_hint);s('t-em-speed-title',t.em_speed_title);
  s('t-em-speed-lbl',t.em_speed_lbl);s('t-sk-slow',t.sk_slow);s('t-sk-fast',t.sk_fast);
  s('t-em-warn',t.em_warn);
  s('t-sf1h',t.sf1h);s('t-sf1p',t.sf1p);s('t-sf2h',t.sf2h);s('t-sf2p',t.sf2p);
  s('t-sf3h',t.sf3h);s('t-sf3p',t.sf3p);s('t-sf4h',t.sf4h);s('t-sf4p',t.sf4p);
  s('t-lbl-jump',t.lbl_jump);s('t-h-jump',t.h_jump);s('t-p-jump',t.p_jump);
  s('t-sv1t',t.sv1t);s('t-sv1m',t.sv1m);s('t-sv2t',t.sv2t);s('t-sv2m',t.sv2m);
  s('t-goto-btn',t.goto_btn);s('t-goto-btn2',t.goto_btn);
  s('t-jump-banner',t.jump_banner);s('t-b-ext',t.b_ext);
  s('t-scroll-note',t.scroll_note);s('t-new-chat',t.new_chat);
  s('t-cs1',t.cs1);s('t-cs2',t.cs2);s('t-cs3',t.cs3);s('t-cs4',t.cs4);
  s('t-chat1',t.chat1);s('t-chat2',t.chat2);s('t-chat3',t.chat3);
  s('t-chat4',t.chat4,true);s('t-chat5',t.chat5);s('t-chat6',t.chat6);
  s('t-hl-pin',t.hl_pin);
  s('t-lbl-ai',t.lbl_ai);s('t-h-ai',t.h_ai);s('t-p-ai',t.p_ai);
  s('t-lbl-how',t.lbl_how);s('t-h-how',t.h_how);s('t-p-how',t.p_how);
  s('t-step1h',t.step1h);s('t-step1p',t.step1p);
  s('t-step2h',t.step2h);s('t-step2p',t.step2p);
  s('t-step3h',t.step3h);s('t-step3p',t.step3p);
  s('t-step4h',t.step4h);s('t-step4p',t.step4p);
  s('t-lbl-price',t.lbl_price);s('t-h-price',t.h_price);s('t-p-price',t.p_price);
  s('t-name-free',t.name_free);s('t-price-free',t.price_free);s('t-period-free',t.period_free);
  s('t-pf1',t.pf1);s('t-pf2',t.pf2);s('t-pf3',t.pf3);s('t-pf4',t.pf4);s('t-pf5',t.pf5);
  s('t-btn-free2',t.btn_free2);
  s('t-name-pro',t.name_pro);s('t-period-pro',t.period_pro);
  s('t-pp1',t.pp1);s('t-pp2',t.pp2);s('t-pp3',t.pp3);s('t-pp4',t.pp4);s('t-pp5',t.pp5);
  s('t-btn-pro',t.btn_pro);
  s('t-name-one',t.name_one);s('t-regular-one',t.regular_one);s('t-period-one',t.period_one);
  s('t-ribbon',t.ribbon);
  s('t-po1',t.po1);s('t-po2',t.po2);s('t-po3',t.po3);s('t-po4',t.po4);s('t-po5',t.po5);
  s('t-btn-one',t.btn_one);s('t-plan-note',t.plan_note,true);
  s('t-lbl-faq',t.lbl_faq);s('t-h-faq',t.h_faq);s('t-p-faq',t.p_faq);
  s('t-fq1',t.fq1);s('t-fa1',t.fa1);s('t-fq2',t.fq2);s('t-fa2',t.fa2);
  s('t-fq3',t.fq3);s('t-fa3',t.fa3);s('t-fq4',t.fq4);s('t-fa4',t.fa4);
  s('t-fq5',t.fq5);s('t-fa5',t.fa5);
  s('t-lbl-cta',t.lbl_cta);s('t-h-cta',t.h_cta);s('t-p-cta',t.p_cta,true);
  s('t-cta-free',t.cta_free);s('t-cta-plan',t.cta_plan);
}
""")
js_lines.append("document.addEventListener('DOMContentLoaded',()=>setLang('ja'));")
js_lines.append("</script>")
js_code = "\n".join(js_lines)

result = base.replace("</body>", js_code + "\n</body>")
Path("orchestra_lp_v4.html").write_text(result, encoding="utf-8")
size = Path("orchestra_lp_v4.html").stat().st_size
print(f"orchestra_lp_v4.html: {size:,} bytes")
print("Next: WordPress")
