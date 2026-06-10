import os

TPL = r"C:\Users\Administrator\.codex\skills\guizang-ppt-skill\assets\template.html"
OUT = r"D:\codex\backup\skills\skills-catalog.html"

with open(TPL, "r", encoding="utf-8") as f:
    tpl = f.read()

def slide(extra_class, content):
    return f"<section class=\"slide {extra_class}\">\n{content}\n</section>"

def chrome(codex="Skills Pack", right="Codex"):
    return f'''<div class="chrome"><div class="left"><span>{codex}</span><span class="sep"></span><span>#CKB</span></div><div class="right"><span>{right}</span></div></div>'''

def foot(title="Codex Skills Pack"):
    return f'<div class="foot"><span class="title">{title}</span><span>slide</span></div>'

def stat_card(name, desc):
    return f'<div class="stat-card"><div class="stat-label" style="font-family:var(--mono);font-size:.82vw;letter-spacing:0;text-transform:none;opacity:.95">{name}</div><div class="stat-note" style="font-size:.72vw;margin-top:.2vh;opacity:.68">{desc}</div></div>'

# === SLIDES ===
slides_html = ""

# Slide 1: Cover — 卖点聚焦
slides_html += slide("dark hero", f'''
{chrome()}
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:2vh">
  <div class="kicker" data-anim>Codex Skills Pack</div>
  <div class="display-zh" data-anim style="font-size:7.5vw;max-width:85vw">一人搭建<br>全员即用</div>
  <div class="lead" data-anim style="margin-top:2.5vh;font-size:1.15vw;max-width:48vw;opacity:.7">75 个技能 · 拷贝即用 · 覆盖开发全流程</div>
  <div class="kicker" data-anim style="margin-top:5vh">guizang-ppt-skill · Style A</div>
</div>
{foot()}
''')

# Slide 2: 核心卖点
slides_html += slide("light", f'''
{chrome("Value Prop", "Why This Pack")}
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding:0 3vw">
  <div class="h1-zh" data-anim style="text-align:center;margin-bottom:0.5vh;font-size:3.8vw">不必从零搭，拿走就用</div>
  <div class="rule" data-anim="divider"></div>
  <div class="split" style="margin-top:0" data-anim>
    <div style="display:flex;flex-direction:column;gap:1.5vh;justify-content:center">
      <div class="stat-card" style="border:none;padding:1vh 0">
        <div class="stat-nb" style="font-size:3vw">⚡</div>
        <div class="stat-label" style="font-size:.9vw;letter-spacing:.08em">零配置安装</div>
        <div class="stat-note" style="font-size:.8vw">一条命令 75 个技能全部上线<br>不用装插件、不用配环境、不用写胶水</div>
      </div>
      <div class="stat-card" style="border:none;padding:1vh 0">
        <div class="stat-nb" style="font-size:3vw">🧩</div>
        <div class="stat-label" style="font-size:.9vw;letter-spacing:.08em">即开即用的工具箱</div>
        <div class="stat-note" style="font-size:.8vw">视频制作 · 代码分析 · 飞书集成 · 前端设计 · 文档办公<br>覆盖开发者一天工作中的高频场景</div>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:1.5vh;justify-content:center">
      <div class="stat-card" style="border:none;padding:1vh 0">
        <div class="stat-nb" style="font-size:3vw">📦</div>
        <div class="stat-label" style="font-size:.9vw;letter-spacing:.08em">结构化，可带走</div>
        <div class="stat-note" style="font-size:.8vw">每个技能独立文件夹 + SKILL.md<br>想去哪个项目就复制哪个，不用整包带</div>
      </div>
      <div class="stat-card" style="border:none;padding:1vh 0">
        <div class="stat-nb" style="font-size:3vw">🤖</div>
        <div class="stat-label" style="font-size:.9vw;letter-spacing:.08em">Agent 原生友好</div>
        <div class="stat-note" style="font-size:.8vw">Codex / Cline 放目录即用<br>Claude Code / Cursor 也能读 README 后自安装</div>
      </div>
    </div>
  </div>
</div>
{foot()}
''')

