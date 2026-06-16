"""
你以为的以为 — 概率直觉训练营
"""
import streamlit as st, pandas as pd, numpy as np, plotly.graph_objects as go
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import random, time, re, os

st.set_page_config(page_title="你以为的以为",page_icon="🤔",layout="wide",initial_sidebar_state="expanded")
ROOT=Path(__file__).resolve().parent; ASSETS=ROOT/"assets"; DATA_DIR=ROOT/"data"

# 加载 .env 配置
load_dotenv(ROOT/".env")
AI_KEY = os.getenv("DEEPSEEK_API_KEY", "")
AI_BASE = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

def get_ai_client():
    if not AI_KEY or AI_KEY == "your_api_key_here":
        return None
    return OpenAI(api_key=AI_KEY, base_url=AI_BASE)

st.markdown("""<style>
.stApp{background-color:#0E1117}.main .block-container{padding-top:1rem}
.stButton>button{border-radius:8px;font-weight:600;transition:all .2s}
#MainMenu{visibility:hidden}footer{visibility:hidden}[data-testid="stDecoration"]{display:none}
hr{border-color:#2A2D35;margin:24px 0}
.gacha-card{display:inline-block;width:42px;height:56px;border-radius:6px;margin:2px;text-align:center;line-height:56px;font-weight:700;font-size:14px;transition:all .3s}
.gacha-SSR{background:linear-gradient(135deg,#F0B90B,#FFD700);color:#0E1117;box-shadow:0 0 16px rgba(240,185,11,.6);animation:ssrPulse .6s ease-in-out 3}
.gacha-SR{background:linear-gradient(135deg,#7B2D8E,#9B59B6);color:#fff;box-shadow:0 0 8px rgba(155,89,182,.4)}
.gacha-R{background:linear-gradient(135deg,#2A4A7F,#4A90D9);color:#fff}
@keyframes ssrPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.15);box-shadow:0 0 24px rgba(240,185,11,.9)}}
.avatar-icon{display:inline-block;width:38px;height:38px;border-radius:50%;background:#1A1D24;text-align:center;line-height:38px;font-size:20px;margin:3px;transition:all .3s;border:1px solid #2A2D35}
.avatar-icon.collision{border-color:#F0B90B;box-shadow:0 0 12px rgba(240,185,11,.6);animation:collisionPulse .4s ease-in-out 3}
@keyframes collisionPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.3)}}
</style>""",unsafe_allow_html=True)

# ── Session State ──
for k,v in {"coins":1000,"achievements":[],"games_completed":{},"game_scores":{},"radar_scores":{"独立直觉":0,"条件思维":0,"样本警觉":0,"大数感觉":0,"混淆嗅觉":0,"贝叶斯脑":0,"因果链条":0,"估计智慧":0,"维度直觉":0},"history":[],"current_game":"lobby"}.items():
    if k not in st.session_state: st.session_state[k]=v

CHAPTER_COLORS={"chapter1":"#F0B90B","chapter2":"#00B4D8","chapter3":"#E07B39","chapter4":"#9B59B6"}
GAME_META={1:{"title":"传说之魂","subtitle":"终极召唤","chapter":1,"icon":"🎮"},2:{"title":"密室秘钥","subtitle":"三把锁，一把钥匙","chapter":1,"icon":"🔒"},3:{"title":"撞头像","subtitle":"有多少人跟你撞了？","chapter":1,"icon":"🎨"},4:{"title":"翻倍陷阱","subtitle":"期望为正却注定破产的赌局","chapter":1,"icon":"🪙"},5:{"title":"天才的诅咒","subtitle":"新秀墙还是运气？","chapter":2,"icon":"⚽"},6:{"title":"两个神医","subtitle":"该找谁看病？","chapter":2,"icon":"🏥"},7:{"title":"沉默的大多数","subtitle":"你看到的只是幸存者","chapter":2,"icon":"💸"},8:{"title":"阳性","subtitle":"你应该恐慌吗？","chapter":2,"icon":"🩺"},9:{"title":"离奇档案","subtitle":"当你发现了惊天秘密","chapter":3,"icon":"📁"},10:{"title":"鸡与蛋","subtitle":"谁是因，谁是果？","chapter":3,"icon":"🐔"},11:{"title":"幕后黑手","subtitle":"真凶另有其人","chapter":3,"icon":"🕵️"},12:{"title":"星光错觉","subtitle":"选角的秘密","chapter":3,"icon":"🌟"},13:{"title":"收缩魔法","subtitle":"把无关的东西拉在一起反而更准？","chapter":4,"icon":"🪄"},14:{"title":"空心球","subtitle":"这个世界只有皮","chapter":4,"icon":"🍉"},15:{"title":"无法区分的人","subtitle":"混在一起的两群人","chapter":4,"icon":"👥"}}

# ── AI 系统提示词 ──
AI_SYSTEM_PROMPTS = {
    "lobby": """你是一个概率与统计思维训练平台的 AI 导师，名为「以为解药」。你的风格是：生动、有洞见、善于用生活中的类比解释抽象概念。

这个平台包含 15 个互动游戏，分为 4 章：
1. 赌徒的直觉（游戏1-4）：几何分布/无记忆性、蒙提霍尔问题、生日悖论、非各态历经性
2. 真相猎人的调查（游戏5-8）：回归均值、辛普森悖论、幸存者偏差、贝叶斯定理/基础率谬误
3. 因果侦探事务所（游戏9-12）：虚假相关/多重比较、反向因果、混杂变量、对撞偏差
4. 换个维度看世界（游戏13-15）：詹姆斯-斯坦悖论、高维几何直觉、维度诅咒

请用中文回答，保持回答简洁有力（控制在 300 字以内），用类比帮助理解。当你觉得需要时，可以适当使用 LaTeX 数学公式。""",

    1: """你是「以为解药」，正在为玩家讲解游戏1「传说之魂」——关于几何分布与无记忆性。

核心概念：
- 每次抽卡是独立的，概率不会"累积"。SSR 出率 1%，期望 100 次，但 P50 约 69 次。
- 「垫刀」是赌徒谬误——硬币没有记忆。
- 几何分布的无记忆性：P(X > k+m | X > k) = P(X > m)

请用中文回应玩家的问题，结合抽卡/游戏的类比，帮助建立"独立事件"的直觉。""",

    2: """你是「以为解药」，正在为玩家讲解游戏2「密室秘钥」——蒙提霍尔问题。

核心概念：
- 三扇门，一扇有钥匙。你选一扇，主持人打开另一扇空门。
- 换门胜率 2/3，不换 1/3。关键在于主持人的行为携带信息——他永远不会打开有钥匙的门。
- 这是贝叶斯更新的经典案例。

请用中文回应，用"主持人知道答案"这个关键点帮助玩家理解为什么不是五十五十。""",

    3: """你是「以为解药」，正在为玩家讲解游戏3「撞头像」——生日悖论。

核心概念：
- 80 个头像，23 人就超过 50% 碰撞概率。
- 比较的不是某个特定的人跟你相同，而是所有 C(N,2) 对人中任意一对相同。
- P(碰撞) ≈ 1 - e^(-N(N-1)/160)

请用中文回应，帮助玩家理解"组合爆炸"的力量——配对数量增长远远快于人数增长。""",

    4: """你是「以为解药」，正在为玩家讲解游戏4「翻倍陷阱」——非各态历经性。

核心概念：
- 每次抛硬币：正面×1.5，反面×0.6。算术期望 +5%，但几何平均 √(1.5×0.6) ≈ 0.949 < 1。
- 系综平均（平行宇宙的平均）≠ 时间平均（你反复玩的实际路径）。
- 这就是非各态历经性：期望为正的游戏，反复 All-in 却必然破产。

请用中文回应，用"你只能活一次"这个角度解释为什么期望值不是唯一重要的东西。""",

    5: """你是「以为解药」，正在为玩家讲解游戏5「天才的诅咒」——回归均值。

核心概念：
- 观测值 = 真实能力 + 随机运气。第一赛季的高分往往是好运气站在了中等能力上。
- 第二赛季运气重抽，极值自然回弹——这就是回归均值。
- 这不是"诅咒"，不是"新秀墙"——只是统计规律。

请用中文回应，帮助玩家区分"信号"和"噪声"，理解为什么极端值倾向于向均值回落。""",

    6: """你是「以为解药」，正在为玩家讲解游戏6「两个神医」——辛普森悖论。

核心概念：
- 华大夫总体治愈率 83%，张大夫 78%。但每种病张大夫都更好。
- 原因：华大夫收了更多轻症（容易治），张大夫收了更多重症（难治）。病人结构不同导致了总体反转。
- 分组比较时，分组变量必须在"治疗前"就存在，否则会引入新的偏差。

请用中文回应，帮助玩家建立"看数据先看分层"的思维习惯。""",

    7: """你是「以为解药」，正在为玩家讲解游戏7「沉默的大多数」——幸存者偏差。

核心概念：
- 你只看到 50 个成功的学员在发声，看不到 9,950 个沉默的失败者。
- 失败者不会写好评、不会发帖、不会告诉你"我被割了"。
- 真实成功率 0.5%，但你看到的好评率 100%。

请用中文回应，帮玩家养成"每次看到成功案例，先问失败的人在哪"的思维习惯。""",

    8: """你是「以为解药」，正在为玩家讲解游戏8「阳性」——贝叶斯定理与基础率谬误。

核心概念：
- 检测准确率 99%，但罕见病发病率仅 0.1%。阳性后真正患病的概率只有约 9%。
- P(患病|阳性) ≠ P(阳性|患病)。99% 准确率说的是后者。
- 贝叶斯定理：后验概率 = 似然 × 先验 / 证据。先验（基础率）非常重要。

请用中文回应，帮助玩家理解"条件概率的方向不能互换"。""",

    9: """你是「以为解药」，正在为玩家讲解游戏9「离奇档案」——虚假相关与多重比较。

核心概念：
- 两条曲线高度同步 ≠ 因果关系。常见结构是 X ← Z → Y（第三变量同时驱动两者）。
- 翻足够多的变量，总能找到"显著"的虚假关联（多重比较 / p-hacking）。
- 相关是对称的（Corr(X,Y)=Corr(Y,X)），但因果不是。

请用中文回应，帮玩家建立"相关≠因果"的直觉，鼓励他们追问"有没有第三个变量"。""",

    10: """你是「以为解药」，正在为玩家讲解游戏10「鸡与蛋」——反向因果。

核心概念：
- 戴眼镜的人智商更高 → 不是眼镜让人聪明，而是高智商→更爱学习→更容易近视。
- 消防员越多损失越大 → 不是消防员导致损失，而是大火→派出更多消防员。
- 住院越久死亡率越高 → 不是住院害人，而是病情重→住院久→死亡率高。

请用中文回应，帮助玩家养成"看到相关先问因果方向"的习惯，强调时间顺序的重要性。""",

    11: """你是「以为解药」，正在为玩家讲解游戏11「幕后黑手」——遗漏变量/混杂偏差。

核心概念：
- 咖啡与心脏病相关，但真正驱动两者的是"长期熬夜"。
- DAG 结构：咖啡(X) ← 长期熬夜(Z) → 心脏病(Y)
- 如果不控制 Z，X 和 Y 之间的虚假关联会被误认为因果。

请用中文回应，帮助玩家理解"每当你看到两个变量相关，先问有没有第三个变量在背后"。""",

    12: """你是「以为解药」，正在为玩家讲解游戏12「星光错觉」——对撞偏差/选择偏差。

核心概念：
- 在全体报名者中，颜值和演技完全独立（r≈0）。
- 但只选"总分够高"的被录取者时，颜值和演技出现虚假负相关。
- 控制一个对撞变量（是否被录取），在两个独立变量间凭空创造了关联。

请用中文回应，解释"按结果筛选样本会扭曲变量之间的关系"这个反直觉的现象。""",

    13: """你是「以为解药」，正在为玩家讲解游戏13「收缩魔法」——詹姆斯-斯坦悖论。

核心概念：
- 同时估计多个参数时，把每个参数的估计值都往总体均值"缩"一点，反而整体更准。
- MLE（直接用样本均值）无偏但方差大；JS 收缩引入一点偏差，但大幅降低方差。
- MSE = 方差 + 偏差²。当 d≥3 时，JS 的风险严格低于 MLE。
- 这叫"偏差-方差权衡"——有时候，有偏的估计反而比无偏的好。

请用中文回应，帮助玩家建立"估计不是越'纯粹'越好"的思维。""",

    14: """你是「以为解药」，正在为玩家讲解游戏14「空心球」——高维几何直觉。

核心概念：
- 高维高斯分布中，几乎所有点都集中在半径 √d 的薄壳上，球内部几乎是空的。
- 变异系数随维度趋于 0——所有点到原点的距离几乎相同。
- "西瓜皮现象"：d=1000 时，最外层 1% 半径的皮占总体积的 99.99%+。

请用中文回应，帮助玩家理解"高维空间完全不像低维"，建立对维度诅咒的直觉。""",

    15: """你是「以为解药」，正在为玩家讲解游戏15「无法区分的人」——维度诅咒与线性可分。

核心概念：
- 在低维（2维）中完全混在一起的两群人，加入足够多随机噪声维度后，变得几乎完美线性可分。
- Cover 定理：N 个点在 d 维空间中，随机超平面可分的概率随 d 增大。当 d > N 时几乎一定可分。
- 这就是"维度祝福"的另一面——高维既可以让距离失效，也可以让分类变得极其容易。

请用中文回应，帮助玩家理解"高维空间的几何直觉完全不同于低维"。"""
}

PLOTLY_DARK={"plot_bgcolor":"#1A1D24","paper_bgcolor":"#1A1D24","font":{"color":"#E4E6EB"},"xaxis":{"gridcolor":"#2A2D35"},"yaxis":{"gridcolor":"#2A2D35"}}

def add_coins(n): st.session_state.coins+=n
def check_achievement(a):
    if a not in st.session_state.achievements: st.session_state.achievements.append(a); return True
    return False
def complete_game(gid,score=1): st.session_state.games_completed[str(gid)]=True
def update_radar(dim,score): st.session_state.radar_scores[dim]=max(st.session_state.radar_scores.get(dim,0),score)

def top_nav(gid):
    meta=GAME_META[gid];ch=meta["chapter"];color=list(CHAPTER_COLORS.values())[ch-1]
    ch_names=["","赌徒的直觉","真相猎人的调查","因果侦探事务所","换个维度看世界"]
    c1,c2,c3=st.columns([0.5,2,1])
    with c1:
        if st.button("☰ 大厅",key=f"tn_home_{gid}",use_container_width=True): st.session_state.current_game="lobby";st.rerun()
    with c2: st.markdown(f"<span style='color:{color};font-weight:600;'>第{ch}章·{ch_names[ch]}</span> <span style='color:#8B8F98;'>| {meta['icon']} 游戏{gid}/15·{meta['title']}</span>",unsafe_allow_html=True)
    with c3:
        cp,cn=st.columns(2)
        if cp.button("◀",key=f"tn_prev_{gid}",use_container_width=True): st.session_state.current_game=str(max(1,gid-1));st.rerun()
        if cn.button("▶",key=f"tn_next_{gid}",use_container_width=True): st.session_state.current_game=str(min(15,gid+1));st.rerun()

def chapter_banner(gid):
    meta=GAME_META[gid];ch=meta["chapter"];color=list(CHAPTER_COLORS.values())[ch-1]
    ch_names=["","赌徒的直觉","真相猎人的调查","因果侦探事务所","换个维度看世界"];ch_icons=["","🏕️","🏥","🔎","🌌"]
    st.markdown(f"""<div style="background:linear-gradient(90deg,{color}18 0%,{color}08 50%,transparent 100%);border-left:3px solid {color};padding:12px 20px;border-radius:0 8px 8px 0;margin-bottom:20px;display:flex;align-items:center;gap:12px;"><span style="font-size:24px;">{ch_icons[ch]}</span><div><span style="color:{color};font-weight:700;font-size:14px;">第{ch}章·{ch_names[ch]}</span><span style="color:#8B8F98;font-size:14px;margin-left:8px;">{meta['icon']} 游戏{gid}/15·{meta['title']}</span></div><div style="flex:1;"></div><span style="color:#8B8F98;font-size:12px;">{meta['subtitle']}</span></div>""",unsafe_allow_html=True)

def reveal_box(title,content,metaphor,ai_context="",gid=0):
    st.markdown("---")
    st.markdown(f"""<div class="reveal-box"><h2 style="color:#F0B90B;margin-bottom:16px;">🔍 {title}</h2><p style="font-size:16px;line-height:1.8;color:#E4E6EB;">{content}</p><div style="background:#1A1D24;border-radius:8px;padding:16px;margin-top:16px;"><span style="color:#8B8F98;">🎭 </span><span style="color:#E4E6EB;font-style:italic;">{metaphor}</span></div></div>""",unsafe_allow_html=True)

def math_detail(formula):
    with st.expander("📐 数学细节"): st.markdown(formula)

def reset_game(prefix: str):
    for key in list(st.session_state.keys()):
        if key.startswith(prefix):
            del st.session_state[key]

# ═══════════════════════════════════════════════════════════
# LOBBY
# ═══════════════════════════════════════════════════════════
def show_lobby():
    logo=ASSETS/"logo.png"
    if logo.exists(): st.image(str(logo),width=160)
    st.markdown("""<h1 style="font-size:42px;margin-bottom:0;color:#E4E6EB;">你<span style="color:#F0B90B;">以为</span>的以为</h1><p style="color:#8B8F98;font-size:16px;">训练你的概率直觉，识破统计陷阱，破解因果迷思</p>""",unsafe_allow_html=True)
    st.markdown("---")
    c1,c2,c3,c4=st.columns(4)
    n_done=len(st.session_state.games_completed)
    c1.metric("💰 金币",st.session_state.coins);c2.metric("🏆 成就",f"{len(st.session_state.achievements)}/16")
    c3.metric("🎮 已完成",f"{n_done}/15");c4.metric("📊 总流水",sum(abs(h.get("coins_change",0)) for h in st.session_state.history))
    st.markdown("---")
    col_r,col_c=st.columns([1,1])
    with col_r:
        st.subheader("🎯 直觉雷达")
        scores=st.session_state.radar_scores;dims=list(scores.keys());vals=list(scores.values())
        fig=go.Figure(data=go.Scatterpolar(r=vals+[vals[0]],theta=dims+[dims[0]],fill='toself',fillcolor='rgba(240,185,11,0.2)',line=dict(color='#F0B90B',width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0,5],gridcolor='#2A2D35',color='#8B8F98'),angularaxis=dict(gridcolor='#2A2D35',color='#E4E6EB'),bgcolor='#1A1D24'),**PLOTLY_DARK,height=380,margin=dict(l=40,r=40,t=20,b=20))
        st.plotly_chart(fig,use_container_width=True)
    with col_c:
        st.subheader("📖 章节选择")
        for icon,name,count,color,games in [("🏕️","第一章·赌徒的直觉","4个游戏","#F0B90B",[1,2,3,4]),("🏥","第二章·真相猎人的调查","4个游戏","#00B4D8",[5,6,7,8]),("🔎","第三章·因果侦探事务所","4个游戏","#E07B39",[9,10,11,12]),("🌌","第四章·换个维度看世界","3个游戏","#9B59B6",[13,14,15])]:
            done=sum(1 for g in games if str(g) in st.session_state.games_completed)
            next_g=next((g for g in games if str(g) not in st.session_state.games_completed),games[0])
            with st.container(border=True):
                st.markdown(f"""<div style="display:flex;align-items:center;gap:8px;padding:8px 0;"><span style="font-size:20px;">{icon}</span><div style="flex:1;"><span style="color:#E4E6EB;font-weight:600;">{name}</span><span style="color:#8B8F98;font-size:12px;margin-left:8px;">{done}/{len(games)} 完成</span></div></div>""",unsafe_allow_html=True)
                st.progress(done/len(games))
                if st.button("▶ 进入",key=f"ch_{icon}"): st.session_state.current_game=str(next_g);st.rerun()

