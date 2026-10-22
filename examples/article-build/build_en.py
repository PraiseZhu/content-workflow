# Render source: python3 build.py -> ../images/cn/*.png (headless Chromium)
import subprocess, os
OUT='../images/en'
CSS='''
*{margin:0;padding:0;box-sizing:border-box}
body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#04120e;color:#fff;font-family:"Inter","Noto Sans CJK SC",sans-serif;position:relative}
.ab{position:absolute}
.photo{position:absolute;filter:grayscale(1) sepia(1) hue-rotate(118deg) saturate(1.6) brightness(1.05) contrast(1.2)}
.tint{position:absolute;inset:0;background:radial-gradient(ellipse at 30%% 40%%,rgba(20,120,95,.18),rgba(2,14,11,.55));mix-blend-mode:normal}
.grain{position:absolute;inset:0;opacity:.22;mix-blend-mode:overlay;background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='300' height='300' filter='url(%%23n)'/></svg>")}
.vl{position:absolute;top:0;bottom:0;width:1px;background:rgba(255,255,255,.13)}
.hl{position:absolute;left:0;right:0;height:1px;background:rgba(255,255,255,.13)}
.or{background:#FF5A1F!important}
.nav{font:500 %(nav)dpx "Inter";letter-spacing:.06em;text-transform:uppercase}
.mono{font-family:"JetBrains Mono","IBM Plex Mono",monospace;text-transform:uppercase;letter-spacing:.04em}
.tag{font:400 %(tag)dpx "JetBrains Mono";letter-spacing:.02em}
.zh{font-family:"Noto Sans CJK SC";font-weight:700;letter-spacing:-.01em;font-feature-settings:"palt"}
.title{line-height:1.08;letter-spacing:-.02em;white-space:nowrap}
.title .l{font-family:"Inter";font-weight:800;letter-spacing:-.04em}
.chip{background:#FF5A1F;color:#fff;font:600 %(chip)dpx "JetBrains Mono";padding:.35em .7em;letter-spacing:.05em;white-space:nowrap}
.chipw{background:#fff;color:#04120e;font:600 %(chipw)dpx "JetBrains Mono";padding:.3em .6em;white-space:nowrap;display:inline-block}
.br{position:absolute;border:0}
.br i{position:absolute;width:28%%;height:28%%;border-color:#FF5A1F;border-style:solid;border-width:0}
.br i:nth-child(1){left:0;top:0;border-left-width:3px;border-top-width:3px}
.br i:nth-child(2){right:0;top:0;border-right-width:3px;border-top-width:3px}
.br i:nth-child(3){left:0;bottom:0;border-left-width:3px;border-bottom-width:3px}
.br i:nth-child(4){right:0;bottom:0;border-right-width:3px;border-bottom-width:3px}
.br b{position:absolute;left:50%%;top:50%%;transform:translate(-50%%,-50%%);color:#FF5A1F;font:300 30px "JetBrains Mono"}
.colh{font:300 %(colh)dpx "Inter","Noto Sans CJK SC";letter-spacing:.01em}
.list{font:400 %(list)dpx/1.9 "JetBrains Mono";letter-spacing:.04em;text-transform:uppercase;color:rgba(255,255,255,.88)}
.giant{font-family:"Inter";font-weight:700;letter-spacing:-.05em;line-height:.8}
.bar{border:1px solid rgba(255,255,255,.7);height:%(barh)dpx;position:relative}
.bar span{position:absolute;left:0;top:0;bottom:0;background:#fff}
'''
def page(W,H,body,s=1.0):
    d=dict(W=W,H=H,nav=int(15*s),tag=int(30*s),chip=int(17*s),chipw=int(13*s),colh=int(30*s),list=int(12*s),barh=int(12*s))
    return '<!doctype html><html><head><meta charset="utf-8"><style>'+CSS%d+'</style></head><body>'+body+'<div class="grain"></div></body></html>'
def photo(src,left,top,w,dim=1.0): return f'<img class="photo" src="{src}" style="left:{left}px;top:{top}px;width:{w}px;opacity:{dim}"><div class="tint"></div>'
def grid(W,H,cols,rows):
    return ''.join(f'<div class="vl" style="left:{x}px"></div>' for x in cols)+''.join(f'<div class="hl" style="top:{y}px"></div>' for y in rows)