# Slide 3: 适合谁用
slides_html += slide("light", f'''
{chrome("Target", "Who Needs This")}
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding:0 3vw">
  <div class="h2-zh" data-anim style="text-align:center;margin-bottom:0.5vh">谁适合这份技能包</div>
  <div class="rule" data-anim="divider"></div>
  <div class="grid-3" style="margin-top:0;gap:3vw" data-anim>
    <div class="stat-card" style="border:none;padding:1.5vh 0">
      <div class="stat-nb" style="font-size:2.2vw">👤 个人开发者</div>
      <div class="stat-note" style="font-size:.85vw;margin-top:.6vh">不用重复造轮子，一个命令装备整条工作流</div>
    </div>
    <div class="stat-card" style="border:none;padding:1.5vh 0">
      <div class="stat-nb" style="font-size:2.2vw">🏢 技术团队</div>
      <div class="stat-note" style="font-size:.85vw;margin-top:.6vh">统一团队的工具集标准，新成员复制即用</div>
    </div>
    <div class="stat-card" style="border:none;padding:1.5vh 0">
      <div class="stat-nb" style="font-size:2.2vw">🔄 跨项目交付</div>
      <div class="stat-note" style="font-size:.85vw;margin-top:.6vh">不再每个项目单独配一遍 agent 指令</div>
    </div>
  </div>
</div>
{foot()}
''')

# Slide 4: 技能总览
slides_html += slide("light", f'''
{chrome("Overview", "75 Skills")}
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding:0 3vw">
  <div class="h1-zh" data-anim style="text-align:center;margin-bottom:0.5vh;font-size:3.8vw">75 个技能 · 9 大分类</div>
  <div class="rule" data-anim="divider"></div>
  <div class="grid-4" style="margin-top:0;gap:1.5vw 3vw" data-anim>
    <div class="stat-card"><div class="stat-nb">15<div class="stat-unit">个</div></div><div class="stat-label">🎬 视频制作</div></div>
    <div class="stat-card"><div class="stat-nb">14<div class="stat-unit">个</div></div><div class="stat-label">🧠 代码理解</div></div>
    <div class="stat-card"><div class="stat-nb">26<div class="stat-unit">个</div></div><div class="stat-label">💬 飞书集成</div></div>
    <div class="stat-card"><div class="stat-nb">4<div class="stat-unit">个</div></div><div class="stat-label">🎨 前端设计</div></div>
    <div class="stat-card"><div class="stat-nb">6<div class="stat-unit">个</div></div><div class="stat-label">📄 文档办公</div></div>
    <div class="stat-card"><div class="stat-nb">2<div class="stat-unit">个</div></div><div class="stat-label">🤖 AI 开发</div></div>
    <div class="stat-card"><div class="stat-nb">1<div class="stat-unit">个</div></div><div class="stat-label">🧪 测试</div></div>
    <div class="stat-card"><div class="stat-nb">7<div class="stat-unit">个</div></div><div class="stat-label">🪄 其他 + 项目</div></div>
  </div>
</div>
{foot()}
''')

def cat_slide(title, items):
    inner = "".join(stat_card(n, d) for n, d in items)
    return slide("light", f'''
{chrome("Skills", title.split("·")[0].strip())}
<div style="flex:1;display:flex;flex-direction:column;padding:0 2vw">
  <div class="h2-zh" data-anim style="margin-bottom:0;font-size:2.8vw">{title}</div>
  <div class="rule" data-anim="divider" style="margin:1vh 0"></div>
  <div class="grid-3" data-anim style="margin-top:1vh;gap:.6vw 2vw">{inner}</div>
</div>
{foot()}
''')

