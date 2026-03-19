import streamlit as st

DARK_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,*::before,*::after{box-sizing:border-box;}
.stApp{background:#030308;background-image:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(76,87,240,0.15),transparent),radial-gradient(ellipse 60% 40% at 80% 80%,rgba(29,185,84,0.06),transparent);color:#fff;font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
div[data-testid="stHeader"]{background:transparent;}
div.block-container{padding-top:0!important;padding-bottom:0!important;max-width:100%!important;}
div[data-testid="column"]{padding:4px!important;}
@keyframes pulse{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:.6;}50%{transform:translate(-50%,-50%) scale(1.15);opacity:1;}}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-12px);}}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
.hero-wrap{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;position:relative;overflow:hidden;}
.hero-wrap::before{content:'';position:absolute;width:600px;height:600px;background:radial-gradient(circle,rgba(76,87,240,0.12) 0%,transparent 70%);top:50%;left:50%;transform:translate(-50%,-50%);animation:pulse 4s ease-in-out infinite;}
.hero-badge{font-size:.72rem;font-weight:700;letter-spacing:5px;text-transform:uppercase;color:rgba(255,255,255,.4);margin-bottom:18px;}
.hero-title{font-size:clamp(4rem,12vw,9rem);font-weight:900;letter-spacing:-6px;line-height:.9;background:linear-gradient(135deg,#fff 30%,rgba(255,255,255,.4) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:float 6s ease-in-out infinite;margin-bottom:20px;}
.hero-sub{font-size:1rem;opacity:.4;letter-spacing:6px;text-transform:uppercase;margin-bottom:50px;}
.topbar{background:rgba(3,3,8,.88);backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,.06);padding:10px 20px;position:sticky;top:0;z-index:100;}
.topbar-logo{font-size:1.2rem;font-weight:900;letter-spacing:-1px;background:linear-gradient(135deg,#fff,rgba(255,255,255,.5));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.glass{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:20px;padding:22px;backdrop-filter:blur(20px);margin-bottom:12px;transition:border-color .2s;animation:fadeIn .3s ease;}
.glass:hover{border-color:rgba(76,87,240,.3);}
.sub-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:18px;padding:20px;height:180px;position:relative;transition:border-color .2s,transform .2s;margin-bottom:8px;}
.sub-card:hover{border-color:rgba(76,87,240,.4);transform:translateY(-2px);}
.sub-card-name{font-size:1.05rem;font-weight:700;margin-bottom:3px;}
.sub-card-cred{font-size:.7rem;opacity:.45;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;}
.sub-stat{font-size:.65rem;opacity:.5;text-transform:uppercase;letter-spacing:1px;}
.sub-val{font-size:1.5rem;font-weight:800;}
.ghost-btn-container{margin-top:-180px;height:180px;position:relative;z-index:10;}
.ghost-btn-container button{height:180px!important;width:100%!important;opacity:0!important;border:none!important;background:transparent!important;cursor:pointer!important;}
.pill{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:100px;padding:6px 14px;font-size:.78rem;font-weight:600;margin:4px;}
.pill-green{border-color:rgba(29,185,84,.4);color:#1db954;}
.pill-red{border-color:rgba(255,82,82,.4);color:#ff5252;}
.pill-yellow{border-color:rgba(255,167,38,.4);color:#ffa726;}
.pill-blue{border-color:rgba(76,87,240,.4);color:#7c8ff5;}
.cal-event{border-left:3px solid;padding:10px 14px;border-radius:0 10px 10px 0;margin-bottom:8px;background:rgba(255,255,255,.03);}
.cal-event.upcoming{border-color:#4c57f0;}.cal-event.today{border-color:#1db954;background:rgba(29,185,84,.08);}
.cal-event.past{border-color:rgba(255,255,255,.2);opacity:.5;}.cal-event.warning{border-color:#ffa726;}
.cal-event-date{font-size:.68rem;opacity:.55;text-transform:uppercase;letter-spacing:1px;}
.cal-event-name{font-size:.92rem;font-weight:600;margin-top:2px;}
.cal-event-days{font-size:.75rem;margin-top:4px;}
.auth-card{max-width:420px;margin:0 auto;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:40px 36px;}
.auth-title{font-size:1.6rem;font-weight:800;margin-bottom:4px;}
.auth-sub{font-size:.85rem;opacity:.5;margin-bottom:28px;}
.stTextInput>div>div>input,.stNumberInput>div>div>input,div[data-baseweb="select"]>div{background:rgba(255,255,255,.05)!important;color:#fff!important;border-radius:10px!important;border:1px solid rgba(255,255,255,.1)!important;}
.stButton>button{background:linear-gradient(135deg,rgba(255,255,255,.1),rgba(255,255,255,.04));border:1px solid rgba(255,255,255,.15);color:white;border-radius:10px;font-weight:600;transition:all .2s;}
.stButton>button:hover{background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.3);}
.enter-cta button{background:rgba(255,255,255,.06)!important;border-radius:999px!important;padding:15px 60px!important;border:1px solid rgba(255,255,255,.5)!important;box-shadow:0 0 30px rgba(255,255,255,.15)!important;font-size:1rem!important;font-weight:800!important;letter-spacing:3px;text-transform:uppercase;}
.enter-cta button:hover{background:rgba(255,255,255,.15)!important;box-shadow:0 0 40px rgba(255,255,255,.3)!important;}
.cgpa-big{font-size:3.5rem;font-weight:900;letter-spacing:-3px;}
.cgpa-label{font-size:.72rem;opacity:.5;letter-spacing:3px;text-transform:uppercase;}
.sec-title{font-size:1.3rem;font-weight:800;letter-spacing:-.5px;margin:24px 0 12px;display:flex;align-items:center;gap:10px;}
.sec-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,.1),transparent);}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:2px;}
@media(max-width:768px){.topbar{padding:8px 10px;}.glass{padding:14px;}.sub-card{height:160px;}.ghost-btn-container{margin-top:-160px;height:160px;}.ghost-btn-container button{height:160px!important;}.cgpa-big{font-size:2.2rem;}}
</style>"""

LIGHT_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,*::before,*::after{box-sizing:border-box;}
.stApp{background:#f0f2f8;background-image:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(76,87,240,0.07),transparent);color:#111;font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
div[data-testid="stHeader"]{background:transparent;}
div.block-container{padding-top:0!important;padding-bottom:0!important;max-width:100%!important;}
div[data-testid="column"]{padding:4px!important;}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
.hero-wrap{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.hero-badge{font-size:.72rem;font-weight:700;letter-spacing:5px;text-transform:uppercase;color:rgba(0,0,0,.4);margin-bottom:18px;}
.hero-title{font-size:clamp(4rem,12vw,9rem);font-weight:900;letter-spacing:-6px;line-height:.9;color:#111;margin-bottom:20px;}
.hero-sub{font-size:1rem;opacity:.4;letter-spacing:6px;text-transform:uppercase;margin-bottom:50px;}
.topbar{background:rgba(255,255,255,.95);backdrop-filter:blur(24px);border-bottom:1px solid rgba(0,0,0,.07);padding:10px 20px;position:sticky;top:0;z-index:100;box-shadow:0 1px 12px rgba(0,0,0,.06);}
.topbar-logo{font-size:1.2rem;font-weight:900;letter-spacing:-1px;color:#111;}
.glass{background:#fff;border:1px solid rgba(0,0,0,.07);border-radius:20px;padding:22px;box-shadow:0 2px 16px rgba(0,0,0,.05);margin-bottom:12px;transition:all .2s;animation:fadeIn .3s ease;}
.glass:hover{border-color:rgba(76,87,240,.3);box-shadow:0 4px 24px rgba(76,87,240,.1);}
.sub-card{background:#fff;border:1px solid rgba(0,0,0,.07);border-radius:18px;padding:20px;height:180px;position:relative;transition:all .2s;margin-bottom:8px;box-shadow:0 2px 12px rgba(0,0,0,.04);}
.sub-card:hover{border-color:rgba(76,87,240,.4);transform:translateY(-2px);box-shadow:0 6px 24px rgba(76,87,240,.1);}
.sub-card-name{font-size:1.05rem;font-weight:700;margin-bottom:3px;color:#111;}
.sub-card-cred{font-size:.7rem;opacity:.4;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;}
.sub-stat{font-size:.65rem;opacity:.45;text-transform:uppercase;letter-spacing:1px;}
.sub-val{font-size:1.5rem;font-weight:800;}
.ghost-btn-container{margin-top:-180px;height:180px;position:relative;z-index:10;}
.ghost-btn-container button{height:180px!important;width:100%!important;opacity:0!important;border:none!important;background:transparent!important;cursor:pointer!important;}
.pill{display:inline-flex;align-items:center;gap:6px;background:rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.1);border-radius:100px;padding:6px 14px;font-size:.78rem;font-weight:600;margin:4px;color:#333;}
.pill-green{border-color:rgba(29,185,84,.4);color:#158a3e;}
.pill-red{border-color:rgba(255,82,82,.4);color:#c62828;}
.pill-yellow{border-color:rgba(255,167,38,.4);color:#e65100;}
.pill-blue{border-color:rgba(76,87,240,.4);color:#4c57f0;}
.cal-event{border-left:3px solid;padding:10px 14px;border-radius:0 10px 10px 0;margin-bottom:8px;background:#fff;box-shadow:0 1px 6px rgba(0,0,0,.04);}
.cal-event.upcoming{border-color:#4c57f0;}.cal-event.today{border-color:#1db954;background:rgba(29,185,84,.06);}
.cal-event.past{border-color:rgba(0,0,0,.2);opacity:.5;}.cal-event.warning{border-color:#ffa726;}
.cal-event-date{font-size:.68rem;opacity:.5;text-transform:uppercase;letter-spacing:1px;}
.cal-event-name{font-size:.92rem;font-weight:600;margin-top:2px;color:#111;}
.cal-event-days{font-size:.75rem;margin-top:4px;}
.auth-card{max-width:420px;margin:0 auto;background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:24px;padding:40px 36px;box-shadow:0 4px 32px rgba(0,0,0,.08);}
.auth-title{font-size:1.6rem;font-weight:800;margin-bottom:4px;color:#111;}
.auth-sub{font-size:.85rem;opacity:.5;margin-bottom:28px;}
.stTextInput>div>div>input,.stNumberInput>div>div>input,div[data-baseweb="select"]>div{background:#f5f7fc!important;color:#111!important;border-radius:10px!important;border:1px solid rgba(0,0,0,.12)!important;}
.stButton>button{background:linear-gradient(135deg,#4c57f0,#7c8ff5);border:none;color:white;border-radius:10px;font-weight:700;transition:all .2s;}
.stButton>button:hover{opacity:.9;transform:translateY(-1px);}
.enter-cta button{background:#111!important;border-radius:999px!important;padding:15px 60px!important;border:none!important;color:white!important;font-size:1rem!important;font-weight:800!important;letter-spacing:3px;text-transform:uppercase;}
.cgpa-big{font-size:3.5rem;font-weight:900;letter-spacing:-3px;}
.cgpa-label{font-size:.72rem;opacity:.5;letter-spacing:3px;text-transform:uppercase;}
.sec-title{font-size:1.3rem;font-weight:800;letter-spacing:-.5px;margin:24px 0 12px;display:flex;align-items:center;gap:10px;color:#111;}
.sec-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(0,0,0,.1),transparent);}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(0,0,0,.15);border-radius:2px;}
@media(max-width:768px){.topbar{padding:8px 10px;}.glass{padding:14px;}.sub-card{height:160px;}.ghost-btn-container{margin-top:-160px;height:160px;}.ghost-btn-container button{height:160px!important;}.cgpa-big{font-size:2.2rem;}}
</style>"""


def inject_css(dark: bool = True):
    st.markdown(DARK_CSS if dark else LIGHT_CSS, unsafe_allow_html=True)
