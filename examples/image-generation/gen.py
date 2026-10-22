import subprocess,os
D=os.path.dirname(os.path.abspath(__file__))
CSS="""*{margin:0;box-sizing:border-box}body{background:#000;color:#fff;font-family:"Helvetica Neue","Inter","PingFang SC","Noto Sans CJK SC",sans-serif;overflow:hidden;position:relative}
.aur{position:absolute;inset:0;overflow:hidden}.aur:before{content:"";position:absolute;inset:-10%;filter:blur(70px);background:radial-gradient(40% 60% at 30% 45%,#7CD844 0,transparent 70%),radial-gradient(35% 55% at 64% 55%,#00BDFF 0,transparent 70%),radial-gradient(30% 40% at 85% 25%,#B6F37C55 0,transparent 70%)}
.aur:after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(0,0,0,.55) 0 6px,transparent 6px 22px,rgba(0,0,0,.25) 22px 30px,transparent 30px 44px)}
.dim{opacity:.4}.wrap{position:absolute;inset:0;padding:80px 90px}
h2{font-size:64px;font-weight:800;line-height:1.15}em{color:#7CD844;font-style:normal}
.card{background:#fff;color:#000;border-radius:28px;padding:36px}.pill{display:inline-block;background:#B6F37C;color:#000;border-radius:99px;padding:8px 22px;font-size:24px;font-weight:700}
.row{display:flex;gap:28px}.sub{font-size:24px;opacity:.7;margin-top:10px}"""
def logo(h=100,c="#fff",w=None):
    hs=[.4,.68,.88,1,.88,.68,.4];w=w or h*.12
    return f'<div style="display:flex;gap:{w*.55}px;align-items:center">'+''.join(f'<i style="display:block;flex:0 0 {w}px;width:{w}px;height:{h*x}px;border-radius:{w}px;background:{c}"></i>' for x in hs)+'</div>'