def br(x,y,w,h,plus=True): return f'<div class="br" style="left:{x-w/2}px;top:{y-h/2}px;width:{w}px;height:{h}px"><i></i><i></i><i></i><i></i>'+('<b>+</b>' if plus else '')+'</div>'
def nav(items,xs,y,s=''): return ''.join(f'<div class="ab nav" style="left:{x}px;top:{y}px;{s}">{t}</div>' for t,x in zip(items,xs))
def tele(x,y,lines,fs=12): return f'<div class="ab mono" style="left:{x}px;top:{y}px;font-size:{fs}px;line-height:1.8;color:rgba(255,255,255,.8)">'+'<br>'.join(lines)+'</div>'
def prog(x,y,w,p=88,fs=11): return f'<div class="ab" style="left:{x}px;top:{y}px;width:{w}px"><div class="mono" style="font-size:{fs}px;margin-bottom:6px">PROCESSING {p}%</div><div class="bar"><span style="width:{p}%"></span></div></div>'
def ab(x,y,html,style=''): return f'<div class="ab" style="left:{x}px;top:{y}px;{style}">{html}</div>'
def target(x,y,w,h,chip,sub,side='left'):
    cx = x-w/2-10 if side=='left' else x+w/2+10
    tr = 'translateX(-100%)' if side=='left' else ''
    return br(x,y,w,h)+ab(cx,y-h/2-8,f'<div class="chipw">{sub}</div><br><div class="chip" style="display:inline-block;margin-top:6px">{chip}</div>',f'transform:{tr} translateY(-100%);text-align:{"right" if side=="left" else "left"}')

NAV=['REVIEW','GATES','ISOLATION','APPEAL','RELEASE']
COLS=[('GATES',['DETERMINISTIC GATES','CI GREEN','NO CONFLICT','EVERY 3 MIN']),
      ('ISOLATION',['4-STAGE','CREDENTIAL ISOLATION','NO-CRED SCAN','GATEWAY TOKEN ONLY']),
      ('VERIFY',['AUTHOR APPEAL','RE-CHECK ON HEAD','MAINTAINER RULING','DEFER TO ISSUE']),
      ('RELEASE',['8 REQUIRED CHECKS','NO P0 / P1','THREADS RESOLVED','DESIGNATED MERGE'])]

def hero(W,H,s,f):
    # f: layout dict
    b=photo('campus.jpg',f['px'],f['py'],f['pw'])
    b+=f'<div class="ab" style="left:{f["px"]+f["pw"]-500*s}px;top:0;width:{600*s}px;bottom:0;background:linear-gradient(90deg,rgba(4,18,14,0),#04120e)"></div>'
    b+=grid(W,H,f['cols'],f['rows'])
    b+=f'<div class="hl or" style="top:{f["orule"]}px;height:2px;background:#FF5A1F"></div>'
    b+=f'<div class="vl or" style="left:{f["ovl"]}px;width:1px;opacity:.85"></div>'
    b+=nav(NAV,f['navx'],f['navy'])
    b+=ab(f['tagx'],f['tagy'],'[ REVIEW-01 ]','font:400 %dpx JetBrains Mono'%(34*s))
    b+=tele(f['tagx'],f['tagy']+70*s,['CONTACT','FINDING P1 · SRC MODEL-A  CONF 0.71','HEAD 7F3C · DIFF 214 LN · RE-CHECK'],int(12*s))
    b+=prog(f['tagx'],f['tagy']+150*s,200*s,fs=int(11*s))
    b+=target(*f['tgt'],'P1 · VERIFYING','FINDING / P1',side=f.get('side','left'))
    b+=ab(f['tx'],f['ty'],'<div class="zh title" style="font-size:%dpx">When <span class="l">AI</span> Reviews <span class="l">AI</span><br>Beware the Nod</div>'%f['tfs'])
    b+=ab(f['dx'],f['dy'],f'<div style="display:flex;gap:{18*s}px;align-items:flex-start"><div style="font:300 {64*s}px/0.9 Inter">®</div><div><div class="zh" style="font-size:{40*s}px;line-height:1.2">Opinions must become evidence</div><div style="font:400 {20*s}px Inter;margin-top:{10*s}px;opacity:.9">Verify before block.</div></div></div>')
    for (h,l),x in zip(COLS,f['colx']):
        b+=ab(x,f['chy'],f'<div class="colh zh" style="font-weight:400">{h}</div>')
        b+=ab(x,f['ly'],'<div class="list">'+'<br>'.join(l)+'</div>')
    b+=ab(f['gx'],f['gy'],f'<div class="giant" style="font-size:{f["gfs"]}px">P0/P1</div>')
    return page(W,H,b,s)