# ═══════════════════════════════════════════════════════════
# 游戏 1: 传说之魂
# ═══════════════════════════════════════════════════════════
def show_game_01():
    top_nav(1);chapter_banner(1)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#1a1a10 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🎮</span><div><h3 style="color:#F0B90B;margin:0 0 8px 0;">传说之魂 —— 终极召唤</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">你心心念念那个 <b style="color:#F0B90B;">SSR 传说角色</b>，出率 <b>1%</b>。<br>💬 <i>"垫了这么多刀，差不多该出了吧？"</i><br>——真的吗？</p></div></div></div>""",unsafe_allow_html=True)
    if "g01_pulls" not in st.session_state: st.session_state.g01_pulls=0;st.session_state.g01_ssr_at=None;st.session_state.g01_history=[];st.session_state.g01_revealed=False
    ssr_rate=0.01
    st.markdown("### 🎯 召唤阵")
    cp1,cp2=st.columns([2,1])
    pull_n=0
    with cp1:
        cc=st.columns(4)
        if cc[0].button("🔮 1连抽",use_container_width=True): pull_n=1
        if cc[1].button("🔮 10连抽 🔥",use_container_width=True): pull_n=10
        if cc[2].button("🔮 50连抽",use_container_width=True): pull_n=50
        if cc[3].button("🔮 100连抽",use_container_width=True): pull_n=100
    with cp2:
        st.metric("📦 已抽次数",st.session_state.g01_pulls)
        if st.session_state.g01_ssr_at: st.metric("⭐ SSR 第几次出",st.session_state.g01_ssr_at)
    if pull_n>0 and not st.session_state.g01_revealed:
        for _ in range(pull_n):
            st.session_state.g01_pulls+=1;roll=np.random.random()
            if roll<ssr_rate: st.session_state.g01_history.append("SSR")
            elif roll<0.10: st.session_state.g01_history.append("SR")
            else: st.session_state.g01_history.append("R")
            if st.session_state.g01_ssr_at is None and st.session_state.g01_history[-1]=="SSR": st.session_state.g01_ssr_at=st.session_state.g01_pulls
        st.rerun()
    if st.session_state.g01_history:
        st.markdown("#### 🃏 抽卡记录")
        show_n=min(30,len(st.session_state.g01_history));recent=st.session_state.g01_history[-show_n:]
        cards="".join(f'<div class="gacha-card gacha-{r}">{chr(9733) if r=="SSR" else chr(9670) if r=="SR" else chr(9679)}</div>' for r in recent)
        st.markdown(f'<div style="line-height:1;">{cards}</div>',unsafe_allow_html=True)
        cnts={r:st.session_state.g01_history.count(r) for r in ["SSR","SR","R"]}
        st.markdown(f"<span style='color:#F0B90B;'>★ SSR×{cnts['SSR']}</span> <span style='color:#9B59B6;'>◆ SR×{cnts['SR']}</span> <span style='color:#4A90D9;'>● R×{cnts['R']}</span> <span style='color:#8B8F98;'>| 总计 {st.session_state.g01_pulls} 抽</span>",unsafe_allow_html=True)
    if st.session_state.g01_ssr_at:
        st.markdown("---");st.markdown("#### 📊 运气排第几？")
        x=np.arange(1,400);cdf=1-(1-ssr_rate)**x
        p50=int(np.ceil(np.log(0.5)/np.log(1-ssr_rate)));p90=int(np.ceil(np.log(0.1)/np.log(1-ssr_rate)))
        pct=int((1-(1-ssr_rate)**st.session_state.g01_ssr_at)*100)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=x,y=cdf,mode='lines',line=dict(color='#F0B90B',width=3),fill='tozeroy',fillcolor='rgba(240,185,11,0.08)'))
        fig.add_vline(x=p50,line_dash="dash",line_color="#00D4AA",annotation_text=f"P50={p50}次")
        fig.add_vline(x=p90,line_dash="dash",line_color="#00B4D8",annotation_text=f"P90={p90}次")
        fig.add_vline(x=st.session_state.g01_ssr_at,line_color="#FF4757",line_width=3,annotation_text=f"你={st.session_state.g01_ssr_at}次")
        fig.update_layout(**PLOTLY_DARK,height=320,xaxis_title="抽卡次数",yaxis_title="至少出货一次的概率",xaxis_range=[0,max(st.session_state.g01_ssr_at+50,100)])
        st.plotly_chart(fig,use_container_width=True)
        st.markdown(f"<div style='text-align:center;font-size:48px;font-weight:800;color:#F0B90B;'>{pct}<span style='font-size:16px;color:#8B8F98;'> 百分位</span></div>",unsafe_allow_html=True)
        if not st.session_state.g01_revealed:
            st.markdown("#### 🤔 朋友说'快了快了，概率会累积的'——对吗？")
            ccy,ccn=st.columns(2)
            if ccy.button("✅ 对",key="g01_y",use_container_width=True): st.session_state.g01_revealed=True;st.rerun()
            if ccn.button("❌ 不对",key="g01_n",use_container_width=True): st.session_state.g01_revealed=True;st.rerun()
        if st.session_state.g01_revealed:
            reveal_box("每一次抽卡都是独立的——「垫刀」只是幻觉",f"你抽了 <b>{st.session_state.g01_ssr_at}</b> 次，排在第 <b>{pct}</b> 百分位。几何分布的尾巴就是这么长。<br>P50={p50}次，P90={p90}次。<b>1% 概率 ≠ 100 次必出。</b>","\"垫刀\"是游戏公司写在你脑子里的代码。每次抽卡都是全新的——硬币没有记忆。",f"SSR概率1%，玩家抽了{st.session_state.g01_ssr_at}次，P50={p50},P90={p90}。",1)
            math_detail("**几何分布** $$P(X=k)=(1-p)^{k-1}p$$ **累积概率** $$P(X\\le k)=1-(1-p)^k$$ **期望** $$E[X]=1/p=100$$ **P50** $$\\approx 69$$ **无记忆性** $$P(X>k+m\\mid X>k)=P(X>m)$$")
            if st.button("🔄 重启",use_container_width=True,type="primary"):
                for k in list(st.session_state.keys()):
                    if k.startswith("g01_"): del st.session_state[k]
                st.rerun()
            complete_game(1);update_radar("独立直觉",3)

# ═══════════════════════════════════════════════════════════
# 游戏 2: 密室秘钥
# ═══════════════════════════════════════════════════════════
def show_game_02():
    top_nav(2);chapter_banner(2)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#1a1510 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🔒</span><div><h3 style="color:#F0B90B;margin:0 0 8px 0;">密室秘钥 —— 三把锁，一把钥匙</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">三个密码锁盒——<b>只有一个藏着大门钥匙</b>。你选了一个。<br>📢 广播：<i>"给你一个提示。"</i> 主持人打开另一个空盒。<br>💬 A："换啊！" 💬 B："别换，五十五十！"</p></div></div></div>""",unsafe_allow_html=True)
    if "g02_phase" not in st.session_state: st.session_state.g02_phase="story";st.session_state.g02_strategy=None;st.session_state.g02_results=[]
    if st.session_state.g02_phase=="story":
        c1,c2,c3=st.columns(3)
        if c1.button("🚫 打死不换",key="g02_stay",use_container_width=True): st.session_state.g02_strategy="stay";st.session_state.g02_phase="auto_sim";st.rerun()
        if c2.button("🔄 每次都换",key="g02_switch",use_container_width=True): st.session_state.g02_strategy="switch";st.session_state.g02_phase="auto_sim";st.rerun()
        if c3.button("🤔 手动一局",key="g02_manual",use_container_width=True): st.session_state.g02_phase="manual_play";st.rerun()
    elif st.session_state.g02_phase=="manual_play":
        st.markdown("### 🎮 手动模式")
        if "g02_mstate" not in st.session_state: st.session_state.g02_mstate="choose"
        if st.session_state.g02_mstate=="choose":
            cc=st.columns(3)
            for i,cl in enumerate(cc):
                with cl:
                    st.markdown(f"""<div style="background:#1A1D24;border:2px solid #2A2D35;border-radius:16px;padding:24px;text-align:center;"><span style="font-size:48px;">🔒</span><br><span style="color:#E4E6EB;">{i+1}号盒</span></div>""",unsafe_allow_html=True)
                    if st.button(f"选{i+1}号",key=f"g02_mc_{i}",use_container_width=True):
                        st.session_state.g02_mchoice=i;st.session_state.g02_mcar=np.random.randint(0,3)
                        avail=[j for j in range(3) if j!=i and j!=st.session_state.g02_mcar]
                        st.session_state.g02_mreveal=avail[np.random.randint(0,len(avail))]
                        st.session_state.g02_mstate="decide";st.rerun()
        elif st.session_state.g02_mstate=="decide":
            ch=st.session_state.g02_mchoice;rv=st.session_state.g02_mreveal
            for i in range(3):
                with st.columns(3)[i]:
                    if i==rv: st.markdown(f"""<div style="background:#1a1015;border:2px solid #FF4757;border-radius:16px;padding:24px;text-align:center;opacity:.7;"><span style="font-size:48px;">📦</span><br><span style="color:#FF4757;">空的！</span></div>""",unsafe_allow_html=True)
                    elif i==ch: st.markdown(f"""<div style="background:#1a1a10;border:2px solid #F0B90B;border-radius:16px;padding:24px;text-align:center;box-shadow:0 0 12px rgba(240,185,11,.4);"><span style="font-size:48px;">🔒</span><br><span style="color:#F0B90B;">👈 你的选择</span></div>""",unsafe_allow_html=True)
                    else: st.markdown(f"""<div style="background:#1A1D24;border:2px solid #00D4AA;border-radius:16px;padding:24px;text-align:center;"><span style="font-size:48px;">🔒</span><br><span style="color:#00D4AA;">未打开</span></div>""",unsafe_allow_html=True)
            ca,cb=st.columns(2)
            if ca.button("🔄 换！",key="g02_sw",use_container_width=True,type="primary"):
                final=next(j for j in range(3) if j!=ch and j!=rv)
                st.session_state.g02_mwin=(final==st.session_state.g02_mcar);st.session_state.g02_mstate="result";st.rerun()
            if cb.button("🚫 不换",key="g02_st",use_container_width=True):
                st.session_state.g02_mwin=(ch==st.session_state.g02_mcar);st.session_state.g02_mstate="result";st.rerun()
        elif st.session_state.g02_mstate=="result":
            car=st.session_state.g02_mcar
            for i in range(3):
                with st.columns(3)[i]:
                    if i==car: st.markdown(f"""<div style="background:#0a1a15;border:2px solid #00D4AA;border-radius:16px;padding:24px;text-align:center;box-shadow:0 0 20px rgba(0,212,170,.5);"><span style="font-size:48px;">🗝️</span><br><span style="color:#00D4AA;">钥匙在这！</span></div>""",unsafe_allow_html=True)
                    else: st.markdown(f"""<div style="background:#1a1015;border:2px solid #FF4757;border-radius:16px;padding:24px;text-align:center;opacity:.5;"><span style="font-size:48px;">📦</span><br><span style="color:#FF4757;">空的</span></div>""",unsafe_allow_html=True)
            st.success("✅ 逃出去了！" if st.session_state.g02_mwin else "❌ 困住了…")
            if st.button("▶ 用策略模拟50局",key="g02_goto_auto",use_container_width=True,type="primary"): st.session_state.g02_strategy="switch";st.session_state.g02_phase="auto_sim";st.rerun()
    elif st.session_state.g02_phase=="auto_sim":
        strategy=st.session_state.g02_strategy;st.markdown(f"### 📊 策略：{'🚫 打死不换' if strategy=='stay' else '🔄 每次都换'}")
        n_rounds=st.radio("模拟局数",[10,50,200],horizontal=True,key="g02_r")
        if st.button("▶ 开始模拟！",key="g02_start",type="primary",use_container_width=True):
            results=[]
            for _ in range(n_rounds):
                key_pos=np.random.randint(0,3);first_pick=np.random.randint(0,3)
                candidates=[j for j in range(3) if j!=first_pick and j!=key_pos]
                host_opens=candidates[np.random.randint(0,len(candidates))]
                final_pick=next(j for j in range(3) if j!=first_pick and j!=host_opens) if strategy=="switch" else first_pick
                results.append(final_pick==key_pos)
            st.session_state.g02_results=results;st.session_state.g02_phase="reveal";st.rerun()
    elif st.session_state.g02_phase=="reveal":
        results=st.session_state.g02_results;wins=sum(results);rate=wins/len(results)*100
        strategy=st.session_state.g02_strategy;st.markdown(f"### 📊 {wins}/{len(results)} 逃脱 → {rate:.1f}%")
        cum_rates=np.cumsum(results)/np.arange(1,len(results)+1)*100
        fig=go.Figure()
        fig.add_trace(go.Scatter(y=cum_rates,mode='lines',line=dict(color='#F0B90B',width=2.5),name='你的逃脱率'))
        fig.add_hline(y=66.7,line_dash="dash",line_color="#00D4AA",annotation_text="换盒理论66.7%")
        fig.add_hline(y=33.3,line_dash="dash",line_color="#FF4757",annotation_text="不换理论33.3%")
        fig.update_layout(**PLOTLY_DARK,height=320,xaxis_title="局数",yaxis_title="逃脱率(%)",yaxis_range=[0,100])
        st.plotly_chart(fig,use_container_width=True)
        reveal_box("两选一不是五十五十——主持人知道答案",f"你的逃脱率：<b>{rate:.1f}%</b>。<br>主持人<b>不是随机开盒</b>——他知道钥匙在哪。<br>初选正确概率=1/3。换盒=2/3。<b>差一倍。</b>","帮你排除错误选项的人，才是关键。生活中换赛道——重点不是'换'，而是有没有人给了你新信息。",f"策略={'换盒' if strategy=='switch' else '不换'}，逃脱率={rate:.1f}%,{len(results)}局。",2)
        math_detail("**贝叶斯推导** $$P(C=K)=\\frac{1}{3}$$ 主持人永远不开有钥匙的盒子 → $$P(\\text{换盒赢})=\\frac{2}{3}$$")
        if st.button("🔄 换个策略",key="g02_retry",use_container_width=True): st.session_state.g02_phase="story";st.session_state.g02_strategy=None;st.session_state.g02_results=[];st.rerun()
        complete_game(2);update_radar("条件思维",4 if rate>60 else 2)
        if strategy=="switch" and rate>60: check_achievement("换盒达人")

# ═══════════════════════════════════════════════════════════
# 游戏 3: 撞头像
# ═══════════════════════════════════════════════════════════
def show_game_03():
    top_nav(3);chapter_banner(3)
    EMJ=["😀","🎨","🎯","🎲","🎸","🎧","🎮","🎭","🎪","🎺","🎻","🎹","🎼","🎽","🎾","🎿","🏀","🏁","🏂","🏃","🏄","🏆","🏈","🏊","🏋","🏌","🏍","🏎","🏏","🏐","🏑","🏒","🏓","🏔","🏕","🏖","🏗","🏘","🏙","😃","😄","😁","😆","😅","🤣","😂","🙂","😉","😊","😇","🥰","😍","🤩","😘","😗","😋","😛","😜","🤪","😝","🤑","🤗","🤭","🤫","🤔"]
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#151a1a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🎨</span><div><h3 style="color:#F0B90B;margin:0 0 8px 0;">撞头像</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">校园App——<b>365个</b>默认头像随机分配。<br>💬 室友：<i>"至少100人以上才会撞头像！"</i><br>你敢赌吗？</p></div></div></div>""",unsafe_allow_html=True)
    if "g03_phase" not in st.session_state: st.session_state.g03_phase="bet";st.session_state.g03_predict=50;st.session_state.g03_people=[];st.session_state.g03_collision_at=None;st.session_state.g03_bet_amount=0
    if st.session_state.g03_phase=="bet":
        st.session_state.g03_predict=st.slider("🎯 你赌第几个人时撞头像？",5,150,st.session_state.g03_predict)
        cc=st.columns(4)
        for i,amt in [(0,10),(1,50),(2,100),(3,st.session_state.coins)]:
            label=f"💰 押{amt}" if amt<st.session_state.coins else "🚀 All-in"
            if cc[i].button(label,key=f"g03_b{i}",use_container_width=True): st.session_state.g03_bet_amount=amt;st.session_state.g03_phase="running";st.session_state.g03_people=[];st.session_state.g03_collision_at=None;st.rerun()
    elif st.session_state.g03_phase=="running":
        if "g03_auto" not in st.session_state: st.session_state.g03_auto=False
        if "g03_delay" not in st.session_state: st.session_state.g03_delay=0.8
        cd,cm,ca,cp,cr=st.columns([2,1,1,1,1])
        with cd: st.session_state.g03_delay=st.select_slider("⏱ 间隔(秒/人)",[0.3,0.5,0.8,1.0,1.5,2.0],value=st.session_state.g03_delay)
        with cm:
            if st.button("👤 +1",key="g03_m1",use_container_width=True,disabled=st.session_state.g03_auto):
                if st.session_state.g03_collision_at is None:
                    new=random.choice(EMJ[:365]);st.session_state.g03_people.append(new)
                    if len(set(st.session_state.g03_people))<len(st.session_state.g03_people): st.session_state.g03_collision_at=len(st.session_state.g03_people)
                st.rerun()
        with ca:
            label="▶ 自动开始" if not st.session_state.g03_people else "▶ 继续自动"
            if not st.session_state.g03_auto and st.button(label,key="g03_auto_btn",use_container_width=True,type="primary",disabled=st.session_state.g03_collision_at is not None): st.session_state.g03_auto=True;st.rerun()
        with cp:
            if st.button("⏸ 暂停",key="g03_pause",use_container_width=True,disabled=not st.session_state.g03_auto): st.session_state.g03_auto=False;st.rerun()
        with cr:
            if st.button("🔄 重来",key="g03_reset",use_container_width=True): st.session_state.g03_auto=False;st.session_state.g03_phase="bet";st.session_state.g03_people=[];st.session_state.g03_collision_at=None;st.rerun()
        if st.session_state.g03_auto and st.session_state.g03_collision_at is None:
            new=random.choice(EMJ[:365]);st.session_state.g03_people.append(new)
            if len(set(st.session_state.g03_people))<len(st.session_state.g03_people): st.session_state.g03_collision_at=len(st.session_state.g03_people);st.session_state.g03_auto=False
            else: time.sleep(st.session_state.g03_delay)
            st.rerun()
        n=len(st.session_state.g03_people)
        if n>0:
            grid='<div style="line-height:1.2;">'
            for i,av in enumerate(st.session_state.g03_people):
                cls="avatar-icon collision" if st.session_state.g03_collision_at and i+1==st.session_state.g03_collision_at and st.session_state.g03_people[:i].count(av)>0 else "avatar-icon"
                grid+=f'<div class="{cls}">{av}</div>'
            grid+='</div>';st.markdown(grid,unsafe_allow_html=True)
        c1,c2,c3=st.columns(3);c1.metric("👥 已注册",n);c2.metric("🔗 配对数",f"{n*(n-1)//2:,}");c3.metric("🎯 你的赌注",f"第{st.session_state.g03_predict}人")
        if st.session_state.g03_collision_at is not None:
            st.balloons();nc=st.session_state.g03_collision_at;diff=abs(nc-st.session_state.g03_predict)
            st.markdown(f"## ⚡ 第 **{nc}** 个人——撞头像了！")
            x_t=np.arange(1,101);y_t=[1-np.exp(-i*(i-1)/(2*365)) for i in x_t]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=x_t,y=y_t,mode='lines',line=dict(color='#F0B90B',width=3),fill='tozeroy',fillcolor='rgba(240,185,11,0.08)'))
            fig.add_vline(x=23,line_dash="dash",line_color="#00D4AA",annotation_text="23人→50%")
            fig.add_vline(x=nc,line_color="#FF4757",line_width=3,annotation_text=f"碰撞={nc}")
            fig.update_layout(**PLOTLY_DARK,height=350,xaxis_title="人数",yaxis_title="碰撞概率")
            st.plotly_chart(fig,use_container_width=True)
            if st.button("📊 看分析",key="g03_reveal",type="primary",use_container_width=True): st.session_state.g03_phase="reveal";st.rerun()
    elif st.session_state.g03_phase=="reveal":
        reveal_box("秘密不在于365——在于任意两人互相比对",f"你预测第<b>{st.session_state.g03_predict}</b>人，实际第<b>{st.session_state.g03_collision_at}</b>人就撞了。<br><b>23人</b>时碰撞概率就超50%——只有253对比较。<br>配对C(N,2)=N(N-1)/2——增长比你想象快得多。","黑客不是猜你的密码，而是在所有人里找任意碰撞。足够大的群体里，'巧合'几乎必然发生。",f"预测{st.session_state.g03_predict}人，实际{st.session_state.g03_collision_at}人碰撞。",3)
        math_detail("$$P(\\text{碰撞})=1-\\frac{365\\cdots(365-N+1)}{365^N}\\approx 1-e^{-N(N-1)/730}$$ 23人→50.7%，比较的是所有$$C(N,2)$$对。")
        if st.button("🔄 再来",key="g03_again",use_container_width=True,type="primary"): st.session_state.g03_phase="bet";st.session_state.g03_people=[];st.session_state.g03_collision_at=None;st.rerun()
        complete_game(3);update_radar("大数感觉",3)