def mark(s=120): return f'<div style="display:flex;align-items:center;gap:{s*.35}px">{logo(s*.8)}<div style="font-size:{s}px;font-weight:800;letter-spacing:.06em">EXAMPLE</div></div>'
def render(path,w,h,body,aur="aur"):
    html=f'<html><head><meta charset=utf-8><style>{CSS}body{{width:{w}px;height:{h}px}}</style></head><body><div class="{aur}"></div>{body}</body></html>'
    p=os.path.join(D,path);open(p[:-4]+'.html','w').write(html)
    subprocess.run(['google-chrome','--headless=new','--no-sandbox','--hide-scrollbars',f'--window-size={w},{h}',f'--screenshot={p}','file://'+p[:-4]+'.html'],stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
TAG="Listen with care and shape what you imagine."
C='<div class=wrap style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{g}px;text-align:center">{b}</div>'
# covers
render('cn/cover_2350x1000.png',2350,1000,C.format(g=34,b=mark(170)+f'<div style="font-size:76px;font-weight:700">一个免费、开源的游戏音频中间件</div><div style="font-size:40px;opacity:.85">{TAG}</div>'))
render('cn/square_1000x1000.png',1000,1000,C.format(g=0,b=logo(560)))
render('cn/tietu_1080x1440.png',1080,1440,C.format(g=40,b=logo(300)+mark(110)+'<div style="font-size:64px;font-weight:700;line-height:1.35">一个免费、开源的<br>游戏音频中间件</div>'+f'<div style="font-size:32px;opacity:.85">{TAG}</div>'))
# X header safe zone: 200 sides,160 top,120 bottom
render('en/x_header_2000x800.png',2000,800,f'<div style="position:absolute;left:200px;right:200px;top:160px;bottom:120px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px">{mark(130)}<div style="font-size:40px;opacity:.9">{TAG}</div></div>')
# fig1 bridge
def bridge(L,path,needs,a,b,mid,title):
    nd=''.join(f'<div class=card style="padding:30px 34px;font-size:{"32" if L=="cn" else "27"}px;line-height:1.4;font-weight:500"><span class=pill style="font-size:18px;padding:4px 14px;margin-right:12px">0{i+1}</span>{t}</div>' for i,t in enumerate(needs))
    box=lambda t,s='': f'<div style="flex:1;border:2px solid #ffffff55;border-radius:28px;padding:44px;text-align:center;font-size:40px;font-weight:700;background:#00000088{s}">{t}</div>'
    arr='<div style="font-size:54px;color:#7CD844">→</div>'
    render(path,1600,900,f'''<div class=wrap style="display:flex;flex-direction:column;justify-content:center"><h2>{title}</h2><div style="display:flex;flex-direction:column;gap:22px;margin-top:44px">{nd}</div>
<div style="display:flex;align-items:center;gap:24px;margin-top:64px">{box(a)}{arr}<div style="flex:1.2;background:#00BDFF;color:#000;border-radius:28px;padding:40px;display:flex;gap:22px;align-items:center;justify-content:center;font-size:38px;font-weight:800">{logo(56,"#000")}{mid}</div>{arr}{box(b)}</div></div>''','aur dim')
bridge('cn','cn/01_bridge.png',["脚步要根据地面材质自动切换。","战斗音乐要在被Boss发现的时候立即开始播放。","血条快耗尽时，希望全场的声音都变得模糊虚幻，并能听到清晰的心跳声。"],"声音素材","游戏运行逻辑","Example Studio",'搭建<em>声音素材</em>与<em>游戏运行逻辑</em>之间的桥梁')
bridge('en','en/01_bridge.png',["Footsteps need to change automatically depending on the surface.","The battle music needs to start the moment the boss spots the player.","When the player's health is almost gone, I want the whole soundscape to become muffled and dreamlike, with a clear heartbeat cutting through."],"Sound assets","Game logic","Example Studio",'Example <em>Studio</em>')
# fig2 three
def three(path,title,items,fs):
    cs=''.join(f'<div class=card style="flex:1;height:470px;display:flex;flex-direction:column;gap:26px"><div style="font-size:96px;font-weight:800;color:#00BDFF;line-height:1">0{i+1}</div><div style="font-size:{fs}px;font-weight:700;line-height:1.35">{t}</div><div style="margin-top:auto"><span class=pill>{p}</span></div></div>' for i,(p,t) in enumerate(items))
    render(path,1600,900,f'<div class=wrap><h2>{title}</h2><div class=row style="margin-top:70px">{cs}</div></div>','aur dim')
three('cn/02_differences.png','Example Studio <em>与众不同</em>',[("免费","免费，让尝试更容易。"),("开源共创","开源共创，所有开发者一同参与工具的成长。"),("自给自足","自给自足，让团队能自主敏捷迭代。")],40)
three('en/02_differences.png','Example <em>Studio</em>',[("Free","Free to use, easier to try."),("Open-source","Open-source collaboration, with every developer invited to help the tool grow."),("Full source","Full source access, so teams can iterate independently and move quickly.")],32)
# fig3 roadmap
def col(label,items,color,fs,flex=1,dark=False):
    li=''.join(f'<div style="font-size:{fs}px;line-height:1.35;padding:12px 0;border-top:1px solid {"#0002" if not dark else "#fff3"}">{t}</div>' for t in items)
    bg="#fff;color:#000" if not dark else "#000000aa;color:#fff;border:2px solid #ffffff44"
    return f'<div style="flex:{flex};border-radius:24px;padding:26px;background:{bg}"><span class=pill style="background:{color};font-size:22px">{label}</span><div style="margin-top:16px">{li}</div></div>'
render('cn/03_roadmap.png',1600,900,'<div class=wrap style="padding:64px 70px"><h2 style="font-size:56px">走到了<em>哪一步</em></h2><div class=row style="gap:20px;margin-top:34px;align-items:stretch;height:640px">'+
 col("已可体验",["导入 WAV 音频资源、通过不同容器组织声音、进行简单的变量传参","查看和调整音量、音高、循环等基础属性","创建 声音Action，进行试听和打包","通过简易的 Unity SDK 集成"],"#B6F37C",25,1.25)+
 col("灰度测试中",["工程版本升级","Unity SDK 集成"],"#00BDFF",26,.8)+
 col("开发中",["其他游戏引擎的 SDK","Monitor监控","更丰富的音频交互与连接控制能力"],"#7CD844",26,.9)+
 col("规划方向",["AI自然语言会话执行编辑器任务","独立的音频场景搭建和行为预演","音频设计、渲染、烘焙能力并与主流工作站联通","Agent 自动化处理以及业务分析","2D or 3D 真实物理声音或自定义效果","协作配合、平台联动、辅助工具、插件脚本"],"#fff",23,1.1,True)+
 '</div><div style="position:absolute;left:70px;bottom:40px;font-size:26px;opacity:.85">年底或明年年初发布经生产验证的测试版本</div></div>','aur dim')
render('en/03_roadmap.png',1600,900,'<div class=wrap style="padding:56px 60px"><h2 style="font-size:52px">Example <em>Studio</em></h2><div class=row style="gap:16px;margin-top:26px;align-items:stretch;height:660px">'+
 col("Available now",["Import WAV audio assets, organize sounds using different containers, and pass variables for basic control","View and adjust basic properties such as volume, pitch, and looping","Create sound Actions, preview playback, and build packages","Bring sounds into Unity through a basic Unity SDK integration"],"#B6F37C",18,1.05)+
 col("Testing",["Project upgrades between versions and Unity SDK integration are currently undergoing limited internal testing."],"#00BDFF",19,.75)+
 col("In development",["SDKs for other game engines, Monitor functionality, and richer capabilities for audio interaction, connections, and control"],"#7CD844",19,.75)+
 col("Future",["Performing editor tasks through natural-language conversations with AI.","Building standalone audio scenes and previewing their behavior","Providing comprehensive audio design, rendering, and baking capabilities, with integration into major digital audio workstations.","Using effective AI agent automation and business analysis to simplify the entire process from requirements to product.","Offering comprehensive support for physically realistic sound and custom effects in 2D and 3D games.","Supporting related workflow needs, including collaboration, platform integration, companion tools, plugins, and scripts."],"#fff",15,1.45,True)+
 '</div><div style="position:absolute;left:60px;bottom:30px;font-size:21px;opacity:.85">We expect to release a beta version validated in real production environments toward the end of this year or early next year.</div></div>','aur dim')
# fig4 personas
def four(path,title,items,fs):
    ic=lambda i:f'<div style="width:84px;height:84px;border-radius:50%;background:#000;display:flex;align-items:center;justify-content:center">{logo(46,["#00BDFF","#FF8A00","#7CD844","#B6F37C"][i])}</div>'
    cs=''.join(f'<div class=card style="flex:1;height:420px;display:flex;flex-direction:column;gap:30px">{ic(i)}<div style="font-size:{fs}px;font-weight:700;line-height:1.35">{t}</div></div>' for i,t in enumerate(items))
    render(path,1600,900,f'<div class=wrap><h2>{title}</h2><div class=row style="gap:22px;margin-top:80px">{cs}</div></div>','aur dim')
four('cn/04_join.png','欢迎加入<em>共创</em>',["学习游戏开发或声音设计","从事游戏音频工作","筹备新的游戏项目","喜欢写代码"],38)
four('en/04_join.png','Join <em>us</em>',["If you are learning game development or sound design","If you work in game audio","If you are planning a new game project","If you enjoy writing code"],32)
# fig5 contact
def contact(path,title,rows,qr=True):
    rs=''.join(f'<div style="display:flex;gap:30px;padding:20px 0;border-top:1px solid #ffffff33;font-size:34px"><span style="width:190px;opacity:.6;font-size:26px;padding-top:6px">{k}</span><b>{v}</b></div>' for k,v in rows)
    q=f'<div class=card style="padding:20px;width:400px"><img src="file://{D}/qr.png" style="width:100%;display:block"></div>' if qr else ''
    render(path,1600,900,f'<div class=wrap style="display:flex;gap:70px;align-items:center"><div style="flex:1"><div style="margin-bottom:30px">{mark(64)}</div><h2 style="margin-bottom:24px">{title}</h2>{rs}</div>{q}</div>','aur dim')
R=[("Web","example.com"),("GitHub","github.com/example/example-studio"),("Email","support@example.com"),("X","@ExampleStudio")]
contact('cn/05_contact.png','联系<em>我们</em>',R+[("小红书","xhslink.cn/o/5ha3HXV8UOJ")])
contact('en/05_contact.png','Contact',R+[("Xiaohongshu","xhslink.cn/o/5ha3HXV8UOJ")],False)
# fig6 components
def comps(path,title,items,foot,fs):
    cs=''.join(f'<div class=card style="flex:1;height:400px;display:flex;flex-direction:column;gap:22px;{"background:#00BDFF" if n=="Studio" else ""}"><div style="font-size:52px;font-weight:800">{n}</div><div style="font-size:{fs}px;line-height:1.45;font-weight:500">{t}</div></div>' for n,t in items)
    arr=''
    render(path,1600,900,f'<div class=wrap><h2>{title}</h2><div class=row style="gap:22px;margin-top:70px">{cs}</div><div style="margin-top:40px"><span class=pill>{foot}</span></div></div>','aur dim')
comps('cn/06_components.png','Example Studio <em>四个部分</em>',[("Hub","提供 Studio、SDK 的下载与更新"),("Studio","编排声音、设计播放行为，以及试听和打包"),("Engine","核心声音引擎，在游戏运行时执行声音逻辑与播放"),("SDK","暂仅支持Unity<br>连接 Example Studio 与 Unity引擎")],"Apache 2.0",27)
comps('en/06_components.png','Example <em>Studio</em>',[("Hub","Provides downloads and updates for Studio and the SDK."),("Studio","An editor for arranging sounds, designing playback behavior, previewing audio, and building packages."),("Engine","The core audio engine that handles audio logic and playback while the game is running."),("SDK","For Unity Only<br>An integration toolkit that connects Example Studio with Unity.")],"Apache License 2.0",24)