# Slide 5: 视频制作
slides_html += cat_slide("🎬 视频制作 · HyperFrames 生态 (15)", [
    ("hyperframes", "核心 · 视频合成动画"), ("hyperframes-cli", "CLI 工具链"),
    ("hyperframes-media", "TTS/转录/去背景"), ("hyperframes-registry", "注册块管理"),
    ("remotion-to-hyperframes", "Remotion→HF 迁移"), ("website-to-hyperframes", "网站捕获→视频"),
    ("contribute-catalog", "贡献动效块"), ("animejs", "Anime.js 适配"),
    ("css-animations", "CSS 关键帧适配"), ("gsap", "GSAP 适配"),
    ("lottie", "Lottie 动画适配"), ("three", "Three.js 3D 适配"),
    ("typegpu", "WebGPU 粒子适配"), ("waapi", "Web Animations API"),
    ("tailwind", "Tailwind v4 适配"),
])

# Slide 6: 代码理解
slides_html += cat_slide("🧠 代码理解 · Understand 系列 (14)", [
    ("understand", "代码库→知识图谱"), ("understand-chat", "图谱问答"),
    ("understand-dashboard", "可视化仪表盘"), ("understand-diff", "Diff/PR 分析"),
    ("understand-explain", "模块深入解释"), ("understand-knowledge", "LLM 知识库分析"),
    ("understand-onboard", "入职引导"), ("understand-domain", "业务领域提取"),
    ("understand-architecture", "架构层级分析"), ("understand-fix", "缺陷修复"),
    ("understand-optimize", "性能优化"), ("understand-plan", "重构/计划"),
    ("understand-refactor", "坏味道重构"), ("understand-test", "测试建议"),
])

# Slide 7: 飞书集成上
slides_html += cat_slide("💬 飞书集成 · 上 (13)", [
    ("lark-shared", "认证登录/权限"), ("lark-approval", "审批管理"),
    ("lark-apps", "妙搭部署"), ("lark-attendance", "考勤打卡"),
    ("lark-base", "多维表格"), ("lark-calendar", "日历日程"),
    ("lark-contact", "通讯录查人"), ("lark-doc", "云文档"),
    ("lark-drive", "云空间文件"), ("lark-event", "事件监听"),
    ("lark-im", "即时通讯"), ("lark-mail", "邮箱"),
    ("lark-markdown", "Markdown 操作"),
])

# Slide 8: 飞书集成下
slides_html += cat_slide("💬 飞书集成 · 下 (13)", [
    ("lark-minutes", "妙记/AI 产物"), ("lark-okr", "OKR 管理"),
    ("lark-openapi-explorer", "原生 API"), ("lark-sheets", "电子表格"),
    ("lark-skill-maker", "封装自定义 Skill"), ("lark-slides", "幻灯片"),
    ("lark-task", "任务管理"), ("lark-vc", "视频会议"),
    ("lark-vc-agent", "机器人代参会"), ("lark-whiteboard", "画板"),
    ("lark-wiki", "知识库"), ("lark-workflow-meeting-summary", "会议纪要"),
    ("lark-workflow-standup-report", "日程待办"),
])

# Slide 9: 设计 + 办公
slides_html += slide("light", f'''
{chrome("Creative", "Design + Office")}
<div style="flex:1;display:flex;flex-direction:column;padding:0 2.5vw">
  <div class="h1-zh" data-anim style="font-size:3.4vw;margin-bottom:0">🎨 前端设计 · 📄 文档办公</div>
  <div class="rule" data-anim="divider" style="margin:1vh 0"></div>
  <div class="split" style="margin-top:0" data-anim>
    <div>
      <div class="h3-zh" style="font-size:1.6vw;margin-bottom:1vh;opacity:.7">🎨 设计 (4)</div>
      {"".join(stat_card(n, d) for n, d in [
        ("frontend-design","生产级前端界面"),("impeccable","UX 评审打磨"),
        ("brand-guidelines","Anthropic 品牌色"),("theme-factory","10 套主题预设")])}
    </div>
    <div>
      <div class="h3-zh" style="font-size:1.6vw;margin-bottom:1vh;opacity:.7">📄 办公 (6)</div>
      {"".join(stat_card(n, d) for n, d in [
        ("docx","Word 文档"),("pdf","PDF 处理"),("pptx","PowerPoint"),
        ("xlsx","电子表格"),("doc-coauthoring","合作写作"),("internal-comms","内部通讯")])}
    </div>
  </div>
</div>
{foot()}
''')