# ═══════════════════════════════════════════════════════════
# 游戏 4: 翻倍陷阱 (遍历性破缺)
# ═══════════════════════════════════════════════════════════
def show_game_04():
    top_nav(4);chapter_banner(4)
    WIN,LOSE,INI=1.5,0.6,1000
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#1a1518 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🪙</span><div><h3 style="color:#F0B90B;margin:0 0 8px 0;">翻倍陷阱 —— 稳赚的赌局？</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">扔硬币。正面→钱×1.5(+50%)。反面→钱×0.6(-40%)。<br><b>必须All-in</b>。期望=0.5×1.5+0.5×0.6=<b style="color:#00D4AA;">1.05</b>——每局+5%！<br>数学不会骗人。你有<b>💰 1,000块</b>。全部押上？</p></div></div></div>""",unsafe_allow_html=True)
    if "g04_phase" not in st.session_state: st.session_state.g04_phase="intro";st.session_state.g04_balance=INI;st.session_state.g04_history=[INI];st.session_state.g04_round=0;st.session_state.g04_last_result=None;st.session_state.g04_streak_type=None;st.session_state.g04_streak_count=0
    if st.session_state.g04_phase=="intro":
        if st.button("🪙 扔硬币！All-in",type="primary",use_container_width=True): st.session_state.g04_phase="playing";st.rerun()
    elif st.session_state.g04_phase=="playing":
        bal=st.session_state.g04_balance;rnd=st.session_state.g04_round
        c1,c2,c3,c4=st.columns(4)
        d=bal-INI;clr="#00D4AA" if d>=0 else "#FF4757"
        c1.markdown(f"<div style='text-align:center;'><span style='color:#8B8F98;font-size:12px;'>💰 余额</span><br><span style='color:{clr};font-size:28px;font-weight:800;'>{bal:,.0f}</span></div>",unsafe_allow_html=True)
        c2.markdown(f"<div style='text-align:center;'><span style='color:#8B8F98;font-size:12px;'>📈 盈亏</span><br><span style='color:{clr};font-size:28px;font-weight:800;'>{d:+,.0f}</span></div>",unsafe_allow_html=True)
        c3.markdown(f"<div style='text-align:center;'><span style='color:#8B8F98;font-size:12px;'>🎯 局数</span><br><span style='color:#E4E6EB;font-size:28px;font-weight:800;'>{rnd}</span></div>",unsafe_allow_html=True)
        si="🟢" if st.session_state.g04_streak_type=="win" else "🔴" if st.session_state.g04_streak_type=="lose" else "➖"
        c4.markdown(f"<div style='text-align:center;'><span style='color:#8B8F98;font-size:12px;'>{si} 连{'胜' if st.session_state.g04_streak_type=='win' else '败' if st.session_state.g04_streak_count else '-'}</span><br><span style='color:#E4E6EB;font-size:28px;font-weight:800;'>{st.session_state.g04_streak_count if st.session_state.g04_streak_count else '-'}</span></div>",unsafe_allow_html=True)
        if st.session_state.g04_last_result:
            if st.session_state.g04_last_result=="win": st.success(f"🟢 上一局：正面！×{WIN} → {bal:,.0f}")
            else: st.error(f"🔴 上一局：反面！×{LOSE} → {bal:,.0f}")
            if rnd>=2: st.info(f"💡 一赢一亏 = {WIN}×{LOSE} = **{WIN*LOSE:.2f}**——钱变少了！")
        if len(st.session_state.g04_history)>1:
            y=st.session_state.g04_history;ens=[INI*(1.05**i) for i in range(len(y))]
            fig=go.Figure()
            fig.add_trace(go.Scatter(y=y,mode='lines+markers',line=dict(color='#FF4757',width=2.5),marker=dict(size=6,color='#F0B90B'),name='你的余额'))
            fig.add_trace(go.Scatter(y=ens,mode='lines',line=dict(color='#00B4D8',width=2,dash='dash'),name='系综平均(+5%/局)'))
            fig.add_hline(y=INI,line_dash="dot",line_color="#8B8F98");fig.update_layout(**PLOTLY_DARK,height=280,xaxis_title="局数",yaxis_title="余额",yaxis_type="log" if max(y)/(min(y)+0.01)>10 else "linear")
            st.plotly_chart(fig,use_container_width=True)
        nw=bal*WIN;nl=bal*LOSE
        st.markdown(f"""<div style="background:#1A1D24;border:2px solid #F0B90B;border-radius:12px;padding:20px;text-align:center;margin:16px 0;"><span style="color:#8B8F98;">第{rnd+1}局·All-in 💰{bal:,.0f}</span><br>🟢 正面→<b style="color:#00D4AA;">{nw:,.0f}</b> | 🔴 反面→<b style="color:#FF4757;">{nl:,.0f}</b><br><span style="color:#8B8F98;font-size:11px;">期望:0.5×{nw:,.0f}+0.5×{nl:,.0f}=<b>{(nw+nl)/2:,.0f}</b>(+5%)</span></div>""",unsafe_allow_html=True)
        st.caption("每次输赢由系统随机决定(50/50)，你只能选择何时离场。")
        cs,ca,cq=st.columns([1,1,1])
        with cs:
            if st.button("🪙 扔硬币(随机！)",key="g04_spin",use_container_width=True,type="primary"):
                win=np.random.random()<0.5;st.session_state.g04_balance=bal*(WIN if win else LOSE)
                st.session_state.g04_history.append(st.session_state.g04_balance);st.session_state.g04_round+=1
                st.session_state.g04_last_result="win" if win else "lose"
                nt="win" if win else "lose"
                if st.session_state.g04_streak_type==nt: st.session_state.g04_streak_count+=1
                else: st.session_state.g04_streak_type=nt;st.session_state.g04_streak_count=1
                if st.session_state.g04_balance<1: st.session_state.g04_phase="reveal"
                st.rerun()
        with ca:
            if st.button("⚡ 快进50局",key="g04_auto",use_container_width=True):
                for _ in range(50):
                    b=st.session_state.g04_balance
                    if b<1: st.session_state.g04_phase="reveal";break
                    wn=np.random.random()<0.5;st.session_state.g04_balance=b*(WIN if wn else LOSE)
                    st.session_state.g04_history.append(st.session_state.g04_balance);st.session_state.g04_round+=1
                if st.session_state.g04_balance<1: st.session_state.g04_phase="reveal"
                st.rerun()
        with cq:
            if st.button("🏃 带钱离场",key="g04_quit",use_container_width=True): st.session_state.g04_phase="reveal";st.rerun()
    elif st.session_state.g04_phase=="reveal":
        final=st.session_state.g04_balance;nr=st.session_state.g04_round
        if final>INI: st.success(f"带着 **{final:,.0f}** 离场，赚了 **{final-INI:+,.0f}**。你是极少数幸存者。")
        else: st.error(f"余额 **{final:,.0f}**。玩了{nr}局，几乎归零。")
        # 30条轨迹
        np.random.seed(42);trajs=[]
        for _ in range(30):
            t=[INI]
            for __ in range(max(nr,50)): t.append(t[-1]*(WIN if np.random.random()<0.5 else LOSE))
            trajs.append(t)
        fig=go.Figure()
        for i,t in enumerate(trajs): fig.add_trace(go.Scatter(y=t,mode='lines',line=dict(color='#FF4757' if i==0 else '#2A2D35',width=3 if i==0 else 0.6),opacity=1 if i==0 else 0.4,showlegend=i==0,name='你的路径' if i==0 else None))
        ens=np.mean(np.array(trajs),axis=0);fig.add_trace(go.Scatter(y=ens,mode='lines',line=dict(color='#00B4D8',width=2.5,dash='dash'),name='系综平均'))
        fig.add_hline(y=INI,line_dash="dot",line_color="#8B8F98");fig.update_layout(**PLOTLY_DARK,height=350,xaxis_title="局数",yaxis_title="余额(对数)",yaxis_type="log")
        st.plotly_chart(fig,use_container_width=True)
        st.caption("🔴 红色粗线=你 | 灰色细线=其他29条 | 蓝色虚线=系综平均(稳步上升)")
        # 终局分布
        finals=[INI];np.random.seed(123)
        for _ in range(1000):
            b=INI
            for __ in range(50): b*=WIN if np.random.random()<0.5 else LOSE
            finals.append(max(b,0.01))
        pct_ruined=sum(1 for f in finals if f<INI)/len(finals)*100
        fig2=go.Figure()
        fig2.add_trace(go.Histogram(x=finals,nbinsx=60,marker_color='#F0B90B',opacity=0.7))
        fig2.add_vline(x=INI,line_dash="dash",line_color="#00D4AA",annotation_text="本金1000")
        fig2.add_vline(x=final,line_color="#FF4757",line_width=3,annotation_text=f"你{final:,.0f}")
        fig2.update_layout(**PLOTLY_DARK,height=300,xaxis_title="终局余额",yaxis_title="人数",xaxis_type="log")
        st.plotly_chart(fig2,use_container_width=True)
        st.caption(f"**{pct_ruined:.0f}%** 的玩家亏了。少数暴富者拉高了'平均'——论坛上全是赚钱帖。")
        arith=0.5*WIN+0.5*LOSE;geom=np.sqrt(WIN*LOSE)
        st.markdown(f"""<div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:20px;"><h4 style="color:#F0B90B;">📐 为什么"期望为正"你却亏了？</h4><table style="width:100%;color:#E4E6EB;"><tr><td>🔵 算术平均</td><td>=0.5×{WIN}+0.5×{LOSE}</td><td style="color:#00D4AA;font-weight:700;">={arith:.2f} ✓</td></tr><tr><td>🔴 几何平均</td><td>=√({WIN}×{LOSE})</td><td style="color:#FF4757;font-weight:700;">={geom:.3f} ✗</td></tr></table><p style="color:#8B8F98;font-size:13px;">算术平均=平行宇宙的你平均赚多少。<br>几何平均=你在这一个宇宙里反复All-in后还剩多少。<br><b>你的命运由几何均值决定。</b></p></div>""",unsafe_allow_html=True)
        reveal_box("遍历性破缺：期望为正的游戏，反复玩却必然破产",f"你玩了<b>{nr}</b>局，余额1000→<b>{final:,.0f}</b>。<br>'期望+5%'没算错——但它回答的是错误的问题。<br><b>系综平均</b>(平行宇宙)→每局+5%。<br><b>时间平均</b>(你的路径)→几何均值√(1.5×0.6)={geom:.3f}。<br>这就叫<b>遍历性破缺</b>：当过程涉及乘法(复利/All-in)时，系综平均和时间平均是两个东西。","创业期望回报为正(VC赚钱)——但你只能活一次。杠杆投资涨50%跌40%→反复All-in→归零。你的命运由几何均值决定。",f"遍历性破缺。Win×1.5,Lose×0.6。玩了{nr}局，最终{final:.0f}。算术平均={arith:.2f}，几何平均={geom:.3f}。",4)
        math_detail("**系综平均** $$E[R]=0.5\\times1.5+0.5\\times0.6=1.05$$ **时间平均** $$G=\\sqrt{1.5\\times0.6}\\approx0.949$$ 非各态历经：时间平均≠系综平均。")
        if st.button("🔄 重新来过",key="g04_again",use_container_width=True,type="primary"): st.session_state.g04_phase="intro";st.session_state.g04_balance=INI;st.session_state.g04_history=[INI];st.session_state.g04_round=0;st.rerun()
        complete_game(4);update_radar("独立直觉",4)