def render(name,html,W,H):
    p=f'{name}.html'; open(p,'w').write(html)
    subprocess.run(['chromium','--headless=new','--no-sandbox','--hide-scrollbars','--force-device-scale-factor=1',f'--window-size={W},{H}',f'--screenshot={OUT}/{name}.png','--virtual-time-budget=3000','file://'+os.path.abspath(p)],check=True,capture_output=True)

# HEADER 2000x800 (X Article cover 5:2; 2026-10-17 specs)
# safe zone x200-1800, y160-680 (see wewrite references/image-specs.md)
W,H=2000,800
_h=hero(W,H,0.9,dict(px=-260,py=-20,pw=1100,
  cols=[200,560,900,1240,1580,1800],rows=[210,485,535],orule=440,ovl=520,
  navx=[200,560,900,1240,1580],navy=176,tagx=200,tagy=225,
  tgt=(450,500,80,72),side='left',
  tx=570,ty=228,tfs=84,dx=1415,dy=238,
  colx=[570,910,1250,1590],chy=550,ly=598,gx=198,gy=548,gfs=128))
_h=_h.replace('Opinions must become evidence','Opinions must<br>become evidence')
render('header-x-2000x800',_h,W,H)
# ---------- inline figures 1600x900 ----------
W,H=1600,900
def node(x,y,zh,en,w=200,orange=False,center=True):
    c='#FF5A1F' if orange else 'rgba(255,255,255,.9)'
    l=x-w/2 if center else x
    return (f'<div class="ab" style="left:{l}px;top:{y-38}px;width:{w}px;height:76px;background:rgba(4,18,14,.55)">'
      +''.join(f'<div class="ab" style="{p};width:12px;height:12px;border-color:{c};border-style:solid;border-width:{bw}"></div>' for p,bw in
         [('left:0;top:0','2px 0 0 2px'),('right:0;top:0','2px 2px 0 0'),('left:0;bottom:0','0 0 2px 2px'),('right:0;bottom:0','0 2px 2px 0')])
      +f'<div class="zh" style="text-align:center;font-size:22px;margin-top:12px;white-space:nowrap">{zh}</div>'
      +f'<div class="mono" style="text-align:center;font-size:11px;margin-top:4px;color:{"#FF8A5C" if orange else "rgba(255,255,255,.7)"};white-space:nowrap">{en}</div></div>')
def line(x1,y1,x2,y2,orange=False,dash=False,label=''):
    import math
    L=math.hypot(x2-x1,y2-y1); a=math.degrees(math.atan2(y2-y1,x2-x1))
    c='#FF5A1F' if orange else 'rgba(255,255,255,.75)'
    st=f'border-top:1px {"dashed" if dash else "solid"} {c}'
    h=f'<div class="ab" style="left:{x1}px;top:{y1}px;width:{L}px;{st};transform-origin:0 0;transform:rotate({a}deg)"></div>'
    h+=f'<div class="ab" style="left:{x2-4}px;top:{y2-4}px;width:8px;height:8px;background:{c}"></div>'
    if label: h+=ab((x1+x2)/2,(y1+y2)/2-22,f'<div class="mono" style="font-size:11px;color:rgba(255,255,255,.75);white-space:nowrap;transform:translateX(-50%)">{label}</div>')
    return h