# Slide 10: AI + 测试 + 其他 + 本项目
slides_html += cat_slide("🤖 AI · 🧪 测试 · 🪄 其他 · 📦 项目 (11)", [
    ("claude-api", "Claude API/Anthropic SDK"), ("mcp-builder", "MCP 服务端搭建"),
    ("webapp-testing", "Playwright 测试"), ("skill-creator", "创建自定义 Skill"),
    ("algorithmic-art", "p5.js 生成艺术"), ("canvas-design", "PNG/PDF 视觉设计"),
    ("web-artifacts-builder", "React 制品构建"), ("slack-gif-creator", "Slack GIF"),
    ("powershell-python-bridge", "编码问题指南"),
    ("impeccable", "界面打磨 · 考核系统"), ("guizang-ppt-skill", "本 PPT 技能"),
])

# Slide 11: 安装指引 — 收尾
slides_html += slide("dark hero", f'''
{chrome("Get Started", "One Command")}
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:2.5vh">
  <div class="display-zh" data-anim style="font-size:5.5vw">现在就带走</div>
  <div class="lead" data-anim style="font-size:1vw;max-width:44vw;opacity:.7;line-height:2;text-align:left;font-family:var(--mono);background:rgba(255,255,255,.06);padding:2.5vh 2.5vw;border-radius:8px">
    # macOS / Linux<br>
    cp -r .codex-skills/* ~/.codex/skills/<br>
    cp -r .codex-skills/lark-* ~/.agents/skills/<br><br>
    # Windows PowerShell<br>
    Copy-Item ".codex-skills/*" "$env:USERPROFILE\.codex\skills\" -Recurse
  </div>
  <div class="kicker" data-anim style="margin-top:3vh">下次新对话即生效 · 无需重启</div>
</div>
{foot()}
''')

# === Inject into template ===
tpl = tpl.replace('[必填] 替换为 PPT 标题 · Deck Title', 'Codex Skills Pack · 一人搭建 全员即用')
tpl = tpl.replace('<!-- SLIDES_HERE -->', slides_html)

# Add auto-flip via keyboard event dispatch (compatible with template's own navigation)
auto_flip = '''
<script>
(function(){
  var autoTimer = null;
  function startAutoFlip(){
    if(autoTimer) clearInterval(autoTimer);
    autoTimer = setInterval(function(){
      window.dispatchEvent(new KeyboardEvent("keydown", {key: "ArrowRight"}));
    }, 8000);
  }
  document.addEventListener("click", function(e){
    if(e.target.closest("#nav") || e.target.closest("#overview")) return;
    var key = e.clientX > window.innerWidth * 0.5 ? "ArrowRight" : "ArrowLeft";
    window.dispatchEvent(new KeyboardEvent("keydown", {key: key}));
    startAutoFlip();
  });
  document.addEventListener("keydown", function(e){
    if(["ArrowRight","ArrowLeft","ArrowUp","ArrowDown","PageUp","PageDown","Home","End"," "].includes(e.key)){
      setTimeout(startAutoFlip, 100);
    }
  });
  startAutoFlip();
})();
</script>
'''

tpl = tpl.replace('</body>', auto_flip + '\n</body>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write(tpl)

print("Done:", OUT)
print("Size:", os.path.getsize(OUT), "bytes")