# ═══════════════════════════════════════════════════════════
# 游戏 5: 天才的诅咒 (回归均值)
# ═══════════════════════════════════════════════════════════
def show_game_05():
    top_nav(5)
    chapter_banner(5)

    st.markdown(
        """
        <div class="game-card">
            <h3>⚽ 天才的诅咒</h3>
            <p style="color:#E4E6EB;font-size:15px;line-height:1.7;">
            你是俱乐部的<b>首席球探</b>。第一赛季排行榜上突然冒出一批“天才新人”。<br>
            但你心里很清楚：<b>进球 = 真实天赋 + 随机运气</b>。<br>
            你只有 <b>3 个签约名额</b>。选错了，明年你的位置就危险了。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "g05_true" not in st.session_state:
        np.random.seed(int(time.time()))
        n = 50
        true_skill = np.random.normal(75, 10, n)
        luck_s1 = np.random.normal(0, 8, n)
        st.session_state.g05_true = true_skill
        st.session_state.g05_s1 = true_skill + luck_s1
        st.session_state.g05_s2 = None
        st.session_state.g05_picks = []
        st.session_state.g05_reason = None
        st.session_state.g05_phase = "stage1"

    if st.session_state.g05_phase not in ("stage1", "stage2", "stage25", "stage3"):
        st.session_state.g05_phase = "stage1"

    s1 = st.session_state.g05_s1
    true = st.session_state.g05_true

    if st.session_state.g05_phase == "stage1":
        st.markdown("### 🏆 第一赛季 · 排行榜")
        rankings = sorted(enumerate(s1), key=lambda x: x[1], reverse=True)
        top10 = rankings[:10]

        left, right = st.columns([1.15, 1])
        with left:
            st.markdown("#### 🔥 前十名球员榜单")
            for rank, (idx, goals) in enumerate(top10, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
                color = "#F0B90B" if rank <= 3 else "#00B4D8" if rank <= 5 else "#4A90D9"
                glow = "0 0 14px rgba(240,185,11,0.25)" if rank <= 3 else "none"
                st.markdown(
                    f"""
                    <div style="background:#1A1D24;border:1px solid {color};border-radius:12px;padding:14px 18px;margin-bottom:10px;box-shadow:{glow};">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
                            <div>
                                <span style="font-size:22px;">{medal}</span>
                                <span style="color:{color};font-weight:800;font-size:18px;"> 第{rank}名</span>
                                <span style="color:#E4E6EB;font-weight:700;font-size:18px; margin-left:10px;">球员 #{idx+1:02d}</span>
                            </div>
                            <div style="text-align:right; min-width:120px;">
                                <span style="color:#F0B90B;font-size:28px;font-weight:800;">{goals:.0f}</span>
                                <span style="color:#E4E6EB;font-size:18px;"> 球</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with right:
            st.markdown("#### 📋 全部 50 名球员")
            rows_html = '<div style="max-height:320px; overflow-y:auto; font-size:13px; line-height:1.9; font-family:monospace;">'
            for rank, (idx, goals) in enumerate(rankings, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
                color = "#F0B90B" if rank <= 3 else "#E4E6EB" if rank <= 10 else "#8B8F98"
                bar = "█" * int(goals / max(s1) * 20) if max(s1) > 0 else ""
                rows_html += f'<span style="color:{color};">{medal} #{rank:2d} 球员#{idx+1:02d} {goals:5.0f}球 {bar}</span><br>'
            rows_html += '</div>'
            st.markdown(rows_html, unsafe_allow_html=True)

        st.markdown(
            """
            <div style="background:#1A1D24;border:1px solid #F0B90B;border-radius:12px;padding:16px;">
                <span style="color:#F0B90B;font-weight:600;">💡 你注意到没？</span>
                <span style="color:#E4E6EB;">前十名看起来都像天才——但排行榜最会骗人。你现在要签下最值得培养的 3 人。</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("▶ 进入签约环节", key="g05_go_stage2", type="primary", use_container_width=True):
            st.session_state.g05_phase = "stage2"
            st.rerun()

    elif st.session_state.g05_phase == "stage2":
        st.markdown("### ✍️ 球探签约名单")
        st.caption("请输入你看好的球员编号（1~50），最多 3 人。支持逗号/空格分隔，例如：1, 5, 12")

        # 历史数据浏览（签约时仍可回看）
        with st.expander("📋 回看第一赛季全部数据（签约前最后确认）", expanded=True):
            rankings = sorted(enumerate(s1), key=lambda x: x[1], reverse=True)
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown("#### 🔥 前十名回顾")
                for rank, (idx, goals) in enumerate(rankings[:10], 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
                    color = "#F0B90B" if rank <= 3 else "#00B4D8" if rank <= 5 else "#4A90D9"
                    st.markdown(
                        f"""
                        <div style="background:#1A1D24;border:1px solid {color};border-radius:10px;padding:10px 14px;margin-bottom:8px;">
                            <span style="font-size:18px;">{medal}</span>
                            <span style="color:{color};font-weight:800;"> 第{rank}名</span>
                            <span style="color:#E4E6EB;font-weight:700; margin-left:8px;">球员 #{idx+1:02d}</span>
                            <span style="float:right; color:#F0B90B; font-weight:800;">{goals:.0f}球</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            with col_b:
                st.markdown("#### 🧾 全部 50 名球员速查表")
                rows_html = '<div style="max-height:360px; overflow-y:auto; font-size:13px; line-height:1.9; font-family:monospace;">'
                for rank, (idx, goals) in enumerate(rankings, 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
                    color = "#F0B90B" if rank <= 3 else "#E4E6EB" if rank <= 10 else "#8B8F98"
                    bar = "█" * int(goals / max(s1) * 18) if max(s1) > 0 else ""
                    rows_html += f'<span style="color:{color};">{medal} #{rank:2d} 球员#{idx+1:02d} {goals:5.0f}球 {bar}</span><br>'
                rows_html += '</div>'
                st.markdown(rows_html, unsafe_allow_html=True)

        pick_input = st.text_input(
            "输入球员编号：",
            value=", ".join(str(p + 1) for p in st.session_state.g05_picks) if st.session_state.g05_picks else "",
            key="g05_pick_input",
            placeholder="例如：1, 5, 12",
        )
        picks = []
        if pick_input.strip():
            for n_str in re.findall(r"\d+", pick_input):
                n = int(n_str)
                if 1 <= n <= 50 and (n - 1) not in picks:
                    picks.append(n - 1)
        if len(picks) > 3:
            st.error("最多只能签 3 人。请删掉多余编号。")
            picks = picks[:3]
        st.session_state.g05_picks = picks

        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                if i < len(picks):
                    idx = picks[i]
                    st.markdown(
                        f"""
                        <div style="background:#1a1a10;border:2px solid #F0B90B;border-radius:12px;padding:16px;text-align:center;min-height:120px;">
                            <span style="color:#F0B90B;font-weight:800;font-size:18px;">球员 #{idx+1:02d}</span><br>
                            <span style="color:#E4E6EB;">第一赛季 {s1[idx]:.0f} 球</span><br>
                            <span style="color:#8B8F98;font-size:12px;">签约名单 {i+1}/3</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div style="background:#16181d;border:1px dashed #2A2D35;border-radius:12px;padding:16px;text-align:center;min-height:120px;">
                            <span style="color:#8B8F98;">空缺</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        if picks:
            st.success(f"✅ 当前已选：{', '.join(f'#{p+1:02d}' for p in picks)}")
        else:
            st.info("👆 还没有签任何人")

        if len(picks) == 3:
            if st.button("▶ 确认签约，进入第二赛季", key="g05_confirm", type="primary", use_container_width=True):
                st.session_state.g05_phase = "stage25"
                st.rerun()

    elif st.session_state.g05_phase == "stage25":
        st.markdown("### 🤔 你为什么会选他们？")
        st.caption("这个选择不会影响结果，但会影响你后面的复盘角度。")
        c1, c2, c3 = st.columns(3)
        if c1.button("🔥 第一赛季太猛了", key="g05_reason_hot", use_container_width=True):
            st.session_state.g05_reason = "hot"
            st.session_state.g05_s2 = true + np.random.normal(0, 8, 50)
            st.session_state.g05_phase = "stage3"
            st.rerun()
        if c2.button("📈 看起来更稳定", key="g05_reason_stable", use_container_width=True):
            st.session_state.g05_reason = "stable"
            st.session_state.g05_s2 = true + np.random.normal(0, 8, 50)
            st.session_state.g05_phase = "stage3"
            st.rerun()
        if c3.button("✨ 感觉像真天才", key="g05_reason_genius", use_container_width=True):
            st.session_state.g05_reason = "genius"
            st.session_state.g05_s2 = true + np.random.normal(0, 8, 50)
            st.session_state.g05_phase = "stage3"
            st.rerun()

    elif st.session_state.g05_phase == "stage3":
        st.markdown("### 📉 第二赛季揭晓")
        s2 = st.session_state.g05_s2
        picks = st.session_state.g05_picks
        rankings_s1 = sorted(enumerate(s1), key=lambda x: x[1], reverse=True)
        rankings_s2 = sorted(enumerate(s2), key=lambda x: x[1], reverse=True)
        top10_s2 = set(idx for idx, _ in rankings_s2[:10])
        rank_map_s2 = {idx: rank+1 for rank, (idx, _) in enumerate(rankings_s2)}

        st.markdown("#### 🧾 你签下的 3 个人，第二赛季表现如何？")
        cols = st.columns(3)
        for i, idx in enumerate(picks):
            diff = s2[idx] - s1[idx]
            border = "#00D4AA" if true[idx] >= 85 else "#FF4757"
            label = "🟢 真天才" if true[idx] >= 85 else "🔴 只是运气好"
            mood = "📈" if diff > 3 else "📉" if diff < -3 else "➡️"
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background:#1A1D24;border:2px solid {border};border-radius:12px;padding:16px;text-align:center;min-height:180px;">
                        <span style="color:#E4E6EB;font-weight:800;font-size:18px;">球员 #{idx+1:02d}</span><br>
                        <span style="color:#F0B90B;">S1: {s1[idx]:.0f}球</span><br>
                        <span style="color:#00B4D8;">S2: {s2[idx]:.0f}球</span><br>
                        <span style="color:{border}; font-weight:700;">{mood} {diff:+.0f}</span><br>
                        <span style="color:#8B8F98;font-size:12px;">真实天赋 {true[idx]:.0f}</span><br>
                        <span style="color:#8B8F98;font-size:12px;">第二赛季排名 #{rank_map_s2[idx]}</span><br>
                        <span style="font-size:13px;">{label}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("#### 📋 第一赛季 Top10 → 第二赛季变化")
        table = "| 排名 | 球员 | 第一赛季 | 第二赛季 | 变化 | 真实天赋 | 还在Top10? |\n"
        table += "|------|------|----------|----------|------|----------|------------|\n"
        top10_s1 = set(idx for idx, _ in rankings_s1[:10])
        for rank, (idx, _) in enumerate(rankings_s1[:10], 1):
            diff = s2[idx] - s1[idx]
            emoji = "📉" if diff < -3 else "📈" if diff > 3 else "➡️"
            still_top = "✅" if idx in top10_s2 else "❌ 跌出"
            genius_flag = "🟢" if true[idx] >= 85 else ""
            table += f"| {rank} | #{idx+1:02d} {genius_flag} | {s1[idx]:.0f} | {s2[idx]:.0f} | {emoji} {diff:+.0f} | {true[idx]:.0f} | {still_top} |\n"
        st.markdown(table)
        st.caption(f"第一赛季 Top10 中，只有 {sum(1 for idx in top10_s1 if idx in top10_s2)} 人留在了第二赛季 Top10。")

        correct = sum(1 for i in picks if true[i] >= 85)
        hit_rate = correct / len(picks) * 100 if picks else 0
        if hit_rate >= 67:
            st.success(f"🎯 你是靠谱球探：命中 {correct}/3，命中率 {hit_rate:.0f}%")
        elif hit_rate >= 34:
            st.warning(f"🤔 你有点眼光：命中 {correct}/3，命中率 {hit_rate:.0f}%")
        else:
            st.error(f"😬 你被排行榜骗惨了：命中 {correct}/3，命中率 {hit_rate:.0f}%")

        st.markdown("#### 🔁 多赛季稳定性模拟")
        n_extra = st.slider("额外模拟赛季数", 3, 20, 5, key="g05_extra")
        if st.button("🔁 运行多赛季模拟", key="g05_multi", type="primary"):
            top10_counts = {idx: 0 for idx in range(50)}
            s1_top10 = [idx for idx, _ in rankings_s1[:10]]
            for _ in range(n_extra):
                season_data = true + np.random.normal(0, 8, 50)
                season_rank = sorted(enumerate(season_data), key=lambda x: x[1], reverse=True)
                for idx, _ in season_rank[:10]:
                    top10_counts[idx] += 1

            data = [(idx, top10_counts[idx]) for idx in s1_top10]
            data.sort(key=lambda x: x[1], reverse=True)
            st.markdown("##### 📋 后续赛季仍然能留在前十的次数")
            for pos, (idx, count) in enumerate(data, 1):
                color = "#00D4AA" if count >= n_extra * 0.8 else "#F0B90B" if count >= 1 else "#FF4757"
                label = "始终强势" if count >= n_extra * 0.8 else "偶尔出现" if count >= 1 else "完全消失"
                stars = "★" * count + "☆" * (n_extra - count)
                st.markdown(
                    f"""
                    <div style="background:#1A1D24;border:1px solid {color};border-radius:12px;padding:14px 18px;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
                            <div>
                                <span style="color:{color};font-weight:800;font-size:17px;">第{pos}位</span>
                                <span style="color:#E4E6EB;font-weight:700;font-size:18px; margin-left:10px;">球员 #{idx+1:02d}</span>
                            </div>
                            <div style="text-align:right; min-width:140px;">
                                <span style="color:{color};font-size:24px;font-weight:800;">{count}/{n_extra}</span>
                                <span style="color:#8B8F98;font-size:13px;"> 季</span><br>
                                <span style="color:#8B8F98;font-size:12px;">{label}</span>
                            </div>
                        </div>
                        <div style="margin-top:8px; color:#F0B90B; letter-spacing:2px; font-size:16px;">{stars}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            always_top = sum(1 for _, count in data if count >= n_extra * 0.8)
            never_top = sum(1 for _, count in data if count == 0)
            st.markdown(
                f"""
                <div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:16px;">
                    <span style="color:#00D4AA;">🟢 始终强势：{always_top} 人</span> &nbsp;&nbsp;
                    <span style="color:#FF4757;">🔴 再也没进前十：{never_top} 人</span><br>
                    <span style="color:#8B8F98;font-size:13px;">只有真正的强者能长期留在顶端，大多数“天才”只是那一年运气好。</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### 🔬 天赋 vs 运气：Top5 的真相")
        top5 = [idx for idx, _ in rankings_s1[:5]]
        for rank, idx in enumerate(top5, 1):
            talent_part = true[idx]
            luck_part = s1[idx] - true[idx]
            total = s1[idx]
            luck_color = "#F0B90B" if luck_part >= 0 else "#FF4757"
            st.markdown(
                f"""
                <div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:16px;margin-bottom:12px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
                        <div>
                            <span style="color:#E4E6EB;font-weight:800;font-size:18px;">第{rank}名 · 球员 #{idx+1:02d}</span><br>
                            <span style="color:#8B8F98;font-size:13px;">第一赛季总成绩 {total:.0f} 球</span>
                        </div>
                        <div style="text-align:right; min-width:170px;">
                            <span style="color:#00D4AA;font-weight:700;">真实天赋 {talent_part:.0f}</span><br>
                            <span style="color:{luck_color};font-weight:700;">运气 {'+' if luck_part >= 0 else ''}{luck_part:.0f}</span>
                        </div>
                    </div>
                    <div style="margin-top:10px;">
                        <div style="background:#2A2D35;border-radius:8px;height:18px;overflow:hidden;display:flex;">
                            <div style="background:#00D4AA;width:{max(0,min(100,talent_part/100*100))}%;height:100%;"></div>
                            <div style="background:{luck_color};width:{max(0,min(100,abs(luck_part)/100*100))}%;height:100%;"></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:12px;color:#8B8F98;">
                            <span>绿色=天赋</span><span>{'橙色' if luck_part >= 0 else '红色'}=运气</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        reveal_box(
            "极值 = 信号 + 噪声。噪声下次消失，极值自然回弹。",
            f"你签下的 3 个人中，只有 <b>{correct}</b> 个是真天才。<br>"
            f"第一赛季的高分往往不是纯天赋，而是<b>真实能力 + 好运气</b>。<br>"
            f"第二赛季运气重抽，极端值自然往中间回落。<br>这就是<b>回归均值</b>。",
            "爆红一次的主播、突然大赚一年的基金经理、只考好一次的学生——很多“天才时刻”背后，都有噪声站台。",
        )
        math_detail(r"""
**模型**：$$X_i=\theta_i+\varepsilon_i$$
其中 $$\theta_i\sim\mathcal{N}(75,10^2)$$ 为真实能力，$$\varepsilon_i\sim\mathcal{N}(0,8^2)$$ 为运气。
条件期望：$$E[\theta\mid X_1=x_1]=\mu+\frac{\sigma_\theta^2}{\sigma_\theta^2+\sigma_\varepsilon^2}(x_1-\mu)$$
收缩因子小于 1，这就是“回归均值”的来源。
""")
        if st.button("🔄 换一批球员", key="g05_new_batch", use_container_width=True, type="primary"):
            reset_game("g05_")
            st.rerun()
        complete_game(5)
        update_radar("大数感觉", 4)

# ═══════════════════════════════════════════════════════════
# 游戏 6: 两个神医 (辛普森悖论)
# ═══════════════════════════════════════════════════════════
def show_game_06():
    top_nav(6)
    chapter_banner(6)

    st.markdown(
        """
        <div class="game-card">
            <h3>🏥 两个神医</h3>
            <p style="color:#E4E6EB;font-size:15px;line-height:1.7;">
            镇上两家诊所打起了擂台。<br>
            🏆 华大夫挂着巨幅广告：<b style="color:#F0B90B;">“治愈率 83%！全镇第一！”</b><br>
            🏥 张大夫的牌子寒酸得多：<b>“治愈率 78%。”</b><br>
            你妈打电话来催你挂号：<i>“赶紧挂华大夫，数据都写着呢！”</i><br>
            但这时，一条匿名消息发来：<i>“别只看总治愈率，看看他们都在治什么病人。”</i>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 固定案例数据
    if "g06_phase" not in st.session_state:
        st.session_state.g06_phase = "overall_choice"
        st.session_state.g06_first_choice = None
        st.session_state.g06_second_choice = None
        st.session_state.g06_grouping_answer = []

    if st.session_state.g06_phase not in ("overall_choice", "split_view", "rechoice", "grouping", "reveal"):
        st.session_state.g06_phase = "overall_choice"

    # ─────────────────────────────
    # 阶段1：先被总体广告骗进去
    # ─────────────────────────────
    if st.session_state.g06_phase == "overall_choice":
        st.markdown("### 📢 先看广告牌")

        left, right = st.columns(2)
        with left:
            st.markdown(
                """
                <div style="background:#1a1a10;border:2px solid #F0B90B;border-radius:16px;padding:24px;min-height:220px;">
                    <div style="text-align:center;">
                        <span style="font-size:34px;">🏆</span><br>
                        <span style="color:#F0B90B;font-size:24px;font-weight:800;">华大夫</span><br>
                        <span style="color:#E4E6EB;font-size:46px;font-weight:900;">83%</span><br>
                        <span style="color:#8B8F98;">总体治愈率</span><br><br>
                        <span style="color:#E4E6EB;">门口排队：🏃🏃🏃🏃🏃🏃🏃🏃</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                """
                <div style="background:#101a1a;border:2px solid #00B4D8;border-radius:16px;padding:24px;min-height:220px;">
                    <div style="text-align:center;">
                        <span style="font-size:34px;">🏥</span><br>
                        <span style="color:#00B4D8;font-size:24px;font-weight:800;">张大夫</span><br>
                        <span style="color:#E4E6EB;font-size:46px;font-weight:900;">78%</span><br>
                        <span style="color:#8B8F98;">总体治愈率</span><br><br>
                        <span style="color:#E4E6EB;">门口排队：🏃</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### 🤔 只看总体治愈率，你先挂谁的号？")
        c1, c2, c3 = st.columns(3)
        if c1.button("🏆 挂华大夫", key="g06_choice_hua", use_container_width=True, type="primary"):
            st.session_state.g06_first_choice = "hua"
            st.session_state.g06_phase = "split_view"
            st.rerun()
        if c2.button("🏥 挂张大夫", key="g06_choice_zhang", use_container_width=True):
            st.session_state.g06_first_choice = "zhang"
            st.session_state.g06_phase = "split_view"
            st.rerun()
        if c3.button("🤔 先看数据再说", key="g06_choice_check", use_container_width=True):
            st.session_state.g06_first_choice = "check"
            st.session_state.g06_phase = "split_view"
            st.rerun()

    # ─────────────────────────────
    # 阶段2：按病种拆开看
    # ─────────────────────────────
    elif st.session_state.g06_phase == "split_view":
        st.markdown("### 🔬 按病种拆开看看")
        st.caption("同一个医生的总体数据，可能只是“病人结构”不同，不一定代表医术更高。")

        fig_group = go.Figure(data=[
            go.Bar(name="华大夫", x=["🤧 轻症", "🏥 重症"], y=[90, 55], marker_color='#F0B90B',
                   text=["90%", "55%"], textposition='outside', textfont=dict(color='#F0B90B', size=16)),
            go.Bar(name="张大夫", x=["🤧 轻症", "🏥 重症"], y=[95, 61], marker_color='#00B4D8',
                   text=["95% ✅", "61% ✅"], textposition='outside', textfont=dict(color='#00D4AA', size=16)),
        ])
        fig_group.update_layout(
            plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24",
            font={"color": "#E4E6EB", "size": 15},
            xaxis={"gridcolor": "#2A2D35"},
            yaxis={"gridcolor": "#2A2D35", "range": [0, 110], "title": "治愈率(%)"},
            height=340, barmode='group',
            title={"text": "每一种病，张大夫都更高", "font": {"color": "#E4E6EB", "size": 18}},
        )
        st.plotly_chart(fig_group, use_container_width=True)

        st.error("🚨 注意：在轻症和重症里，张大夫都赢了。但总体却输给了华大夫。")

        st.markdown("#### 🏃 病人到底都去哪了？")
        col_hua, col_arrow, col_zhang = st.columns([2, 0.6, 2])
        with col_hua:
            st.markdown(
                """
                <div style="background:#1a1a10;border:2px solid #F0B90B;border-radius:12px;padding:16px;text-align:center;">
                    <span style="color:#F0B90B;font-weight:800;font-size:18px;">🏆 华大夫</span><br>
                    <span style="color:#8B8F98;font-size:12px;">总体 83%</span><br><br>
                    <span style="color:#00D4AA;">🤧 轻症 800人</span><br>
                    <span style="font-size:28px;">🏃🏃🏃🏃🏃🏃🏃🏃</span><br>
                    <span style="color:#8B8F98;font-size:11px;">治愈率 90%</span><br><br>
                    <span style="color:#FF4757;">🏥 重症 200人</span><br>
                    <span style="font-size:14px;">🏃🏃</span><br>
                    <span style="color:#8B8F98;font-size:11px;">治愈率 55%</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_arrow:
            st.markdown("<div style='text-align:center; padding-top:80px; font-size:32px; color:#8B8F98;'>⟺</div>", unsafe_allow_html=True)
        with col_zhang:
            st.markdown(
                """
                <div style="background:#101a1a;border:2px solid #00B4D8;border-radius:12px;padding:16px;text-align:center;">
                    <span style="color:#00B4D8;font-weight:800;font-size:18px;">🏥 张大夫</span><br>
                    <span style="color:#8B8F98;font-size:12px;">总体 78%</span><br><br>
                    <span style="color:#00D4AA;">🤧 轻症 200人</span><br>
                    <span style="font-size:14px;">🏃🏃</span><br>
                    <span style="color:#8B8F98;font-size:11px;">治愈率 95%</span><br><br>
                    <span style="color:#FF4757;">🏥 重症 800人</span><br>
                    <span style="font-size:28px;">🏃🏃🏃🏃🏃🏃🏃🏃</span><br>
                    <span style="color:#8B8F98;font-size:11px;">治愈率 61%</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption("👆 华大夫看起来更强，只是因为他收了更多轻症（容易治）。张大夫收了更多重症（难治）。")

        if st.button("▶ 继续：这个分组到底合不合理？", key="g06_to_grouping", type="primary", use_container_width=True):
            st.session_state.g06_phase = "grouping"
            st.rerun()

    # ─────────────────────────────
    # 阶段4：什么时候可以分组？
    # ─────────────────────────────
    elif st.session_state.g06_phase == "grouping":
        st.markdown("### 🧠 什么时候可以分组，什么时候分组会出问题？")
        st.caption("不是“分组”本身正确，而是“按什么变量分组”决定了你是在纠偏，还是在制造偏差。")

        st.markdown("#### 下面哪些分组变量是合理的？（可多选）")
        options = {
            "病情轻重（入院时）": True,
            "年龄段": True,
            "治疗后是否进入 ICU": False,
            "治疗后是否出现副作用": False,
        }
        selected = []
        for label in options:
            if st.checkbox(label, key=f"g06_group_{label}"):
                selected.append(label)
        st.session_state.g06_grouping_answer = selected

        st.markdown(
            """
            <div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:16px;">
                <span style="color:#E4E6EB;font-weight:600;">提示：</span>
                <span style="color:#8B8F98;font-size:13px;">如果一个变量是在治疗前就存在、会影响结果，而且不会被治疗本身改变，那么按它分组通常是合理的。如果一个变量是治疗后才出现的，就可能把因果关系弄坏。</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("✅ 提交判断", key="g06_submit_grouping", type="primary", use_container_width=True):
            st.session_state.g06_phase = "reveal"
            st.rerun()

    # ─────────────────────────────
    # 阶段5：揭示
    # ─────────────────────────────
    elif st.session_state.g06_phase == "reveal":
        first = st.session_state.g06_first_choice
        second = st.session_state.g06_second_choice
        answers = set(st.session_state.g06_grouping_answer)
        correct_set = {"病情轻重（入院时）", "年龄段"}

        if first == "hua" and second == "zhang":
            st.success("🎯 你先被总体数据骗住了，后来通过拆分病种和调比例看穿了它。")
        elif second == "hua":
            st.warning("你仍然更相信总体数据——这正说明辛普森悖论为什么危险。")
        else:
            st.info("你一开始就比较谨慎，这很好。")

        if answers == correct_set:
            st.success("✅ 你选对了分组变量：病情轻重、年龄段。它们都是治疗前就存在的变量。")
        else:
            st.error("❌ 你把治疗后的变量也拿来分组了。这会引入后处理偏差，甚至造成新的对撞偏差。")

        reveal_box(
            "辛普森悖论只告诉你“总体可能骗人”，因果推断更关心“什么时候该分组”",
            "按“病情轻重”分组是合理的，因为它在治疗前就存在，会影响结果，而且不会被治疗改变。<br><br>"
            "如果一个变量是 <b>治疗前就确定</b>、<b>影响结果</b>、而且 <b>不受治疗本身影响</b>，那么每个组内都更像一个“小型随机试验”，分组比较才更有意义。<br><br>"
            "但如果你按“治疗后是否进入 ICU”“治疗后是否出现副作用”这种变量分组，就会把处理后的信息拿来比较，进而制造后处理偏差，甚至对撞偏差。<br><br>"
            "<b>所以：不是所有分组都值得做。只有当分组变量本身不被处理污染时，分组才真正帮助你更接近因果真相。</b>",
            "看到总体数据和分组数据打架时，不要立刻站队。先问：这个分组变量是在治疗前就存在的吗？它会不会被治疗本身改变？这一步，往往比算百分比更重要。",
        )
        math_detail(r"""
华总 $$=0.8\times90\% + 0.2\times55\% = 83\%$$
张总 $$=0.2\times95\% + 0.8\times61\% = 78\%$$
这就是辛普森悖论：各组内趋势一致，但总体趋势可能反转。

更进一步，如果治疗分配在给定某个治疗前变量 $$X$$ 后近似随机，
那么每个 $$X$$ 的分组都可以被看作一个“小型随机试验”。
但如果你按治疗后变量分组，就可能引入后处理偏差或对撞偏差。
""")
        if st.button("🔄 重新挂号", key="g06_retry", use_container_width=True):
            reset_game("g06_")
            st.rerun()
        complete_game(6)
        update_radar("混淆嗅觉", 4)

# ═══════════════════════════════════════════════════════════
# 游戏 7: 沉默的大多数 (幸存者偏差)
# ═══════════════════════════════════════════════════════════
def show_game_07():
    top_nav(7);chapter_banner(7)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#10101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">💸</span><div><h3 style="color:#00B4D8;margin:0 0 8px 0;">沉默的大多数</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">深夜，一条广告精准命中——<br><i style="color:#F0B90B;">"30天速成！月入过万。已有<b>50位</b>学员成功变现！"</i><br>下面一长串报喜截图。学费<b>¥499</b>。该不该买？</p></div></div></div>""",unsafe_allow_html=True)
    if "g07_stage" not in st.session_state: st.session_state.g07_stage="testimonials";st.session_state.g07_belief=None
    if st.session_state.g07_stage=="testimonials":
        st.markdown("### 📜 学员好评墙")
        np.random.seed(77);testimonials=[("😎","辞职了！月入3万！"),("🎉","2周出单！真的有用！"),("💰","最好的¥499投资"),("🚀","月薪5K→稳定2W+"),("🙏","后悔没早买"),("🔥","已推荐5个朋友"),("✨","第3个月开始盈利"),("💎","改变了我的人生")]
        cc=st.columns(4)
        for i,(emoji,text) in enumerate(testimonials):
            with cc[i%4]: st.markdown(f"""<div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:10px;padding:14px;margin-bottom:10px;min-height:130px;"><span style="font-size:24px;">{emoji}</span><span style="color:#F0B90B;">★★★★★</span><br><span style="color:#E4E6EB;font-size:13px;line-height:1.5;">{text}</span></div>""",unsafe_allow_html=True)
        st.markdown("#### 💭 你有多相信这个课程？")
        c1,c2,c3=st.columns(3)
        if c1.button("🤩 非常相信！买！",key="g07_high",use_container_width=True,type="primary"): st.session_state.g07_belief="high";st.session_state.g07_stage="investigate";st.rerun()
        if c2.button("🤔 有点信",key="g07_mid",use_container_width=True): st.session_state.g07_belief="mid";st.session_state.g07_stage="investigate";st.rerun()
        if c3.button("😒 不信",key="g07_low",use_container_width=True): st.session_state.g07_belief="low";st.session_state.g07_stage="investigate";st.rerun()
    elif st.session_state.g07_stage=="investigate":
        st.markdown("### 🔍 深挖后台数据")
        with st.expander("👁️ 第一层：你看到的",expanded=True): st.success("50人成功·50条好评·★★★★★4.9分·好评率98%")
        with st.expander("📂 第二层：购买总人数"): st.warning("累计售出：**10,000份**")
        with st.expander("💀 第三层：沉默的9950人"): st.error("**9,950人购买后无任何动静。**失败者不会主动写差评。")
        with st.expander("📐 第四层：真实成功率"):
            st.markdown("""<div style="background:#1a1515;border:2px solid #FF4757;border-radius:12px;padding:20px;text-align:center;"><span style="color:#FF4757;font-size:48px;font-weight:800;">0.5%</span><br><span style="color:#8B8F98;">50/10,000</span></div>""",unsafe_allow_html=True)
        fig=go.Figure(go.Funnel(y=["10,000人购买","9,950人失败(沉默)","50人成功(发声)"],x=[10000,9950,50],marker=dict(color=["#1A1D24","#FF4757","#00D4AA"]),textinfo="value+percent initial"))
        fig.update_layout(**PLOTLY_DARK,height=250);st.plotly_chart(fig,use_container_width=True)
        reveal_box("你看到的50人——只是10,000个失败者中的0.5%","失败的人不会发帖、不会写好评、不会告诉你'我被割了'。<br><b>幸存者偏差</b>：只有'活下来'的才能进入你的视野。<br>那9,950个沉默的人，才是真相。","不只是课程——创业故事只讲成功的、选股只吹涨的。每次看到'大家都成功了'——先问：那些失败的人在哪？",f"幸存者偏差。10000人购买，50人成功(0.5%)。",7)
        math_detail("观测成功率$$=\\frac{50}{50}=100\\%$$ 真实成功率$$=\\frac{50}{10000}=0.5\\%$$ $$P(发声\\mid成功)\\approx1$$但$$P(发声\\mid失败)\\approx0$$")
        if st.button("🔄 再体验",key="g07_again",use_container_width=True,type="primary"): st.session_state.g07_stage="testimonials";st.rerun()
        complete_game(7);update_radar("样本警觉",4)

# ═══════════════════════════════════════════════════════════
# 游戏 8: 阳性 (贝叶斯定理)
# ═══════════════════════════════════════════════════════════
def show_game_08():
    top_nav(8)
    chapter_banner(8)

    st.markdown(
        """
        <div class="game-card">
            <h3>🩺 阳性</h3>
            <p style="color:#E4E6EB;font-size:15px;line-height:1.7;">
            你刚做完一项罕见病筛查。检测机构写着：<b>准确率 99%</b>。<br>
            报告发到手机上——你点开一看：<b style="font-size:20px;color:#FF4757;">阳性</b><br>
            你心里一沉：<i>“99% 准确率……那我是不是几乎一定得病了？”</i>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "g08_phase" not in st.session_state:
        st.session_state.g08_phase = "guess1"
        st.session_state.g08_guess1 = None
        st.session_state.g08_guess2 = None

    if st.session_state.g08_phase not in ("guess1", "evidence", "guess2", "lab", "reveal"):
        st.session_state.g08_phase = "guess1"

    prevalence = 0.1 / 100
    accuracy = 99.0 / 100
    n = 1000
    ns = max(1, int(n * prevalence))
    nh = n - ns
    fp = int(nh * (1 - accuracy))
    total_pos = ns + fp
    ppv = ns / total_pos * 100 if total_pos > 0 else 0

    if st.session_state.g08_phase == "guess1":
        st.markdown("### 📋 体检报告单")
        st.markdown(
            """
            <div style="background:#1A1D24;border:2px solid #FF4757;border-radius:16px;padding:24px;max-width:520px;margin:0 auto 20px auto;text-align:center;">
                <span style="font-size:12px;color:#8B8F98;letter-spacing:2px;">医学检测报告</span>
                <hr style="border-color:#2A2D35;margin:8px 0;">
                <span style="font-size:46px;">🔴</span><br>
                <span style="font-size:32px;font-weight:900;color:#FF4757;">阳性</span><br>
                <span style="color:#8B8F98;font-size:13px;">检测准确率：99%</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### 🤔 你觉得自己真正患病的概率大概是多少？")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("A. 99%左右", key="g08_g1_a", use_container_width=True, type="primary"):
            st.session_state.g08_guess1 = "99%"
            st.session_state.g08_phase = "evidence"
            st.rerun()
        if c2.button("B. 70%左右", key="g08_g1_b", use_container_width=True):
            st.session_state.g08_guess1 = "70%"
            st.session_state.g08_phase = "evidence"
            st.rerun()
        if c3.button("C. 30%左右", key="g08_g1_c", use_container_width=True):
            st.session_state.g08_guess1 = "30%"
            st.session_state.g08_phase = "evidence"
            st.rerun()
        if c4.button("D. 10%以下", key="g08_g1_d", use_container_width=True):
            st.session_state.g08_guess1 = "10%以下"
            st.session_state.g08_phase = "evidence"
            st.rerun()

    elif st.session_state.g08_phase == "evidence":
        st.markdown("### 👥 别急着看公式——先看 1000 个人")
        st.info(f"1000个人里，真正得病的只有 **{ns} 人**。但健康人里，也会有大约 **{fp} 人** 被误报成阳性。")
        grid_html = '<div style="font-size:7px; line-height:1.1; font-family:monospace; letter-spacing:0;">'
        for i in range(20):
            for j in range(50):
                idx = i * 50 + j
                if idx < ns:
                    grid_html += '🟥'
                elif idx < ns + fp:
                    grid_html += '🩷'
                else:
                    grid_html += '⬛'
            grid_html += '<br>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
        st.caption(f"🟥 真病人 {ns} 人 | 🩷 假阳性 {fp} 人 | ⬛ 真阴性 {n - ns - fp} 人")
        st.warning(f"在这 **{total_pos}** 个阳性结果里，真正有病的只有 **{ns}** 个。")
        if st.button("▶ 看完 1000 人，我再猜一次", key="g08_to_guess2", type="primary", use_container_width=True):
            st.session_state.g08_phase = "guess2"
            st.rerun()

    elif st.session_state.g08_phase == "guess2":
        st.markdown("### 🔄 再猜一次")
        st.info(f"你第一次猜的是：**{st.session_state.g08_guess1}**")
        st.markdown("#### 现在你觉得，阳性后真正患病的概率是多少？")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("A. 99%左右", key="g08_g2_a", use_container_width=True):
            st.session_state.g08_guess2 = "99%"
            st.session_state.g08_phase = "lab"
            st.rerun()
        if c2.button("B. 70%左右", key="g08_g2_b", use_container_width=True):
            st.session_state.g08_guess2 = "70%"
            st.session_state.g08_phase = "lab"
            st.rerun()
        if c3.button("C. 30%左右", key="g08_g2_c", use_container_width=True):
            st.session_state.g08_guess2 = "30%"
            st.session_state.g08_phase = "lab"
            st.rerun()
        if c4.button("D. 10%以下", key="g08_g2_d", use_container_width=True, type="primary"):
            st.session_state.g08_guess2 = "10%以下"
            st.session_state.g08_phase = "lab"
            st.rerun()

    elif st.session_state.g08_phase == "lab":
        st.markdown("### 🧪 参数实验室")
        st.caption("拖动参数，看看报告单和真实患病概率怎么变化。")
        col_p, col_a = st.columns(2)
        with col_p:
            prevalence_live = st.slider("🦠 发病率", 0.01, 10.0, 0.1, 0.01, format="%.2f%%", key="g08_prev_live") / 100
        with col_a:
            accuracy_live = st.slider("🔬 检测准确率", 80.0, 99.9, 99.0, 0.1, format="%.1f%%", key="g08_acc_live") / 100
        ns_live = max(1, int(n * prevalence_live))
        nh_live = n - ns_live
        fp_live = int(nh_live * (1 - accuracy_live))
        total_pos_live = ns_live + fp_live
        ppv_live = ns_live / total_pos_live * 100 if total_pos_live > 0 else 0
        report_color = "#FF4757" if ppv_live < 30 else "#F0B90B" if ppv_live < 70 else "#00D4AA"
        report_emoji = "🔴" if ppv_live < 30 else "🟡" if ppv_live < 70 else "🟢"
        report_html = f'<div style="background:#1A1D24;border:2px solid {report_color};border-radius:16px;padding:24px;max-width:520px;margin:0 auto 20px auto;text-align:center;"><span style="font-size:12px;color:#8B8F98;letter-spacing:2px;">医学检测报告</span><hr style="border-color:#2A2D35;margin:8px 0;"><span style="font-size:46px;">{report_emoji}</span><br><span style="font-size:32px;font-weight:900;color:{report_color};">阳性</span><br><span style="color:#8B8F98;font-size:12px;">真实患病概率</span><br><span style="font-size:30px;font-weight:900;color:{report_color};">{ppv_live:.1f}%</span><br><span style="color:#8B8F98;font-size:11px;">阳性 {total_pos_live} 人中，真病人 {ns_live} 人</span></div>'
        st.markdown(report_html, unsafe_allow_html=True)
        tree_html = f'<div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:18px;line-height:1.8;font-family:monospace;">1000 人<br>├─ 真病人 {ns_live}<br>│  └─ 检测阳性 {ns_live}<br>└─ 健康人 {nh_live}<br>&nbsp;&nbsp;&nbsp;├─ 假阳性 {fp_live}<br>&nbsp;&nbsp;&nbsp;└─ 真阴性 {n - ns_live - fp_live}</div>'
        st.markdown("#### 🌳 树状分解图")
        st.markdown(tree_html, unsafe_allow_html=True)
        if st.button("▶ 现在揭晓为什么直觉会出错", key="g08_to_reveal", type="primary", use_container_width=True):
            st.session_state.g08_phase = "reveal"
            st.session_state.g08_final_ppv = ppv_live
            st.rerun()

    elif st.session_state.g08_phase == "reveal":
        final_ppv = st.session_state.get("g08_final_ppv", ppv)
        st.markdown(f"### 🎯 真实答案：阳性后真正患病的概率大约是 **{final_ppv:.1f}%**")
        compare_html = f'<div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:16px;"><span style="color:#E4E6EB;">第一次猜：<b>{st.session_state.g08_guess1}</b></span><br><span style="color:#E4E6EB;">第二次猜：<b>{st.session_state.g08_guess2}</b></span><br><span style="color:#F0B90B;">真实值：<b>{final_ppv:.1f}%</b></span></div>'
        st.markdown(compare_html, unsafe_allow_html=True)
        reveal_box("你被“99%准确率”吓到了——但它不是你最关心的概率",r"你真正想知道的是：<b>在阳性的人里，我得病的概率是多少？</b><br>这叫 $$P(患病\mid阳性)$$。<br><br>而“99%准确率”说的是另一个东西：$$P(阳性\mid患病)$$。<br>这两个概率不是一回事。<br><br>当疾病本身很罕见时，哪怕检测很准，也会有一批健康人被误报成阳性。","医学、测谎、风控、量化模型……所有高准确率场景里，最容易犯的错就是：把条件概率误当成后验概率。")
        math_detail(r"""**贝叶斯定理**
$$P(D\mid +)=\frac{P(+\mid D)P(D)}{P(+\mid D)P(D)+P(+\mid \neg D)P(\neg D)}$$
发病率 0.1%、准确率 99% 时：
$$P(D\mid +)=\frac{0.99\times0.001}{0.99\times0.001+0.01\times0.999}\approx 9\%$$""")
        if st.button("🔄 重新体检", key="g08_retry", use_container_width=True):
            reset_game("g08_")
            st.rerun()
        complete_game(8)
        update_radar("贝叶斯脑", 4)
def show_game_09():
    top_nav(9)
    chapter_banner(9)

    st.markdown(
        """
        <div class="game-card">
            <h3>📁 离奇档案</h3>
            <p style="color:#E4E6EB;font-size:15px;line-height:1.7;">
            你是一个喜欢“数据破案”的博主。今天你收到了一份神秘档案：<br>
            <i>“这两条曲线高度同步，背后一定藏着什么秘密。”</i><br>
            你的编辑只回了你一句：<b>“先别急着发。再查查。”</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = pd.read_csv(DATA_DIR / "spurious_correlations.csv")
    except Exception:
        st.error("数据文件未找到")
        return

    if "g09_phase" not in st.session_state:
        st.session_state.g09_phase = "cover"
        st.session_state.g09_idx = 0
        st.session_state.g09_first_judgment = None
        st.session_state.g09_final_judgment = None
        st.session_state.g09_evidence = set()

    if st.session_state.g09_phase not in ("cover", "inspect", "investigate", "final_judge", "reveal"):
        st.session_state.g09_phase = "cover"

    idx = st.session_state.g09_idx % len(df)
    row = df.iloc[idx]
    np.random.seed(idx + 42)
    years = list(range(2000, 2020))
    trend_x = np.cumsum(np.random.normal(0.5, 0.3, len(years)))
    trend_y = trend_x * 0.85 + np.random.normal(0, 0.15, len(years))
    r = np.corrcoef(trend_x, trend_y)[0, 1]

    if st.session_state.g09_phase == "cover":
        st.markdown(f"### 🗂️ 案卷 #{idx+1}：{row['title']}")
        st.markdown(
            f"""
            <div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:14px;padding:20px;">
                <span class='info-chip' style='background:#1a1515;color:#FF4757;border:1px solid #FF4757;'>危险等级：高相关</span>
                <span class='info-chip' style='background:#151a15;color:#00D4AA;border:1px solid #00D4AA;'>相关系数：{r:.2f}</span>
                <div style="margin-top:14px;color:#E4E6EB;font-size:14px;line-height:1.8;">
                    变量A：<b>{row['var_x']}</b><br>
                    变量B：<b>{row['var_y']}</b><br>
                    你看到的第一眼证据：<b>两条线几乎同步</b>。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### 🤔 第一直觉：你觉得这是什么类型的关系？")
        c1, c2, c3 = st.columns(3)
        if c1.button("🧨 这大概率是真因果", key="g09_cover_yes", use_container_width=True, type="primary"):
            st.session_state.g09_first_judgment = "cause"
            st.session_state.g09_phase = "inspect"
            st.rerun()
        if c2.button("🤔 有点可疑，再看看", key="g09_cover_maybe", use_container_width=True):
            st.session_state.g09_first_judgment = "suspicious"
            st.session_state.g09_phase = "inspect"
            st.rerun()
        if c3.button("❄️ 只是巧合吧", key="g09_cover_no", use_container_width=True):
            st.session_state.g09_first_judgment = "coincidence"
            st.session_state.g09_phase = "inspect"
            st.rerun()

    elif st.session_state.g09_phase == "inspect":
        st.markdown(f"### 📊 原始证据：{row['title']}")
        col1, col2 = st.columns(2)
        with col1:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(y=trend_x, mode='lines+markers', name=row['var_x'], line=dict(color='#00B4D8', width=2), yaxis='y1'))
            fig_line.add_trace(go.Scatter(y=trend_y, mode='lines+markers', name=row['var_y'], line=dict(color='#E07B39', width=2), yaxis='y2'))
            fig_line.update_layout(
                plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24",
                font={"color": "#E4E6EB"},
                xaxis={"gridcolor": "#2A2D35", "title": "年份"},
                yaxis=dict(title=row['var_x'], side='left', color='#00B4D8', gridcolor='#2A2D35'),
                yaxis2=dict(title=row['var_y'], side='right', overlaying='y', color='#E07B39', gridcolor='#2A2D35'),
                height=300, legend=dict(x=0.01, y=0.99),
                title={"text": "两条线几乎同步！", "font": {"color": "#E4E6EB", "size": 14}},
            )
            st.plotly_chart(fig_line, use_container_width=True)
        with col2:
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(x=trend_x, y=trend_y, mode='markers+text', text=years,
                                             textposition='top center', marker=dict(color='#F0B90B', size=8, opacity=0.8)))
            fig_scatter.update_layout(
                plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24",
                font={"color": "#E4E6EB"},
                xaxis={"gridcolor": "#2A2D35", "title": row['var_x']},
                yaxis={"gridcolor": "#2A2D35", "title": row['var_y']},
                height=300,
                title={"text": f"散点相关：r = {r:.3f}", "font": {"color": "#E4E6EB", "size": 14}},
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("#### 📰 如果你现在就发推文，你会写什么标题？")
        c1, c2, c3 = st.columns(3)
        if c1.button("“A 导致了 B！”", key="g09_headline_ab", use_container_width=True, type="primary"):
            st.session_state.g09_phase = "investigate"
            st.rerun()
        if c2.button("“它们只是相关”", key="g09_headline_corr", use_container_width=True):
            st.session_state.g09_phase = "investigate"
            st.rerun()
        if c3.button("“我要再查一个变量”", key="g09_headline_more", use_container_width=True):
            st.session_state.g09_phase = "investigate"
            st.rerun()

    elif st.session_state.g09_phase == "investigate":
        st.markdown("### 🕵️ 调查模式：再查三条证据")
        st.caption("不要急着给答案。不同档案的真相不一样——你要像侦探一样去查。")

        evidence_bank = {
            "冰淇淋与溺亡": {
                "temp": ("🌡️ 调气温记录", f"气温曲线与 {row['var_x']} 和 {row['var_y']} 都高度同步。天气热 → 冰淇淋销量上升，也更容易有人去游泳。"),
                "season": ("📅 看季节分布", "高值几乎都出现在夏季。‘季节’本身就足以让两条线同时抬升。"),
                "experiment": ("🧪 想象实验", "如果你真要验证‘冰淇淋导致溺亡’，你得在同样气温、同样游泳人数下只改变冰淇淋销量——现实中几乎做不到。"),
            },
            "尼古拉斯·凯奇与泳池": {
                "temp": ("🎬 调电影时间线", "凯奇拍片数量的高低来自片约周期，泳池溺亡来自夏季活动频率——两者只是恰好在某几年同向波动。"),
                "season": ("📅 看年份段落", "把年份切成前后两段后，相关性明显不稳定——这不是一个稳定机制，更像巧合。"),
                "experiment": ("🧪 想象实验", "如果凯奇少拍一部电影，泳池溺亡会变少吗？这个命题本身就荒谬，说明你其实并不真的相信它有因果关系。"),
            },
            "奶酪与被床单缠死": {
                "temp": ("🧀 调消费背景", "奶酪消费受饮食文化和市场推广影响，床单窒息死亡是极低概率意外事件——缺少任何可信共同机制。"),
                "season": ("📅 看波动细节", "两条线只有粗略趋势接近，细看峰谷并不一致——高相关来自稀疏数据和偶然同步。"),
                "experiment": ("🧪 想象实验", "让一群人多吃奶酪，然后观察床单事故是否增加？一旦你把问题说出来，就知道它更像随机巧合。"),
            },
            "手机与谋杀": {
                "temp": ("📈 调人口/时间趋势", "智能手机普及率和很多社会指标都会随时间上升——‘一起上涨’并不能说明手机导致了什么。"),
                "season": ("📅 看增速变化", "手机销量在某些年份猛增，谋杀案却没有同步幅度变化——趋势的斜率并不一致。"),
                "experiment": ("🧪 想象实验", "如果某地一夜之间禁用手机，谋杀案会立刻下降吗？你会发现自己无法给出可信的机制链条。"),
            },
            "有机食品与自闭症": {
                "temp": ("🛒 调健康意识/诊断变化", "有机食品增长来自消费升级，自闭症诊断增加来自诊断标准和认知提升——两者背后的社会趋势不同但同向。"),
                "season": ("📅 看长期趋势", "这是典型的‘两条长期上升曲线’：只要都跟时间一起涨，相关系数就会被轻易抬高。"),
                "experiment": ("🧪 想象实验", "让人群改吃有机食品，然后观察自闭症诊断是否变化？你会马上发现这个因果命题在逻辑上并不成立。"),
            },
        }
        case_evidence = evidence_bank.get(row['title'], {
            "temp": ("🔍 调隐藏变量", f"{row['hidden_variable']} 的变化与两条线都有关，它可能在同时推动两边。"),
            "season": ("📅 看时间结构", "时间分布显示两条线可能只是共同追随某种背景趋势。"),
            "experiment": ("🧪 想象实验", "如果你真的要验证 A 导致 B，就需要控制第三个因素做干预实验。"),
        })

        c1, c2, c3 = st.columns(3)
        if c1.button(case_evidence['temp'][0], key="g09_ev_temp", use_container_width=True):
            st.session_state.g09_evidence.add("temp")
            st.rerun()
        if c2.button(case_evidence['season'][0], key="g09_ev_season", use_container_width=True):
            st.session_state.g09_evidence.add("season")
            st.rerun()
        if c3.button(case_evidence['experiment'][0], key="g09_ev_experiment", use_container_width=True):
            st.session_state.g09_evidence.add("experiment")
            st.rerun()

        if "temp" in st.session_state.g09_evidence:
            st.info(case_evidence['temp'][1])
        if "season" in st.session_state.g09_evidence:
            st.warning(case_evidence['season'][1])
        if "experiment" in st.session_state.g09_evidence:
            st.error(case_evidence['experiment'][1])

        if len(st.session_state.g09_evidence) >= 2:
            if st.button("▶ 我已经掌握 enough 证据，做最终判断", key="g09_to_final", type="primary", use_container_width=True):
                st.session_state.g09_phase = "final_judge"
                st.rerun()

    elif st.session_state.g09_phase == "final_judge":
        st.markdown("### ⚖️ 最终判断")
        st.markdown("现在，你认为什么解释最合理？")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button(f"{row['var_x']} → {row['var_y']}", key="g09_final_ab", use_container_width=True):
            st.session_state.g09_final_judgment = "AB"
            st.session_state.g09_phase = "reveal"
            st.rerun()
        if c2.button(f"{row['var_y']} → {row['var_x']}", key="g09_final_ba", use_container_width=True):
            st.session_state.g09_final_judgment = "BA"
            st.session_state.g09_phase = "reveal"
            st.rerun()
        if c3.button("第三变量同时驱动", key="g09_final_hidden", use_container_width=True, type="primary"):
            st.session_state.g09_final_judgment = "hidden"
            st.session_state.g09_phase = "reveal"
            st.rerun()
        if c4.button("只是巧合", key="g09_final_coincidence", use_container_width=True):
            st.session_state.g09_final_judgment = "coincidence"
            st.session_state.g09_phase = "reveal"
            st.rerun()

    elif st.session_state.g09_phase == "reveal":
        ans = st.session_state.g09_final_judgment
        correct = ans == "hidden"
        if correct:
            st.success(f"✅ 你查出了幕后黑手：{row['hidden_variable']}")
        else:
            st.error(f"❌ 真相不是你选的那个。最合理的解释是：隐藏变量『{row['hidden_variable']}』在同时推动两条线。")
        st.info(row['explanation'])
        reveal_box(
            "相关高得吓人，但两条线仍然可能毫无因果关系",
            f"你第一次的直觉是：**{st.session_state.g09_first_judgment}**。<br>"
            f"最后你判断的是：**{ans}**。<br><br>"
            f"这份档案的关键不是相关系数 {r:.3f}，而是你忽略了 <b>{row['hidden_variable']}</b>。<br>"
            f"它像一只看不见的手，同时拉动了 {row['var_x']} 和 {row['var_y']}，让它们看起来像在互相因果。<br><br>"
            f"这就叫：<b>相关不等于因果</b>。",
            "很多“惊天秘密”其实只是背景变量在作祟。你看到两条线一起动，直觉会自动补出因果箭头——但真正的箭头，可能根本没连在它们之间。",
        )
        math_detail(r"""
**虚假相关**：$$\mathrm{Corr}(X,Y)>0.9$$ 并不意味着 $$X\to Y$$。
更常见的结构是：$$X \leftarrow Z \rightarrow Y$$
其中 $$Z$$（比如气温、季节、人口规模、时间趋势）同时推动 $$X$$ 和 $$Y$$。

相关是对称的：$$\mathrm{Corr}(X,Y)=\mathrm{Corr}(Y,X)$$
但因果不是对称的。
""")
        c1, c2 = st.columns(2)
        if c1.button("▶ 查看下一份档案", key="g09_next_case", use_container_width=True, type="primary"):
            st.session_state.g09_idx += 1
            st.session_state.g09_phase = "cover"
            st.session_state.g09_first_judgment = None
            st.session_state.g09_final_judgment = None
            st.session_state.g09_evidence = set()
            st.rerun()
        if c2.button("🔄 重置全部档案", key="g09_reset_all", use_container_width=True):
            reset_game("g09_")
            st.rerun()
        complete_game(9)
        update_radar("因果链条", 4 if correct else 2)


# ═══════════════════════════════════════════════════════════
# 游戏 10: 鸡与蛋 (因果倒置)
# ═══════════════════════════════════════════════════════════
def show_game_10():
    top_nav(10)
    chapter_banner(10)
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#1A1D24 0%,#15101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;">
            <div style="display:flex;gap:20px;align-items:start;">
                <span style="font-size:48px;">🐔</span>
                <div>
                    <h3 style="color:#E07B39;margin:0 0 8px 0;">鸡与蛋</h3>
                    <p style="color:#E4E6EB;font-size:15px;line-height:1.7;">三位委托人，各自带着一份“看起来很有道理”的数据结论来找你。<br>你的任务不是只答题，而是像侦探一样识别：<b>这句话到底是真的找到因果，还是把箭头画反了？</b></p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cases={
        "A":{"client":"👓 眼镜公司老板","data":"戴眼镜的人平均智商高 8 分。p<0.001。","claim":"推广眼镜→让下一代更聪明。","truth":"高智商 → 更爱学习 → 更容易近视 → 需要眼镜。不是眼镜让人聪明。","timeline":["👶 童年视力习惯","👓 近视形成 / 配眼镜","📚 长期学习","🧠 智力测验更高"]},
        "B":{"client":"🚒 消防局长","data":"派出去的消防员越多，火灾财产损失越大。","claim":"减少消防员→降低损失。","truth":"大火 → 派出更多消防员 → 财产损失更大。不是消防员导致损失上升。","timeline":["🔥 火势扩大","🚒 派出更多消防员","🏚️ 财产损失上升"]},
        "C":{"client":"🏥 医院院长","data":"住院时间越长的人，死亡率越高。","claim":"尽早出院→减少死亡。","truth":"病情更重 → 住院更久 → 死亡率更高。不是住院害死人。","timeline":["🧬 基础病情严重","🏥 住院时间更长","☠️ 死亡率更高"]},
    }
    if "g10_phase" not in st.session_state:
        st.session_state.g10_phase="desk"
        st.session_state.g10_current=None
        st.session_state.g10_results={}
        st.session_state.g10_first_impression={}
        st.session_state.g10_arrow_choice={}
    if st.session_state.g10_phase not in ("desk","case","reveal","summary"):
        st.session_state.g10_phase="desk"

    if st.session_state.g10_phase=="desk":
        st.markdown("### 🗂️ 案件桌面")
        cols=st.columns(3)
        for i,key in enumerate(["A","B","C"]):
            case=cases[key];done=key in st.session_state.g10_results
            border="#00D4AA" if done else "#2A2D35"
            status="✅ 已处理" if done else "待调查"
            status_color="#00D4AA" if done else "#8B8F98"
            with cols[i]:
                st.markdown(f"<div style='background:#1A1D24;border:2px solid {border};border-radius:14px;padding:18px;min-height:170px;'><span style='font-size:28px;'>{case['client'].split()[0]}</span><br><span style='color:#E4E6EB;font-weight:800;font-size:18px;'>案卷 {key}</span><br><span style='color:#8B8F98;font-size:13px;'>{case['client']}</span><br><br><span style='color:#E4E6EB;font-size:13px;'>{case['data']}</span><br><span style='color:{status_color};font-size:12px;'>{status}</span></div>",unsafe_allow_html=True)
                if st.button(f"打开案卷 {key}",key=f"g10_open_{key}",use_container_width=True):
                    st.session_state.g10_current=key
                    st.session_state.g10_phase="case"
                    st.rerun()
        if len(st.session_state.g10_results)==3 and st.button("📊 查看结案总结",key="g10_to_summary",type="primary",use_container_width=True):
            st.session_state.g10_phase="summary"
            st.rerun()

    elif st.session_state.g10_phase=="case":
        ck=st.session_state.g10_current
        case=cases[ck]
        st.markdown(f"### 📋 案卷 {ck}：{case['client']}")
        st.markdown(f"📊 **数据摘要**：{case['data']}")
        st.markdown(f"💬 **委托人结论**：*{case['claim']}*")
        if ck not in st.session_state.g10_first_impression:
            st.markdown("#### 第一反应：这个结论看起来靠谱吗？")
            c1,c2,c3=st.columns(3)
            if c1.button("✅ 好像有道理",key=f"g10_imp_yes_{ck}",use_container_width=True): st.session_state.g10_first_impression[ck]="seems_right"; st.rerun()
            if c2.button("🤔 感觉有问题",key=f"g10_imp_maybe_{ck}",use_container_width=True): st.session_state.g10_first_impression[ck]="suspicious"; st.rerun()
            if c3.button("❓ 我不确定",key=f"g10_imp_unsure_{ck}",use_container_width=True): st.session_state.g10_first_impression[ck]="unsure"; st.rerun()
            return
        st.info(f"你的第一反应：**{st.session_state.g10_first_impression[ck]}**")
        st.markdown("#### 现在真正判断：因果箭头怎么画？")
        cc=st.columns(4)
        if cc[0].button("A→B",key=f"g10_{ck}_ab",use_container_width=True): st.session_state.g10_arrow_choice[ck]="AB"; st.session_state.g10_results[ck]=False; st.session_state.g10_phase="reveal"; st.rerun()
        if cc[1].button("B→A",key=f"g10_{ck}_ba",use_container_width=True,type="primary"): st.session_state.g10_arrow_choice[ck]="BA"; st.session_state.g10_results[ck]=True; st.session_state.g10_phase="reveal"; st.rerun()
        if cc[2].button("🔄 双向",key=f"g10_{ck}_both",use_container_width=True): st.session_state.g10_arrow_choice[ck]="both"; st.session_state.g10_results[ck]=False; st.session_state.g10_phase="reveal"; st.rerun()
        if cc[3].button("❌ 无关",key=f"g10_{ck}_none",use_container_width=True): st.session_state.g10_arrow_choice[ck]="none"; st.session_state.g10_results[ck]=False; st.session_state.g10_phase="reveal"; st.rerun()

    elif st.session_state.g10_phase=="reveal":
        ck=st.session_state.g10_current
        case=cases[ck]
        correct=st.session_state.g10_results[ck]
        if correct: st.success("✅ 你看出来了：他们把箭头画反了。")
        else: st.error("❌ 问题不在相关本身，而在于因果方向被画反了。")
        st.markdown("### ⏱️ 时间轴揭示")
        timeline_html='<div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:18px;">'
        for i,item in enumerate(case['timeline']):
            timeline_html += f'<div style="color:#E4E6EB;font-size:15px;line-height:1.8;">{item}</div>'
            if i < len(case['timeline']) - 1:
                timeline_html += '<div style="color:#8B8F98;font-size:20px;">↓</div>'
        timeline_html += '</div>'
        st.markdown(timeline_html,unsafe_allow_html=True)
        st.markdown(f"### 🔍 真相\n**{case['truth']}**")
        if len(st.session_state.g10_results)<3:
            if st.button("📂 回到案件桌面，处理下一案",key="g10_back_to_desk",type="primary",use_container_width=True):
                st.session_state.g10_phase="desk"; st.session_state.g10_current=None; st.rerun()
        else:
            if st.button("📊 查看结案总结",key="g10_summary_now",type="primary",use_container_width=True): st.session_state.g10_phase="summary"; st.rerun()

    elif st.session_state.g10_phase=="summary":
        st.markdown("### 🧾 结案总结")
        rows=[]
        for ck,case in cases.items():
            first=st.session_state.g10_first_impression.get(ck,'-')
            arrow=st.session_state.g10_arrow_choice.get(ck,'-')
            ok='✅' if st.session_state.g10_results.get(ck) else '❌'
            rows.append(f"| {ck} | {case['client']} | {first} | {arrow} | {ok} |")
        table='| 案卷 | 委托人 | 你第一反应 | 你最终判断 | 结果 |\n|------|--------|------------|------------|------|\n' + '\n'.join(rows)
        st.markdown(table)
        correct_n=sum(1 for v in st.session_state.g10_results.values() if v)
        reveal_box("横截面相关无法告诉你因果方向",f"你共处理了 3 个案子，答对了 <b>{correct_n}/3</b>。<br>真正的问题不是相关强不强，而是：<b>谁先发生，谁后发生？</b><br>时间顺序和干预，才是决定箭头方向的关键。","喝红酒的人更健康？加班多的人升职更快？看到相关，先问：箭头凭什么这样画？")
        math_detail(r"""在横截面数据里，$$X$$ 与 $$Y$$ 的统计关联并不能区分：
$$X \to Y \quad \text{还是} \quad Y \to X$$
只有时间顺序（temporal ordering）或实验干预（intervention）能帮助识别因果方向。
$$P(Y\mid X) \neq P(Y\mid do(X))$$""")
        if st.button("🔄 重新办案",key="g10_retry",use_container_width=True): reset_game("g10_"); st.rerun()
        complete_game(10)
        update_radar("因果链条",4 if correct_n>=2 else 2)

# ═══════════════════════════════════════════════════════════
# 游戏 11: 幕后黑手 (遗漏变量)
# ═══════════════════════════════════════════════════════════
def show_game_11():
    top_nav(11);chapter_banner(11)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#1a1510 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🕵️</span><div><h3 style="color:#E07B39;margin:0 0 8px 0;">幕后黑手</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">咖啡连锁被指控“喝咖啡导致心脏病”——发病率高 <b>40%</b>。<br>老板找你危机公关：<i>“去查查数据到底有没有问题。”</i></p></div></div></div>""",unsafe_allow_html=True)
    if "g11_data" not in st.session_state or "late_night" not in st.session_state.g11_data.columns:
        np.random.seed(123);n=500
        late_night=np.random.binomial(1,0.3,n)
        coffee=np.where(late_night==1,np.random.normal(5,2,n),np.random.normal(2,1.5,n));coffee=np.clip(coffee,0,10)
        heart=40+coffee*0.1+late_night*15+np.random.normal(0,5,n)
        st.session_state.g11_data=pd.DataFrame({"coffee":coffee,"late_night":late_night,"heart_risk":heart});st.session_state.g11_stage="act1"
    df=st.session_state.g11_data
    if st.session_state.g11_stage=="act1":
        st.markdown("### 🎬 第一幕：铁证如山")
        fig=go.Figure();fig.add_trace(go.Scatter(x=df["coffee"],y=df["heart_risk"],mode='markers',marker=dict(color='#E07B39',size=6,opacity=0.6)))
        z=np.polyfit(df["coffee"],df["heart_risk"],1);x_line=np.linspace(0,10,50);fig.add_trace(go.Scatter(x=x_line,y=np.polyval(z,x_line),mode='lines',line=dict(color='#FF4757',width=2)))
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"每日咖啡杯数"},yaxis={"gridcolor":"#2A2D35","title":"心脏病风险"},height=350)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("#### 💭 咖啡应该为此负责吗？")
        c1,c2,c3=st.columns(3)
        if c1.button("✅ 是",key="g11_yes",use_container_width=True): st.session_state.g11_judge="yes";st.session_state.g11_stage="act2";st.rerun()
        if c2.button("🤔 不确定",key="g11_unsure",use_container_width=True): st.session_state.g11_judge="unsure";st.session_state.g11_stage="act2";st.rerun()
        if c3.button("❌ 感觉有问题",key="g11_no",use_container_width=True): st.session_state.g11_judge="no";st.session_state.g11_stage="act2";st.rerun()
    elif st.session_state.g11_stage=="act2":
        st.markdown("### 🎬 第二幕：幕后黑手现身")
        st.markdown("有个变量他们没给你看——**长期熬夜**。")
        late=df[df["late_night"]==1];normal=df[df["late_night"]==0]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=late["coffee"],y=late["heart_risk"],mode='markers',marker=dict(color='#FF4757',size=6,opacity=0.5),name='长期熬夜'))
        fig.add_trace(go.Scatter(x=normal["coffee"],y=normal["heart_risk"],mode='markers',marker=dict(color='#00B4D8',size=6,opacity=0.5),name='作息正常'))
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"每日咖啡杯数"},yaxis={"gridcolor":"#2A2D35","title":"心脏病风险"},height=350)
        st.plotly_chart(fig,use_container_width=True)
        st.success("长期熬夜组和作息正常组内部，咖啡与心脏病的关系几乎消失了。真正把两者同时推高的，是长期熬夜。")
        reveal_box("咖啡不是罪魁祸首——是长期熬夜这个没被看到的变量","第一眼看数据时，咖啡和心脏病风险确实相关。<br>但长期熬夜的人往往喝更多咖啡，同时心血管风险也更高。<br>那个“+40%”并不是咖啡直接造成的，而是熬夜这个第三变量在背后同时影响两边。<br><b>这就是遗漏变量偏差。</b>","就像“学音乐的孩子成绩更好”，真正可能在起作用的并不是音乐本身，而是家庭资源、教育投入这些没被写进表格里的变量。",f"遗漏变量偏差。玩家判断={st.session_state.g11_judge}。混杂变量=长期熬夜。",11)
        math_detail("**DAG** 咖啡$$(X)\\leftarrow$$长期熬夜$$(Z)\\rightarrow$$心脏病$$(Y)$$。<br>如果不控制 $$Z$$，你就会把 $$X$$ 和 $$Y$$ 之间的虚假相关误认为因果。")
        if st.button("🔄 重新调查",key="g11_retry",use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("g11_"): del st.session_state[k]
            st.rerun()
        complete_game(11);update_radar("混淆嗅觉",4)

# ═══════════════════════════════════════════════════════════
# 游戏 12: 星光错觉 (对撞偏差)
# ═══════════════════════════════════════════════════════════
def show_game_12():
    top_nav(12);chapter_banner(12)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#1a1510 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🌟</span><div><h3 style="color:#E07B39;margin:0 0 8px 0;">星光错觉</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">💬 选角导演：<i>"好看演员演技都差，两者天然互斥。我当了三十年选角导演！"</i><br>💬 助理：<i>"老板，我给你看个东西。"</i></p></div></div></div>""",unsafe_allow_html=True)
    if "g12_beauty" not in st.session_state:
        np.random.seed(42);n=300
        st.session_state.g12_beauty=np.random.normal(50,15,n);st.session_state.g12_talent=np.random.normal(50,15,n);st.session_state.g12_phase="story"
    if st.session_state.g12_phase not in ("story","explore","reveal"): st.session_state.g12_phase="story"
    beauty=st.session_state.g12_beauty;talent=st.session_state.g12_talent
    if st.session_state.g12_phase=="story":
        r_all=np.corrcoef(beauty,talent)[0,1]
        fig=go.Figure();fig.add_trace(go.Scatter(x=beauty,y=talent,mode='markers',marker=dict(color='#8B8F98',size=5,opacity=0.5)))
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"颜值"},yaxis={"gridcolor":"#2A2D35","title":"演技"},height=360,title={"text":f"全部报名者：r={r_all:.3f}——颜值和演技毫无关系！","font":{"color":"#E4E6EB","size":14}})
        st.plotly_chart(fig,use_container_width=True);st.success(f"📊 r={r_all:.3f}——完全独立，毫无关系。")
        st.markdown("#### 🤔 那为什么导演会觉得'好看=没演技'？")
        c1,c2=st.columns(2)
        if c1.button("因为他只看被录取的演员",key="g12_a1",use_container_width=True,type="primary"): st.session_state.g12_phase="explore";st.rerun()
        if c2.button("因为确实负相关",key="g12_a2",use_container_width=True): st.session_state.g12_phase="explore";st.rerun()
    elif st.session_state.g12_phase=="explore":
        threshold=st.slider("🎚️ 录取线(颜值+演技)",50,150,110)
        sel=beauty+talent>=threshold;bs=beauty[sel];ts=talent[sel];r_all=np.corrcoef(beauty,talent)[0,1];r_sel=np.corrcoef(bs,ts)[0,1] if len(bs)>10 else 0
        col_a,col_s=st.columns(2)
        with col_a:
            fig1=go.Figure();fig1.add_trace(go.Scatter(x=beauty,y=talent,mode='markers',marker=dict(color='#8B8F98',size=5,opacity=0.4)))
            xl=np.linspace(0,100,50);fig1.add_trace(go.Scatter(x=xl,y=np.clip(threshold-xl,0,100),mode='lines',line=dict(color='#E07B39',width=2,dash='dash'),name=f'录取线={threshold}'))
            fig1.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"颜值"},yaxis={"gridcolor":"#2A2D35","title":"演技"},height=320,title=f"r={r_all:.3f}(无关)")
            st.plotly_chart(fig1,use_container_width=True)
        with col_s:
            fig2=go.Figure();fig2.add_trace(go.Scatter(x=bs,y=ts,mode='markers',marker=dict(color='#E07B39',size=7,opacity=0.7)))
            fig2.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"颜值"},yaxis={"gridcolor":"#2A2D35","title":"演技"},height=320,title=f"r={r_sel:.3f}"+("(伪负相关！)" if r_sel<-0.2 else ""))
            st.plotly_chart(fig2,use_container_width=True)
        st.markdown(f"📊 全人群r={r_all:.3f}→录取后r={r_sel:.3f}→{'🔴虚假负相关！' if r_sel<-0.2 else '调整阈值'}")
        if abs(r_sel)>0.2 and r_sel<0:
            if st.button("💡 我看到负相关了！为什么？",key="g12_reveal",type="primary",use_container_width=True): st.session_state.g12_phase="reveal";st.rerun()
    if st.session_state.g12_phase=="reveal":
        sel=beauty+talent>=110;r_all=np.corrcoef(beauty,talent)[0,1];r_sel=np.corrcoef(beauty[sel],talent[sel])[0,1]
        reveal_box("你看到的负相关——是你自己选的",f"全部报名者中颜值和演技<b>完全独立</b>(r={r_all:.3f})。<br>但当你只选'总分够高'的人——负相关出现了(r={r_sel:.3f})。<br>控制一个<b>对撞变量</b>(是否被录取)，在两个独立变量间<b>凭空创造</b>了负相关。","'漂亮女生都高冷'——你只敢搭讪好看的，好看且热情的早就有对象了。'有钱人都抠'——你只在有钱但不花钱的人里观察。",f"对撞偏差。全人群r={r_all:.3f}，演员子集r={r_sel:.3f}。",12)
        math_detail("全部$$\\text{Corr}(B,T)=0$$ 控制对撞后$$\\text{Corr}(B,T\\mid B+T\\geq\\theta)<0$$ $$B\\rightarrow[录取]\\leftarrow T$$")
        if st.button("🔄 重新体验",key="g12_again",use_container_width=True,type="primary"):
            for k in list(st.session_state.keys()):
                if k.startswith("g12_"): del st.session_state[k]
            st.rerun()
        complete_game(12);update_radar("样本警觉",4 if r_sel<-0.3 else 2)