def frame(bg,tag,head,body,dim=.7,px=0,py=0,pw=1600,extra_tele=None,code='FIG'):
    b=photo(bg,px,py,pw,dim)+f'<div class="ab" style="inset:0;background:rgba(3,14,11,{1-dim})"></div>'
    b+=grid(W,H,[60,380,700,1020,1340,1540],[70,240,760])
    b+=nav(['REVIEW','GATES','ISOLATION','APPEAL','RELEASE'],[60,380,700,1020,1340],30,'font-size:13px')
    b+=ab(60,100,f'<div style="font:400 26px JetBrains Mono">[ {tag} ]</div>')
    b+=ab(60,140,f'<div class="zh" style="font-size:68px;line-height:1.1;letter-spacing:-.01em;white-space:nowrap">{head}</div>')
    b+=body
    b+=tele(60,790,extra_tele or ['SRC REVIEW-PIPE · MODE VERIFY','ORG 0x7F3C · LAT 212MS'],11)
    b+=prog(1340,800,200,fs=11)
    return page(W,H,b,.8)

# FIG1
b='<div class="vl or" style="left:800px;top:240px;bottom:140px;width:2px;background:#FF5A1F"></div>'
b+=ab(60,262,'<div style="font:700 30px Inter;letter-spacing:-.02em">CONSENSUS </div>')
b+=ab(840,262,'<div style="font:700 30px Inter;letter-spacing:-.02em">VERIFICATION </div>')
for i,y in enumerate([400,520,640]):
    b+=node(170,y,f'Model {"ABC"[i]}',f'MODEL-{"ABC"[i]} · VOTE ✓',w=190)
    b+=ab(275,y-12,'<div class="mono" style="font-size:16px;color:#fff">✓</div>')
    b+=line(300,y,540,520)
b+=node(640,520,'Post opinion','POST OPINION',w=180,orange=True)
b+=ab(560,600,'<div class="mono" style="font-size:11px;color:#FF8A5C;line-height:1.7">3/3 AGREE<br>EVIDENCE: NONE</div>')
b+=node(905,520,'One reviewer','ONE REVIEWER',w=160)
b+=node(1105,520,'Server check','SERVER CHECK',w=170)
b+=line(985,520,1020,520); b+=line(1190,520,1225,520)
b+=node(1305,520,'Re-check','RE-CHECK @ PR HEAD',w=160)
b+=line(1385,500,1420,420,orange=True); b+=line(1385,540,1420,620,dash=True)
b+=node(1420,400,'Block','BLOCK',w=120,orange=True,center=False)
b+=node(1420,640,'Drop','DROP',w=120,center=False)
b+=br(1105,520,210,120,False)
render('fig1-consensus-vs-verification',frame('campus.jpg','FIG-01','Nods don\'t count. Evidence does.',b,dim=.45),W,H)

# FIG2  gate.jpg 1280x720 -> 1600x900; barrier y=428, cars x=800 y=315/504/603/720
b='<div class="hl or" style="top:428px;height:2px;background:#FF5A1F"></div>'
b+=ab(60,445,'<div class="chip" style="display:inline-block">PRE-GATE</div><div class="zh" style="font-size:24px;margin-top:12px">Deterministic gates (no model)</div><div class="mono" style="font-size:11px;margin-top:6px;opacity:.75;line-height:1.7">CI GREEN · NO CONFLICT · SIZE OK</div>')
b+=ab(60,620,'<div class="zh" style="font-size:24px">Scheduler, every 3 min</div><div class="mono" style="font-size:11px;margin-top:6px;opacity:.75">SCHEDULER · POLL QUEUE / 180S</div>')
b+=line(330,650,740,690,dash=True)
b+=ab(330,285,'<div class="zh" style="font-size:24px;text-align:right">Server re-check</div><div class="mono" style="font-size:11px;margin-top:6px;opacity:.75;text-align:right">SERVER RE-CHECK</div>')
b+=line(560,315,760,315)
b+=br(800,315,70,90)
b+=target(800,603,70,90,'PR #QUEUED','HOLD / GATE',side='right')
st=[('01','Prepare','REPO TOKEN ONLY',False),('02','Deps + security scan','NO CREDENTIALS',True),('03','Model review','MODEL GATEWAY KEY ONLY',False),('04','Publish','REPO TOKEN ONLY',False)]
b+=ab(1020,262,'<div class="colh zh" style="font-weight:400;font-size:26px">Four stages · isolated credentials</div>')
for i,(n,z,e,o) in enumerate(st):
    y=320+i*104
    b+=ab(1020,y,f'<div style="display:flex;gap:18px;align-items:center;width:520px;height:84px;border:1px solid {"#FF5A1F" if o else "rgba(255,255,255,.35)"};background:rgba(4,18,14,.6);padding:0 18px"><div style="font:700 34px Inter;color:{"#FF5A1F" if o else "#fff"}">{n}</div><div><div class="zh" style="font-size:24px">{z}</div><div class="mono" style="font-size:11px;opacity:.8;margin-top:4px">{e}</div></div></div>')