# ═══════════════════════════════════════════════════════════
# 游戏 13: 收缩魔法 (James-Stein)
# ═══════════════════════════════════════════════════════════
def show_game_13():
    top_nav(13)
    chapter_banner(13)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#15101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🪄</span><div><h3 style="color:#9B59B6;margin:0 0 8px 0;">收缩魔法</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">老板丢给你一批调查数据：<b>5000 个城市</b>，每个城市都做了一次很小样本民调。<br>你的任务不是预测单次结果，而是估计每个城市的<b>真实平均支持率 / 真实均值</b>。<br>💬 实习生：<i>“别直接相信每个城市的样本均值，把它们都往 0（总体平均）缩一点，反而更准。”</i><br>💬 全办公室：<i>“你疯了？这些城市彼此无关，怎么能互相借信息？”</i></p></div></div></div>""",unsafe_allow_html=True)

    if "g13_phase" not in st.session_state:
        st.session_state.g13_phase = "bet"
        st.session_state.g13_d = 50
        st.session_state.g13_has_result = False

    if st.session_state.g13_phase not in ("bet", "experiment", "final_reveal"):
        st.session_state.g13_phase = "bet"

    if st.session_state.g13_phase == "bet":
        st.markdown("### 🤔 你站哪边？")
        c1, c2, c3 = st.columns(3)
        if c1.button("🤬 胡扯！各管各的才最优", key="g13_b1", use_container_width=True, type="primary"):
            st.session_state.g13_bet = "mle"
            st.session_state.g13_phase = "experiment"
            st.rerun()
        if c2.button("🤔 说不清，先实验", key="g13_b2", use_container_width=True):
            st.session_state.g13_bet = "unsure"
            st.session_state.g13_phase = "experiment"
            st.rerun()
        if c3.button("🪄 说不定真有道理", key="g13_b3", use_container_width=True):
            st.session_state.g13_bet = "js"
            st.session_state.g13_phase = "experiment"
            st.rerun()

    elif st.session_state.g13_phase == "experiment":
        st.markdown("### 🔬 收缩实验室")
        d = st.slider("同时估计几个参数？", 1, 5000, st.session_state.g13_d, key="g13_ds")
        st.session_state.g13_d = d

        col_left, col_right = st.columns([1.15, 1])
        with col_left:
            st.markdown("#### 🎯 先看直觉图景")
            st.caption("这里每一个点表示一个“城市真实平均支持率”的估计。灰点 = 直接把样本均值当真 (MLE)；紫点 = 把样本均值往总体平均 0 收缩一点 (JS)。")
        with col_right:
            st.markdown(f"<div class='metric-panel'><span class='stat-label'>当前维度</span><br><span class='big-number' style='font-size:32px;color:#9B59B6;'>{d}</span></div>", unsafe_allow_html=True)

        if st.button("🎲 随机生成一组参数并比较", key="g13_gen", type="primary", use_container_width=True):
            np.random.seed(int(time.time()))
            true_theta = np.random.normal(0, 3, d)
            X = true_theta + np.random.normal(0, 1, d)
            mle_mse = np.mean((X - true_theta) ** 2)
            shrink = max(0, 1 - (d - 2) / np.sum(X ** 2)) if d >= 3 else 1.0
            js = shrink * X
            js_mse = np.mean((js - true_theta) ** 2)
            st.session_state.g13_true = true_theta
            st.session_state.g13_X = X
            st.session_state.g13_js_vals = js
            st.session_state.g13_mle = mle_mse
            st.session_state.g13_js = js_mse
            st.session_state.g13_has_result = True
            st.rerun()

        if st.session_state.get("g13_has_result"):
            true_theta = st.session_state.g13_true
            X = st.session_state.g13_X
            js = st.session_state.g13_js_vals
            mle_mse = st.session_state.g13_mle
            js_mse = st.session_state.g13_js
            shrink = max(0, 1 - (d - 2) / np.sum(X ** 2)) if d >= 3 else 1.0

            c1, c2, c3 = st.columns(3)
            c1.metric("🅰️ MLE 的 MSE", f"{mle_mse:.4f}")
            delta = mle_mse - js_mse
            c2.metric("🅱️ JS 的 MSE", f"{js_mse:.4f}", delta=f"降低 {delta:.4f}" if delta > 0 else f"升高 {-delta:.4f}")
            c3.metric("🔧 收缩强度", f"{shrink:.4f}")

            # 同维度重复实验：让用户看见“不是偶然一次”
            st.markdown("#### 🔁 同一个维度，重复实验 20 次会怎样？")
            if st.button("🔁 重复实验 20 次", key="g13_repeat", use_container_width=True):
                rep_results = []
                for _ in range(20):
                    th = np.random.normal(0, 3, d)
                    xx = th + np.random.normal(0, 1, d)
                    mm = np.mean((xx - th) ** 2)
                    if d >= 3:
                        ss = max(0, 1 - (d - 2) / np.sum(xx ** 2))
                        jj = np.mean((ss * xx - th) ** 2)
                    else:
                        jj = mm
                    rep_results.append((mm, jj, (1 - jj / mm) * 100 if mm > 0 else 0))
                better_count = sum(1 for mm, jj, _ in rep_results if jj < mm)
                fig_rep = go.Figure()
                fig_rep.add_trace(go.Scatter(y=[m for m, _, _ in rep_results], mode='lines+markers',
                                             line=dict(color='#FF4757', width=2), name='MLE'))
                fig_rep.add_trace(go.Scatter(y=[j for _, j, _ in rep_results], mode='lines+markers',
                                             line=dict(color='#9B59B6', width=2), name='JS'))
                fig_rep.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color": "#E4E6EB"},
                                      xaxis={"gridcolor": "#2A2D35", "title": "重复实验编号"},
                                      yaxis={"gridcolor": "#2A2D35", "title": "MSE"}, height=260)
                st.plotly_chart(fig_rep, use_container_width=True)
                st.markdown(f"<div style='background:#1A1D24;border:1px solid #2A2D35;border-radius:10px;padding:12px;'><span style='color:#E4E6EB;'>在当前维度 <b>{d}</b> 下，JS 在 <b>{better_count}/20</b> 次实验里比 MLE 更准。</span></div>", unsafe_allow_html=True)

            # 收缩靶心 / 总体平均线
            st.markdown("#### 🎯 收缩靶心：所有城市都被往哪里拉？")
            overall_mean = 0.0
            fig_target = go.Figure()
            fig_target.add_trace(go.Scatter(x=[overall_mean], y=[0], mode='markers+text',
                                            marker=dict(size=26, color='#9B59B6', symbol='x'),
                                            text=['总体平均 0'], textposition='top center',
                                            textfont=dict(color='#E4E6EB', size=14), name='收缩靶心'))
            sample_show = min(25, d)
            sample_vals = X[:sample_show]
            js_show = js[:sample_show]
            fig_target.add_trace(go.Scatter(x=sample_vals, y=list(range(sample_show)), mode='markers',
                                            marker=dict(size=8, color='#8B8F98'), name='MLE 样本均值'))
            fig_target.add_trace(go.Scatter(x=js_show, y=list(range(sample_show)), mode='markers',
                                            marker=dict(size=8, color='#00D4AA'), name='JS 收缩后'))
            for i in range(sample_show):
                fig_target.add_shape(type='line', x0=sample_vals[i], x1=js_show[i], y0=i, y1=i,
                                     line=dict(color='#9B59B6', width=1, dash='dot'))
            fig_target.add_vline(x=0, line_color='#9B59B6', line_width=2)
            fig_target.update_layout(
                plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24",
                font={"color": "#E4E6EB"},
                xaxis={"gridcolor": "#2A2D35", "title": "估计值（越极端越会被拉回0）"},
                yaxis={"gridcolor": "#2A2D35", "visible": False},
                height=260,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0)
            )
            st.plotly_chart(fig_target, use_container_width=True)
            st.caption("紫色 X = 收缩靶心（总体平均 0）。灰点是原始样本均值，绿点是收缩后的估计。离 0 越远，拉回得越狠。")

            if d < 3:
                st.info(f"d={d} 时，James-Stein 理论上没有统一优势；这正好是它最反直觉的地方——维度一到 3 以上，世界就变了。")
            elif js_mse < mle_mse:
                st.success(f"✅ 这次实验里，JS 比 MLE 低了 {(1 - js_mse / mle_mse) * 100:.1f}% 的误差。")
            else:
                st.warning("这一次随机样本上看不出明显优势，但从整体理论和大量重复实验看，d≥3 时 JS 的总体风险更低。")

            # 可视化1：选前20个参数，展示真实值/观测值/收缩值
            k = min(20, d)
            idxs = np.arange(k)
            fig_points = go.Figure()
            fig_points.add_trace(go.Scatter(x=idxs, y=true_theta[:k], mode='markers+lines', name='真实值 θ', line=dict(color='#00D4AA', width=1), marker=dict(size=8, color='#00D4AA')))
            fig_points.add_trace(go.Scatter(x=idxs, y=X[:k], mode='markers', name='MLE=观测值', marker=dict(size=9, color='#8B8F98')))
            fig_points.add_trace(go.Scatter(x=idxs, y=js[:k], mode='markers', name='JS 收缩后', marker=dict(size=9, color='#9B59B6')))
            for i in range(k):
                fig_points.add_shape(type='line', x0=i, x1=i, y0=js[i], y1=X[i], line=dict(color='#9B59B6', width=1, dash='dot'))
            fig_points.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color": "#E4E6EB"}, xaxis={"gridcolor": "#2A2D35", "title": "参数编号（前20个）"}, yaxis={"gridcolor": "#2A2D35", "title": "估计值"}, height=340, title={"text": "MLE 与 JS 在前 20 个参数上的对比", "font": {"color": "#E4E6EB", "size": 15}})
            st.plotly_chart(fig_points, use_container_width=True)
            st.caption("紫色虚线表示：JS 把每个观测值往 0 的方向拉回了一点。极端值被拉得更多。")

            # 极端值案例卡
            st.markdown("#### 🧾 极端值观察名单（最容易被骗的样本）")
            extreme_idx = np.argsort(np.abs(X))[-5:][::-1]
            for rank, i in enumerate(extreme_idx, 1):
                delta_to_truth = abs(X[i] - true_theta[i]) - abs(js[i] - true_theta[i])
                better = "JS 更近" if delta_to_truth > 0 else "MLE 更近"
                better_color = '#00D4AA' if delta_to_truth > 0 else '#FF4757'
                st.markdown(
                    f"<div style='background:#1A1D24;border:1px solid {better_color};border-radius:10px;padding:10px 14px;margin-bottom:8px;'>"
                    f"<span style='color:#E4E6EB;font-weight:700;'>#{rank} 极端样本</span> "
                    f"<span style='color:#8B8F98;'>θ={true_theta[i]:+.2f}</span> &nbsp;"
                    f"<span style='color:#8B8F98;'>MLE={X[i]:+.2f}</span> &nbsp;"
                    f"<span style='color:#8B8F98;'>JS={js[i]:+.2f}</span> &nbsp;"
                    f"<span style='float:right;color:{better_color};font-weight:700;'>{better}</span></div>",
                    unsafe_allow_html=True)

            # 可视化2：MSE-维度曲线，扩展到5000维，采用对数横轴
            st.markdown("#### 📈 维度越高，JS 的优势越明显吗？")
            dim_points = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
            dim_points = [x for x in dim_points if x <= max(5000, d)]
            if d > 5000:
                dim_points.append(d)
            rep = 60 if d <= 500 else 40 if d <= 2000 else 25
            mle_curve, js_curve = [], []
            for dd in dim_points:
                mm, jj = [], []
                for _ in range(rep):
                    th = np.random.normal(0, 3, dd)
                    xx = th + np.random.normal(0, 1, dd)
                    mm.append(np.mean((xx - th) ** 2))
                    if dd >= 3:
                        ss = max(0, 1 - (dd - 2) / np.sum(xx ** 2))
                        jj.append(np.mean((ss * xx - th) ** 2))
                    else:
                        jj.append(np.mean((xx - th) ** 2))
                mle_curve.append(np.mean(mm))
                js_curve.append(np.mean(jj))
            fig_curve = go.Figure()
            fig_curve.add_trace(go.Scatter(x=dim_points, y=mle_curve, mode='lines+markers', name='MLE 平均 MSE', line=dict(color='#FF4757', width=2.5), marker=dict(size=7)))
            fig_curve.add_trace(go.Scatter(x=dim_points, y=js_curve, mode='lines+markers', name='JS 平均 MSE', line=dict(color='#9B59B6', width=2.5), marker=dict(size=7)))
            fig_curve.add_vline(x=3, line_dash='dash', line_color='#F0B90B', annotation_text='d=3 分界')
            fig_curve.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color": "#E4E6EB"}, xaxis={"gridcolor": "#2A2D35", "title": "维度 d（对数刻度）", "type": "log"}, yaxis={"gridcolor": "#2A2D35", "title": "平均 MSE"}, height=420, width=540, title={"text": "准确率/误差随维度变化（方形展示）", "font": {"color": "#E4E6EB", "size": 15}})
            st.plotly_chart(fig_curve, use_container_width=False)

            # 可视化3：风险降低百分比榜
            st.markdown("#### 🧾 各维度下的风险降低幅度")
            rows = []
            for dd, mm, jj in zip(dim_points, mle_curve, js_curve):
                drop = (1 - jj / mm) * 100 if mm > 0 else 0
                rows.append((dd, mm, jj, drop))
            rows.sort(key=lambda x: x[0])
            for dd, mm, jj, drop in rows:
                color = '#00D4AA' if drop > 0 else '#FF4757'
                st.markdown(f"<div style='background:#1A1D24;border:1px solid {color};border-radius:10px;padding:10px 14px;margin-bottom:8px;'><span style='color:#E4E6EB;'>d={dd:>4}</span> <span style='color:#8B8F98;margin-left:12px;'>MLE={mm:.4f}</span> <span style='color:#8B8F98;margin-left:12px;'>JS={jj:.4f}</span> <span style='float:right;color:{color};font-weight:700;'>{drop:+.2f}%</span></div>", unsafe_allow_html=True)

            st.markdown("#### ⚠️ 什么时候不该盲目收缩？")
            st.markdown(
                """
                <div style="background:#1A1D24;border:1px solid #FF4757;border-radius:12px;padding:16px;">
                    <span style="color:#FF4757;font-weight:700;">注意：</span>
                    <span style="color:#E4E6EB;">James-Stein 的神奇之处建立在一个前提上——这些参数的真实均值整体确实“围绕某个中心”（这里是 0）分布。<br>
                    如果你把收缩靶心设错了，或者参数根本不该往同一个中心缩，收缩也可能变成有害的偏差。</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if d >= 3 and js_mse < mle_mse:
                if st.button("💡 为什么无关信息反而更准？", key="g13_rev", type="primary", use_container_width=True):
                    st.session_state.g13_phase = "final_reveal"
                    st.rerun()

    if st.session_state.g13_phase == "final_reveal":
        d = st.session_state.g13_d
        mle = st.session_state.g13_mle
        js_mse = st.session_state.g13_js
        reveal_box(
            "偏差换方差——把无关的东西拉在一起反而更准",
            f"d={d} 时，JS 比 MLE 低了 <b>{(1-js_mse/mle)*100:.1f}%</b>。<br>MLE 无偏，但方差大；JS 向 0 收缩，引入一点偏差，却显著降低方差。<br><br><b>MSE = 方差 + 偏差²</b>。当维度够高时，减少的方差远大于引入的偏差。<br>这就是为什么无关信息在高维里也能帮你——它们共同提供了一个“往哪里收缩”的方向。",
            "就像你要同时估计 5000 个人的身高，单独看每个人都会被噪声晃动；但如果你知道“人类身高整体不会离谱到天上去”，把极端值往中间拉一点，反而更准。",
        )
        math_detail(r"""
**MLE**：$$\hat{\theta}^{MLE}_i = X_i$$

**James-Stein 估计量**（当 $$d \ge 3$$）：
$$\hat{\theta}^{JS} = \left(1 - \frac{d-2}{\|X\|^2}\right) X$$

它通过向 0 收缩来降低方差。总风险：
$$\mathrm{MSE} = \mathrm{Bias}^2 + \mathrm{Variance}$$

在高维下，JS 的风险可以严格低于 MLE。
""")
        if st.button("🔄 重新实验", key="g13_again", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("g13_"):
                    del st.session_state[k]
            st.rerun()
        complete_game(13)
        update_radar("估计智慧", 4)

# ═══════════════════════════════════════════════════════════
# 游戏 14: 空心球 (高斯环)
# ═══════════════════════════════════════════════════════════
def show_game_14():
    top_nav(14)
    chapter_banner(14)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#10101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🍉</span><div><h3 style="color:#9B59B6;margin:0 0 8px 0;">空心球</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">你是游戏开发者。2D 地图里，点会自然散落在中心和边缘。<br>但引擎升级到高维后，你发现：<b>点都挤到边界附近，球内部像空心的一样。</b><br>这不是 bug——这是高维空间的反直觉本性。</p></div></div></div>""",unsafe_allow_html=True)

    if "g14_phase" not in st.session_state:
        st.session_state.g14_phase = "low_dim"
    if st.session_state.g14_phase not in ("low_dim", "explore", "final_reveal"):
        st.session_state.g14_phase = "low_dim"

    if st.session_state.g14_phase == "low_dim":
        np.random.seed(42)
        pts_2d = np.random.normal(0, 1, (500, 2))
        dists_2d = np.sqrt(np.sum(pts_2d**2, axis=1))
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=dists_2d, nbinsx=30, marker_color='#00B4D8', opacity=0.7))
        fig.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color":"#E4E6EB"}, xaxis={"gridcolor":"#2A2D35","title":"到原点的距离"}, yaxis={"gridcolor":"#2A2D35"}, height=240, title={"text":"2维世界：点会自然散在整个球里","font":{"color":"#E4E6EB"}})
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"2维下，变异系数约 {np.std(dists_2d)/np.mean(dists_2d)*100:.0f}% —— 距离分布很宽，中心附近有很多点。")
        st.markdown("#### 🤔 如果升到 1000 维，你觉得点会去哪？")
        c1, c2, c3 = st.columns(3)
        if c1.button("还是散在整个球里", key="g14_guess_spread", use_container_width=True):
            st.session_state.g14_guess = "spread"; st.session_state.g14_phase = "explore"; st.rerun()
        if c2.button("会更多集中在中心", key="g14_guess_center", use_container_width=True):
            st.session_state.g14_guess = "center"; st.session_state.g14_phase = "explore"; st.rerun()
        if c3.button("会挤到边界附近", key="g14_guess_shell", use_container_width=True, type="primary"):
            st.session_state.g14_guess = "shell"; st.session_state.g14_phase = "explore"; st.rerun()

    elif st.session_state.g14_phase == "explore":
        d = st.slider("🎚️ 维度 d", 2, 1000, st.session_state.get("g14_d", 50), key="g14_d_slider")
        st.session_state.g14_d = d
        sample_n = st.select_slider("点的数量 n", options=[500, 1000, 2000, 5000, 10000], value=5000, key="g14_n_slider")

        if st.button("🎲 撒点观测", key="g14_go", type="primary"):
            np.random.seed(42)
            points = np.random.normal(0, 1, (sample_n, d))
            distances = np.sqrt(np.sum(points**2, axis=1))
            theo = np.sqrt(d)
            cv = np.std(distances) / np.mean(distances) * 100
            normalized = distances / theo
            inner90 = np.mean(normalized < 0.90) * 100
            shell95 = np.mean(normalized >= 0.95) * 100
            shell98 = np.mean(normalized >= 0.98) * 100
            shell99 = np.mean(normalized >= 0.99) * 100
            sample = points[:min(200, sample_n)]
            nn, ff = [], []
            for i in range(len(sample)):
                dists = np.sqrt(np.sum((sample - sample[i]) ** 2, axis=1))
                dists = np.sort(dists[dists > 0])
                if len(dists) > 0:
                    nn.append(dists[0])
                    ff.append(dists[-1])
            ratio = np.mean(nn) / np.mean(ff)
            st.session_state.g14_results = {
                "d": d,
                "sample_n": sample_n,
                "distances": distances,
                "theo": theo,
                "cv": cv,
                "normalized": normalized,
                "inner90": inner90,
                "shell95": shell95,
                "shell98": shell98,
                "shell99": shell99,
                "ratio": ratio,
            }
            st.rerun()

        results = st.session_state.get("g14_results")
        if results and results.get("d") == d and results.get("sample_n") == sample_n:
            distances = results["distances"]
            theo = results["theo"]
            cv = results["cv"]
            normalized = results["normalized"]
            inner90 = results["inner90"]
            shell95 = results["shell95"]
            shell98 = results["shell98"]
            shell99 = results["shell99"]
            ratio = results["ratio"]

            # 图1：原始距离分布
            st.markdown("### 📊 图1：距离分布开始收缩")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=distances, nbinsx=50, marker_color='#9B59B6', opacity=0.7))
            fig.add_vline(x=theo, line_dash="dash", line_color="#F0B90B", line_width=2, annotation_text=f"√d={theo:.1f}")
            fig.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color":"#E4E6EB"}, xaxis={"gridcolor":"#2A2D35","title":"到原点距离"}, yaxis={"gridcolor":"#2A2D35"}, height=280)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"理论≈√{d}=**{theo:.1f}** | 实际均值=**{np.mean(distances):.2f}** | 变异系数=**{cv:.1f}%**")

            # 图2：归一化壳厚
            fig_norm = go.Figure()
            fig_norm.add_trace(go.Histogram(x=normalized, nbinsx=50, marker_color='#00D4AA', opacity=0.75))
            fig_norm.add_vline(x=1.0, line_dash="dash", line_color="#F0B90B", line_width=2, annotation_text="壳中心=1")
            fig_norm.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color":"#E4E6EB"}, xaxis={"gridcolor":"#2A2D35","title":"归一化距离 |x|/√d"}, yaxis={"gridcolor":"#2A2D35"}, height=280)
            st.plotly_chart(fig_norm, use_container_width=True)
            st.caption("归一化后，若大量点都挤在 1 附近，说明它们都漂浮在半径 √d 的薄壳上。")

            # 图3：壳层占比
            shell_df = pd.DataFrame({
                '区域': ['球心附近 (<0.90√d)', '外层壳 (≥0.95√d)', '更薄壳 (≥0.98√d)', '极薄壳 (≥0.99√d)'],
                '占比': [inner90, shell95, shell98, shell99]
            })
            fig3 = go.Figure(go.Bar(x=shell_df['占比'], y=shell_df['区域'], orientation='h',
                                    marker=dict(color=['#FF4757', '#F0B90B', '#00B4D8', '#9B59B6']),
                                    text=[f"{v:.1f}%" for v in shell_df['占比']], textposition='outside',
                                    textfont=dict(color='#E4E6EB', size=14)))
            fig3.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color":"#E4E6EB"}, xaxis={"gridcolor":"#2A2D35","title":"点的占比(%)", "range": [0, 100]}, yaxis={"gridcolor":"#2A2D35", "autorange":"reversed"}, height=300)
            st.plotly_chart(fig3, use_container_width=True)
            st.caption("这个图比散点图更适合说明‘空心球’：高维里，大多数点根本不在内部，而是挤在外壳。")

            # 图4：最近邻/最远邻
            st.markdown("### 📏 图4：‘附近’这个概念快失效了")
            st.metric("最近邻 / 最远邻 比值", f"{ratio:.3f}")
            if ratio > 0.8:
                st.warning("比值非常接近 1 —— 最近的点和最远的点在高维里几乎一样远。")
            else:
                st.info("比值还没接近 1 —— 低维里‘附近’仍然有意义。")

            # 图5：西瓜皮
            st.markdown("### 🍉 图5：西瓜皮占比")
            dims = [3, 5, 10, 30, 50, 100, 200, 500, 1000]
            skin = [(1 - 0.99**dd) * 100 for dd in dims]
            fig4 = go.Figure(go.Scatter(x=dims, y=skin, mode='lines+markers', line=dict(color='#9B59B6', width=2.5), marker=dict(size=10, color='#F0B90B')))
            fig4.update_layout(plot_bgcolor="#1A1D24", paper_bgcolor="#1A1D24", font={"color":"#E4E6EB"}, xaxis={"gridcolor":"#2A2D35","title":"维度"}, yaxis={"gridcolor":"#2A2D35","title":"皮体积占比(%)"}, height=260)
            st.plotly_chart(fig4, use_container_width=True)
            st.caption(f"d={d} 时，若把‘皮’定义为最外层 1% 半径，则皮大约占 {(1-0.99**d)*100:.1f}% 的体积。")

            if cv < 5 or shell98 > 60:
                if st.button("💡 我明白了——为什么高维球会变空心？", key="g14_rev", type="primary", use_container_width=True):
                    st.session_state.g14_phase = "final_reveal"
                    st.session_state.g14_cv = cv
                    st.session_state.g14_theo = theo
                    st.session_state.g14_ratio = ratio
                    st.session_state.g14_shell98 = shell98
                    st.rerun()
            else:
                st.info("如果你还没看清，可以继续增大维度 d 或样本数量 n。高维直觉建立需要一点耐心。")
    if st.session_state.g14_phase == "final_reveal":
        d = st.session_state.g14_d
        cv = st.session_state.g14_cv
        theo = st.session_state.g14_theo
        ratio = st.session_state.g14_ratio
        shell98 = st.session_state.g14_shell98
        reveal_box(
            "高维空间——球是空的，点几乎全都漂在壳上",
            f"在 d={d} 维时，点到原点的距离几乎都集中在 $$\\sqrt{{d}} \approx {theo:.1f}$$ 附近。<br>"
            f"变异系数只有 <b>{cv:.2f}%</b>，而且有 <b>{shell98:.1f}%</b> 的点已经落在最外层的 98% 壳上。<br><br>"
            f"更诡异的是：最近邻 / 最远邻 比值已经是 <b>{ratio:.3f}</b>，也就是说“附近”这个概念都快失效了。<br><br>"
            f"高维世界不再像你熟悉的球体：它更像一个巨大的、几乎只有外壳的空心结构。",
            "这就是为什么高维直觉总会失灵：你以为点会像 2D 那样散在整个球里，但高维里，‘内部’几乎没体积，所有质量都被挤到边界去了。",
        )
        math_detail(r"""
**高斯环现象**：若 $$X \sim \mathcal{N}(0, I_d)$$，则
$$\|X\| \approx \sqrt{d}$$
且变异系数
$$\frac{\mathrm{sd}(\|X\|)}{\mathbb{E}[\|X\|]} \to 0$$

也就是说维度越高，模长越稳定地集中在半径 $$\sqrt{d}$$ 的薄壳上。

**西瓜皮现象**：若“皮”厚度为半径的 1%，则皮体积占比
$$1 - 0.99^d$$
当 $$d=1000$$ 时，已经接近 100%。
""")
        check_achievement("空心球发现者") if d >= 500 else None
        if st.button("🔄 重新探索", key="g14_again", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("g14_"):
                    del st.session_state[k]
            st.rerun()
        complete_game(14)
        update_radar("维度直觉", 4)

# ═══════════════════════════════════════════════════════════
# 游戏 15: 无法区分的人 (高维线性可分)
# ═══════════════════════════════════════════════════════════
def show_game_15():
    top_nav(15);chapter_banner(15)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#15101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">👥</span><div><h3 style="color:#9B59B6;margin:0 0 8px 0;">无法区分的人</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">两个部落的身高体重<b style="color:#FF4757;">完全混在一起</b>。<br>💬 导师：<i>"加特征。随便什么都可以。"</i><br>每个特征单独看都是垃圾——100个垃圾堆在一起给出了<b style="color:#F0B90B;">99.7%</b>的准确率。</p></div></div></div>""",unsafe_allow_html=True)
    if "g15_base2d" not in st.session_state:
        np.random.seed(99);n=200
        st.session_state.g15_base2d=np.vstack([np.random.normal([-0.5,0],[1,1],(n//2,2)),np.random.normal([0.5,0],[1,1],(n//2,2))])
        st.session_state.g15_labels=np.array([0]*(n//2)+[1]*(n//2));st.session_state.g15_dim=2;st.session_state.g15_noise_cache={};st.session_state.g15_phase="struggle"
    if st.session_state.g15_phase not in ("struggle","explore","reveal"): st.session_state.g15_phase="struggle";st.session_state.g15_dim=2
    base=st.session_state.g15_base2d;labels=st.session_state.g15_labels;d=st.session_state.g15_dim
    if d>2:
        extra=d-2;cache=st.session_state.g15_noise_cache
        if extra not in cache: np.random.seed(extra+200);cache[extra]=np.random.normal(0,1,(len(base),extra))
        data=np.hstack([base,cache[extra]])
    else: data=base
    if st.session_state.g15_phase=="struggle":
        fig=go.Figure()
        for lbl,color,name in[(0,'#FF4757','红土族'),(1,'#00B4D8','蓝水族')]:
            mask=labels==lbl;fig.add_trace(go.Scatter(x=data[mask,0],y=data[mask,1],mode='markers',marker=dict(color=color,size=8,opacity=0.5),name=name))
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"身高"},yaxis={"gridcolor":"#2A2D35","title":"体重"},height=380,title={"text":"你能画一条线分开他们吗？","font":{"color":"#E4E6EB"}})
        st.plotly_chart(fig,use_container_width=True)
        try:
            from sklearn.linear_model import LogisticRegression
            acc=LogisticRegression(max_iter=2000).fit(data,labels).score(data,labels)*100
        except: acc=52
        st.error(f"准确率：**{acc:.1f}%**——几乎瞎猜。")
        if st.button("➕ 加入随机特征试试",key="g15_go",type="primary",use_container_width=True): st.session_state.g15_phase="explore";st.session_state.g15_dim=2;st.rerun()
        if st.button("这两群人就是一个部落吧",key="g15_tribe",use_container_width=True): st.session_state.g15_phase="explore";st.rerun()
    elif st.session_state.g15_phase=="explore":
        st.markdown(f"### 🔬 当前维度：**{d}**")
        col_v,col_s=st.columns([2,1])
        with col_v:
            fig=go.Figure()
            for lbl,color,name in[(0,'#FF4757','红土族'),(1,'#00B4D8','蓝水族')]:
                mask=labels==lbl;fig.add_trace(go.Scatter(x=data[mask,0],y=data[mask,1],mode='markers',marker=dict(color=color,size=7,opacity=0.5),name=name))
            fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"身高"},yaxis={"gridcolor":"#2A2D35","title":"体重"},height=360)
            st.plotly_chart(fig,use_container_width=True)
        with col_s:
            try: acc=LogisticRegression(max_iter=2000).fit(data,labels).score(data,labels)*100
            except: acc=50+40*np.tanh(np.linalg.norm(data[labels==0].mean(0)-data[labels==1].mean(0))/5)
            st.session_state.g15_acc=acc;st.metric("📊 准确率",f"{acc:.1f}%")
            if acc>95: st.success("🚀 近乎完美！")
            elif acc>80: st.info("📈 分离趋势明显")
            else: st.warning("🔍 仍然混在一起")
        c1,c2,c3,c4=st.columns(4)
        if c1.button("➕1维",key="g15_a1",use_container_width=True): st.session_state.g15_dim+=1;st.rerun()
        if c2.button("➕10维",key="g15_a10",use_container_width=True): st.session_state.g15_dim+=10;st.rerun()
        if c3.button("🚀50维",key="g15_a50",use_container_width=True): st.session_state.g15_dim=50;st.rerun()
        if c4.button("🔄重来",key="g15_rst",use_container_width=True): st.session_state.g15_dim=2;st.session_state.g15_noise_cache={};st.session_state.g15_phase="struggle";st.rerun()
        if d>=30:
            if st.button("💡 为什么垃圾特征堆在一起就能分开了？",key="g15_rev",type="primary",use_container_width=True): st.session_state.g15_phase="reveal";st.rerun()
        if st.button("📈 绘制维度曲线",key="g15_curve",type="primary"):
            dims=[2,3,5,10,20,30,50,80,100];accs=[]
            for dd in dims:
                if dd<=d:
                    if dd>2:
                        e=dd-2;c=st.session_state.g15_noise_cache
                        if e not in c: np.random.seed(e+200);c[e]=np.random.normal(0,1,(len(base),e))
                        dt=np.hstack([base,c[e]])
                    else: dt=base
                    try: accs.append(LogisticRegression(max_iter=2000).fit(dt,labels).score(dt,labels)*100)
                    except: accs.append(50)
            fig3=go.Figure();fig3.add_trace(go.Scatter(x=dims[:len(accs)],y=accs,mode='lines+markers',line=dict(color='#9B59B6',width=3),marker=dict(size=10,color='#F0B90B')));fig3.add_hline(y=50,line_dash="dot",line_color="#FF4757")
            fig3.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"维度"},yaxis={"gridcolor":"#2A2D35","title":"准确率(%)","range":[40,105]},height=420,width=500)
            st.plotly_chart(fig3,use_container_width=False)
    if st.session_state.g15_phase=="reveal":
        reveal_box("不是算法变聪明了——是空间变大了",f"你加了{d-2}个'垃圾特征'——每个区分力≈50%。<br>但{d}个垃圾堆在一起——准确率<b>{st.session_state.g15_acc:.1f}%</b>。<br>高维空间中<b>任意两组随机点几乎一定线性可分</b>。<br>你每天刷脸、搜索、AI——都在偷这个性质。","你可能觉得两个人'本质上很像'——只是因为你站在低维里看。加足够多的角度，他们千差万别。",f"高维线性可分。{d}维准确率{st.session_state.g15_acc:.1f}%。",15)
        math_detail("**Cover定理** $$N$$个点在$$d$$维空间中随机超平面线性可分的概率随$$d$$增大。当$$d>N$$时几乎一定可分。")
        if st.button("🔄 重新体验",key="g15_again",use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("g15_"): del st.session_state[k]
            st.rerun()
        complete_game(15);update_radar("维度直觉",4)

# ═══════════════════════════════════════════════════════════
# AI 分析讲解
# ═══════════════════════════════════════════════════════════
def show_ai_analysis():
    st.markdown("""<h1 style="font-size:36px;color:#E4E6EB;">🤖 AI 分析讲解</h1><p style="color:#8B8F98;font-size:14px;">选择游戏，配置提示词，自由提问——AI 导师为你深度解析概率与统计概念</p>""", unsafe_allow_html=True)
    st.markdown("---")

    client = get_ai_client()

    # ── 左侧：游戏选择 + 提示词配置 ──
    col_cfg, col_chat = st.columns([1, 2])

    with col_cfg:
        st.subheader("⚙️ 配置")

        # 游戏选择
        game_options = {"lobby": "🏠 大厅（通用）"}
        for gid in range(1, 16):
            m = GAME_META[gid]
            done = "✅" if str(gid) in st.session_state.games_completed else "⬜"
            game_options[str(gid)] = f"{done} {m['icon']} 游戏{gid}·{m['title']}"

        selected_game = st.selectbox(
            "🎮 选择分析的游戏",
            options=list(game_options.keys()),
            format_func=lambda x: game_options[x],
            key="ai_game"
        )

        if selected_game != st.session_state.get("_ai_current_game"):
            st.session_state._ai_current_game = selected_game
            # 切换游戏时不清空历史，但更新系统提示词

        # 系统提示词编辑
        default_prompt = AI_SYSTEM_PROMPTS.get(
            selected_game if selected_game == "lobby" else int(selected_game),
            AI_SYSTEM_PROMPTS["lobby"]
        )
        if "_ai_custom_prompt" not in st.session_state:
            st.session_state._ai_custom_prompt = {}

        # 如果切换了游戏且没有自定义过该游戏的提示词，使用默认
        gk = selected_game
        if gk not in st.session_state._ai_custom_prompt:
            st.session_state._ai_custom_prompt[gk] = default_prompt

        system_prompt = st.text_area(
            "🔧 系统提示词（可编辑）",
            value=st.session_state._ai_custom_prompt[gk],
            height=200,
            key="ai_sys_prompt",
            on_change=lambda: st.session_state._ai_custom_prompt.update(
                {gk: st.session_state.ai_sys_prompt}
            )
        )
        # 同步
        st.session_state._ai_custom_prompt[gk] = system_prompt

        # 快捷提问
        st.subheader("⚡ 快捷提问")
        quick_questions = {
            "lobby": [
                "💡 我应该从哪个游戏开始？",
                "🎯 概率直觉到底是什么？",
                "📊 4个章节分别训练什么能力？",
            ],
            "1": ["🎮 为什么69次就有50%概率出SSR？", "🧠 「垫刀」为什么是错觉？", "📐 什么是无记忆性？"],
            "2": ["🚪 为什么换门概率是2/3不是1/2？", "🔑 主持人的行为为什么重要？", "🔄 这和贝叶斯定理什么关系？"],
            "3": ["🎂 为什么23人就够？", "🔗 组合数C(N,2)是什么意思？", "🏢 这和密码碰撞攻击有什么关系？"],
            "4": ["💸 为什么期望+5%还会破产？", "📉 几何均值为什么小于1？", "🌌 什么是非各态历经性？"],
            "5": ["📉 什么是回归均值？", "⚽ 怎么判断是真天才还是运气？", "🎯 如何避免被极端值欺骗？"],
            "6": ["🏥 辛普森悖论的本质是什么？", "📊 什么时候应该分组看数据？", "⚠️ 分组变量怎么选才合理？"],
            "7": ["💀 幸存者偏差骗了多少人？", "📭 怎么看到沉默的数据？", "💰 还有哪些常见的幸存者偏差？"],
            "8": ["🩺 为什么99%准确率≠99%患病？", "🧮 贝叶斯定理怎么算？", "🦠 基础率为什么这么重要？"],
            "9": ["📁 怎么判断两条曲线是不是巧合？", "🕵️ 数据挖掘偏差怎么避免？", "❌ 相关和因果的本质区别是什么？"],
            "10": ["🐔 怎么判断因果方向？", "⏱️ 时间顺序为什么是关键？", "🔄 有哪些经典的反向因果案例？"],
            "11": ["🕵️ 怎么找到遗漏变量？", "📊 DAG图怎么画？", "☕ 还有哪些遗漏变量的经典例子？"],
            "12": ["🌟 对撞偏差是什么意思？", "📉 为什么筛选后会出伪相关？", "🎬 生活中还有哪些对撞偏差？"],
            "13": ["🪄 为什么收缩反而更准？", "📐 偏差-方差权衡是什么？", "📈 d≥3这个界限为什么重要？"],
            "14": ["🍉 高维球为什么是空的？", "🌌 维度诅咒还有哪些表现？", "📏 为什么高维里所有距离都相等？"],
            "15": ["👥 为什么垃圾特征能分开人群？", "📐 Cover定理是什么？", "🤖 这和机器学习有什么关系？"],
        }
        qs = quick_questions.get(selected_game, quick_questions["lobby"])
        for q in qs:
            if st.button(q, key=f"ai_qq_{q[:20]}", use_container_width=True):
                st.session_state._ai_pending_question = q
                st.rerun()

    # ── 右侧：聊天区 ──
    with col_chat:
        st.subheader("💬 对话")

        if not client:
            st.warning("⚠️ 请先在 `.env` 文件中配置 `DEEPSEEK_API_KEY`，然后重启应用。")
            st.code("DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx\nDEEPSEEK_BASE_URL=https://api.deepseek.com", language="bash")
        else:
            # 初始化聊天历史
            if "_ai_messages" not in st.session_state:
                gid = selected_game if selected_game == "lobby" else int(selected_game)
                meta = GAME_META.get(gid, {"title": "大厅", "icon": "🏠"})
                welcome_msg = f"你好！我是 **AI 概率导师「以为解药」** 🧪\n\n当前分析目标：**{meta.get('icon','🏠')} {meta.get('title','大厅')}**\n\n你可以自由提问关于概率、统计、因果推断的任何问题。我会用生动的类比和严谨的数学帮助你建立直觉。\n\n试试下方的快捷提问，或者直接输入你的问题 👇"
                st.session_state._ai_messages = [{"role": "assistant", "content": welcome_msg}]

            # 渲染历史消息
            for msg in st.session_state._ai_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # 处理快捷提问
            if "_ai_pending_question" in st.session_state and st.session_state._ai_pending_question:
                prompt = st.session_state._ai_pending_question
                st.session_state._ai_pending_question = None
            else:
                prompt = st.chat_input("输入你的问题…", key="ai_chat_input")

            if prompt:
                # 添加用户消息
                st.session_state._ai_messages.append({"role": "user", "content": prompt})

                # 构建消息列表
                gk = st.session_state._ai_current_game
                sys_prompt = st.session_state._ai_custom_prompt.get(gk, AI_SYSTEM_PROMPTS.get("lobby", ""))

                messages = [{"role": "system", "content": sys_prompt}]
                messages.extend(st.session_state._ai_messages)

                # 调用 API
                with st.spinner("🤔 以为解药思考中…"):
                    try:
                        response = client.chat.completions.create(
                            model=AI_MODEL,
                            messages=messages,
                            temperature=0.7,
                            max_tokens=1024,
                        )
                        reply = response.choices[0].message.content
                        st.session_state._ai_messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"❌ API 调用失败：{str(e)}")
                st.rerun()

            # 操作按钮
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🗑️ 清空对话", use_container_width=True):
                    st.session_state._ai_messages = []
                    st.rerun()
            with c2:
                if st.button("🔄 重置提示词", use_container_width=True):
                    gk = st.session_state._ai_current_game
                    default = AI_SYSTEM_PROMPTS.get(
                        gk if gk == "lobby" else int(gk),
                        AI_SYSTEM_PROMPTS["lobby"]
                    )
                    st.session_state._ai_custom_prompt[gk] = default
                    st.rerun()

# ═══════════════════════════════════════════════════════════
# MAIN + ROUTER
# ═══════════════════════════════════════════════════════════
GAME_ROUTER={"lobby":show_lobby,"1":show_game_01,"2":show_game_02,"3":show_game_03,"4":show_game_04,"5":show_game_05,"6":show_game_06,"7":show_game_07,"8":show_game_08,"9":show_game_09,"10":show_game_10,"11":show_game_11,"12":show_game_12,"13":show_game_13,"14":show_game_14,"15":show_game_15,"ai":show_ai_analysis}

def main():
    with st.sidebar:
        logo=ASSETS/"logo.png"
        if logo.exists(): st.image(str(logo),width=200)
        st.markdown("""<h2 style="text-align:center;color:#E4E6EB;">你<span style="color:#F0B90B;">以为</span>的以为</h2><p style="text-align:center;color:#8B8F98;font-size:12px;">概率直觉训练营</p>""",unsafe_allow_html=True)
        st.markdown("---")
        c1,c2=st.columns(2);c1.metric("💰 金币",st.session_state.coins);c2.metric("🏆 成就",f"{len(st.session_state.achievements)}/16")
        st.markdown("---")
        if st.button("🏠 大厅",use_container_width=True): st.session_state.current_game="lobby";st.rerun()
        for ch_label,ch_key,games in [("🏕️ 第一章","chapter1",range(1,5)),("🏥 第二章","chapter2",range(5,9)),("🔎 第三章","chapter3",range(9,13)),("🌌 第四章","chapter4",range(13,16))]:
            with st.expander(f"{ch_label}",expanded=st.session_state.current_game in [str(g) for g in games]):
                for g in games:
                    done=str(g) in st.session_state.games_completed;prefix="✅" if done else "⬜"
                    meta=GAME_META[g]
                    if st.button(f"{prefix} {meta['icon']} {meta['title']}",key=f"nav_{g}",use_container_width=True): st.session_state.current_game=str(g);st.rerun()
        st.markdown("---")
        st.subheader("🤖 AI 分析讲解")
        if st.button("🧪 进入 AI 分析", use_container_width=True, type="primary" if st.session_state.get("current_game") == "ai" else "secondary"):
            st.session_state.current_game = "ai"
            # 清除 AI 对话历史以刷新
            if "_ai_messages" in st.session_state:
                del st.session_state._ai_messages
            st.rerun()
        st.markdown("---");st.caption("《程序设计与科学计算》期末")
    cur=st.session_state.get("current_game","lobby")
    if cur in GAME_ROUTER: GAME_ROUTER[cur]()
    else: show_lobby()

if __name__=="__main__": main()