b+=line(840,315,1010,360,dash=True)
render('fig2-gates-to-isolated-stages',frame('gate.jpg','FIG-02','Gates first, then sealed stages',b,dim=.9),W,H)

# FIG3
b=node(190,500,'One finding','FINDING · P1',w=200,orange=True)
lanes=[(330,'Author appeal','AUTHOR APPEAL','Model re-checks on PR head','RE-CHECK @ HEAD'),(500,'Maintainer ruling','MAINTAINER RULING','Won\'t change + reason','WONTFIX + REASON'),(670,'Defer P1','DEFER P1','Into a qualifying issue','TRACKED ISSUE')]
for i,(y,a,ae,c,ce) in enumerate(lanes):
    b+=line(290,500,560,y)
    b+=ab(1520,y-40,f'<div class="mono" style="font-size:11px;opacity:.6">LANE 0{i+1}</div>','transform:translateX(-100%)')
    b+=node(680,y,a,ae,w=220); b+=line(790,y,1000,y,label='→ CONVERGE')
    b+=node(1140,y,c,ce,w=260)
    b+=f'<div class="hl" style="top:{y}px;left:1270px;right:60px;background:rgba(255,255,255,.4)"></div>'
b+=br(1140,330,300,110,False)
b+=ab(60,740,'<div style="width:1480px;height:44px;background:#FF5A1F;display:flex;align-items:center;justify-content:space-between;padding:0 20px"><span class="zh" style="font-size:24px">P0 can only be fixed</span><span class="mono" style="font-size:13px">P0 · FIX ONLY · NO APPEAL · NO DEFER</span></div>')
render('fig3-three-convergence-paths',frame('campus.jpg','FIG-03','One finding, three ways out',b,dim=.4,extra_tele=['','']).replace('top:790px','top:800px'),W,H)

# FIG4
items=[('8 required checks','8 REQUIRED CHECKS'),('No P0 · P1','NO OPEN P0 / P1'),('All threads resolved','ALL THREADS RESOLVED'),('Maintainer merges','DESIGNATED MAINTAINER MERGE')]
b=''
for i,(z,e) in enumerate(items):
    y=280+i*110
    b+=ab(60,y,f'<div style="display:flex;align-items:center;width:900px;height:86px;border-bottom:1px solid rgba(255,255,255,.3)"><div class="mono" style="width:56px;height:56px;border:2px solid #fff;display:flex;align-items:center;justify-content:center;font-size:28px">✓</div><div class="mono" style="font-size:13px;opacity:.7;margin:0 24px">0{i+1}</div><div class="zh" style="font-size:34px;flex:1">{z}</div><div class="mono" style="font-size:12px;opacity:.8;margin-right:16px">{e}</div><div class="chip" style="font-size:13px">PASS</div></div>')
b+=ab(1080,270,'<div class="chipw">SIDE NOTE</div><br><div class="chip" style="display:inline-block;margin-top:6px">OVERRIDE</div><div class="zh" style="font-size:24px;margin-top:16px;line-height:1.5">Emergency override needs<br>a written reason</div><div class="mono" style="font-size:11px;opacity:.75;margin-top:8px">WRITTEN REASON · PATROL REMINDER</div>')
b+=ab(1060,520,'<div class="giant" style="font-size:250px">8/8</div>')
render('fig4-release-conditions',frame('campus.jpg','FIG-04','Four conditions to release',b,dim=.35),W,H)

