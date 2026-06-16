"""
你以为的以为 — 概率直觉训练营
"""
import streamlit as st, pandas as pd, numpy as np, plotly.graph_objects as go
from pathlib import Path
import random, time, re

st.set_page_config(page_title="你以为的以为",page_icon="🤔",layout="wide",initial_sidebar_state="expanded")
ROOT=Path(__file__).resolve().parent; ASSETS=ROOT/"assets"; DATA_DIR=ROOT/"data"

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
    top_nav(5);chapter_banner(5)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#101a1a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">⚽</span><div><h3 style="color:#00B4D8;margin:0 0 8px 0;">天才的诅咒</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">你是俱乐部的<b>首席球探</b>。第一赛季冒出了一堆"天才"。<br>但进球=<b>真实天赋+随机运气</b>。你能从50个球员里挑出真天才吗？</p></div></div></div>""",unsafe_allow_html=True)
    if "g05_true" not in st.session_state:
        np.random.seed(int(time.time()));n=50
        true_skill=np.random.normal(75,10,n);luck_s1=np.random.normal(0,8,n)
        st.session_state.g05_true=true_skill;st.session_state.g05_s1=true_skill+luck_s1
        st.session_state.g05_s2=None;st.session_state.g05_picks=[];st.session_state.g05_phase="stage1"
    if st.session_state.g05_phase not in ("stage1","stage2","stage3"): st.session_state.g05_phase="stage1"
    if st.session_state.g05_phase=="stage1":
        st.markdown("### 🏆 第一赛季排行榜")
        s1=st.session_state.g05_s1;rankings=sorted(enumerate(s1),key=lambda x:x[1],reverse=True)
        top10=rankings[:10];names=[f"🥇 #{idx+1:02d}" if i==0 else f"🥈 #{idx+1:02d}" if i==1 else f"🥉 #{idx+1:02d}" if i==2 else f"  #{idx+1:02d}" for i,(idx,_) in enumerate(top10)]
        fig=go.Figure(go.Bar(x=[g for _,g in top10],y=names,orientation='h',marker=dict(color=['#F0B90B' if i<3 else '#00B4D8'if i<5 else'#4A90D9' for i in range(10)]),text=[f"{g:.0f}球" for g in[_[1] for _ in top10]],textposition='outside',textfont=dict(color='#E4E6EB',size=14)))
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"进球数","range":[0,max([_[1] for _ in top10])+15]},yaxis={"gridcolor":"#2A2D35","autorange":"reversed","tickfont":{"size":13}},height=320,margin=dict(l=20,r=50,t=10,b=20))
        st.plotly_chart(fig,use_container_width=True)
        st.caption("💡 前几名看起来都是'天才'——但进球=真实天赋+随机运气。运气下赛季就消失了。")
        if st.button("▶ 去选出真天才",key="g05_go",type="primary",use_container_width=True): st.session_state.g05_phase="stage2";st.rerun()
    elif st.session_state.g05_phase=="stage2":
        st.markdown("### 🎯 选出真实天赋≥85的球员")
        s1=st.session_state.g05_s1;pick_input=st.text_input("🎯 输入球员编号(1~50)，逗号分隔：",value=", ".join(str(p+1) for p in st.session_state.g05_picks) if st.session_state.g05_picks else "",placeholder="例如: 1, 5, 12, 23, 44")
        picks=[]
        if pick_input.strip():
            for n_str in re.findall(r'\d+',pick_input):
                n=int(n_str)
                if 1<=n<=50 and (n-1) not in picks: picks.append(n-1)
        st.session_state.g05_picks=picks
        if picks: st.markdown(f"<span style='color:#F0B90B;font-weight:600;'>✅ 已选 {len(picks)} 人</span>",unsafe_allow_html=True)
        else: st.info("👆 输入球员编号")
        if st.button("✅ 揭晓第二赛季！",key="g05_reveal",type="primary",use_container_width=True):
            st.session_state.g05_s2=st.session_state.g05_true+np.random.normal(0,8,50);st.session_state.g05_phase="stage3";st.rerun()
    elif st.session_state.g05_phase=="stage3":
        true=st.session_state.g05_true;s1=st.session_state.g05_s1;s2=st.session_state.g05_s2;picks=st.session_state.g05_picks
        rankings_s1=sorted(enumerate(s1),key=lambda x:x[1],reverse=True);rankings_s2=sorted(enumerate(s2),key=lambda x:x[1],reverse=True)
        top10_s2=set(idx for idx,_ in rankings_s2[:10])
        st.markdown("#### 📋 Top10第二赛季表现")
        table="| 排名 | 球员 | S1 | S2 | 变化 | 真实 | 还在Top10? |\n|------|------|----|----|------|-----|------------|\n"
        for rank,(idx,goals) in enumerate(rankings_s1[:10],1):
            diff=s2[idx]-s1[idx];emoji="📉" if diff<-3 else "📈" if diff>3 else "➡️"
            table+=f"|{rank}|#{idx+1:02d}|{s1[idx]:.0f}|{s2[idx]:.0f}|{emoji}{diff:+.0f}|{true[idx]:.0f}|{'✅' if idx in top10_s2 else '❌跌出'}|\n"
        st.markdown(table)
        if picks:
            correct=sum(1 for i in picks if true[i]>=85);hit_rate=correct/len(picks)*100
            st.success(f"🎯 命中率 {hit_rate:.0f}% ({correct}/{len(picks)})") if hit_rate>=50 else st.error(f"😬 命中率 {hit_rate:.0f}%")
        # 散点图
        top5=[idx for idx,_ in rankings_s1[:5]]
        fig=go.Figure()
        colors=['#F0B90B' if i in top5 else '#FF4757' if i in picks else '#00B4D8' for i in range(50)]
        sizes=[14 if i in top5 else 10 if i in picks else 6 for i in range(50)]
        fig.add_trace(go.Scatter(x=s1,y=s2,mode='markers+text',marker=dict(color=colors,size=sizes),text=[f"#{i+1:02d}" for i in range(50)],textposition='top center',textfont=dict(size=8,color='#8B8F98'),customdata=true,hovertemplate='<b>#%{text}</b><br>S1:%{x:.0f}<br>S2:%{y:.0f}<br>真实:%{customdata:.0f}'))
        z=np.polyfit(s1,s2,1);x_line=np.linspace(min(s1)-3,max(s1)+3,50)
        fig.add_trace(go.Scatter(x=x_line,y=np.polyval(z,x_line),mode='lines',line=dict(color='#F0B90B',width=2.5,dash='dash'),name='回归线'))
        fig.add_hline(y=np.mean(true),line_dash="dot",line_color="#8B8F98",annotation_text=f"真实均值{np.mean(true):.0f}")
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"第一赛季"},yaxis={"gridcolor":"#2A2D35","title":"第二赛季"},height=400)
        st.plotly_chart(fig,use_container_width=True)
        # 多赛季模拟
        st.markdown("#### 🔁 多赛季模拟")
        n_extra=st.slider("额外赛季数",3,20,5,key="g05_extra")
        if st.button("🔁 运行",key="g05_multi",type="primary"):
            s1_top10=[idx for idx,_ in rankings_s1[:10]];counts={idx:0 for idx in range(50)}
            for _ in range(n_extra):
                for idx,_ in sorted(enumerate(true+np.random.normal(0,8,50)),key=lambda x:x[1],reverse=True)[:10]: counts[idx]+=1
            data=[(idx,counts[idx]) for idx in s1_top10];names=[f"#{idx+1:02d}" for idx,_ in data];cs=[c for _,c in data]
            fig2=go.Figure(go.Bar(x=cs,y=names,orientation='h',marker=dict(color=['#00D4AA' if c>=n_extra/2 else '#F0B90B' if c>=1 else '#FF4757' for c in cs]),text=[f"{c}/{n_extra}季" for c in cs],textposition='outside',textfont=dict(color='#E4E6EB')))
            fig2.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":f"后续{n_extra}季进入Top10次数"},yaxis={"gridcolor":"#2A2D35","autorange":"reversed"},height=260)
            st.plotly_chart(fig2,use_container_width=True)
        reveal_box("极值=信号+噪声。噪声下次消失，极值自然回弹。",f"你选了{len(picks)}人，命中<b>{correct if picks else 0}</b>个真天才。<br>第一赛季30球=<b>真实能力(~20球)+运气(~+10球)</b>。<br>这就是<b>回归均值</b>——新秀墙、二年级魔咒都只是穿了马甲。","考了第一下次退步？回归均值。惩罚了调皮学生他变乖？可能只是回归均值。",f"50名球员，选了{len(picks)}人，命中{correct if picks else 0}个。Top5全部回落。",5)
        math_detail("**模型** $$X_i=\\theta_i+\\varepsilon_i$$ $$E[\\theta\\mid X_1=x_1]=\\mu+\\frac{\\sigma_\\theta^2}{\\sigma_\\theta^2+\\sigma_\\varepsilon^2}(x_1-\\mu)$$ 收缩因子<1。")
        if st.button("🔄 换一批球员",key="g05_new",use_container_width=True,type="primary"):
            for k in list(st.session_state.keys()):
                if k.startswith("g05_"): del st.session_state[k]
            st.rerun()
        complete_game(5);update_radar("大数感觉",4)

# ═══════════════════════════════════════════════════════════
# 游戏 6: 两个神医 (辛普森悖论)
# ═══════════════════════════════════════════════════════════
def show_game_06():
    top_nav(6);chapter_banner(6)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#101a18 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🏥</span><div><h3 style="color:#00B4D8;margin:0 0 8px 0;">两个神医</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">华大夫广告：<b style="color:#F0B90B;">'治愈率83%！全镇第一！'</b><br>张大夫诊所：<b>'治愈率78%。'</b> 门可罗雀。<br>📱 匿名消息：<i>"先看分组数据再决定。"</i></p></div></div></div>""",unsafe_allow_html=True)
    if "g06_revealed" not in st.session_state: st.session_state.g06_revealed=False;st.session_state.g06_choice=None
    fig=go.Figure(data=[go.Bar(name="华大夫",x=["总体"],y=[83],marker_color='#F0B90B',text="83%",textposition='outside',textfont=dict(color='#F0B90B',size=20)),go.Bar(name="张大夫",x=["总体"],y=[78],marker_color='#00B4D8',text="78%",textposition='outside',textfont=dict(color='#00B4D8',size=20))])
    fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35"},yaxis={"gridcolor":"#2A2D35","range":[0,100],"title":"治愈率(%)"},height=280,barmode='group')
    st.plotly_chart(fig,use_container_width=True)
    if not st.session_state.g06_revealed:
        c1,c2,c3=st.columns(3)
        if c1.button("🏆 选华大夫(83%)",key="g06_hua",use_container_width=True,type="primary"): st.session_state.g06_choice="hua";st.session_state.g06_revealed=True;st.rerun()
        if c2.button("🤔 先看分组数据",key="g06_check",use_container_width=True): st.session_state.g06_choice="check";st.session_state.g06_revealed=True;st.rerun()
        if c3.button("🏥 选张大夫(78%)",key="g06_zhang",use_container_width=True): st.session_state.g06_choice="zhang";st.session_state.g06_revealed=True;st.rerun()
    if st.session_state.g06_revealed:
        st.markdown("---");st.markdown("### 🔬 分病种对比")
        fig2=go.Figure(data=[go.Bar(name="华大夫",x=["🤧轻症","🏥重症"],y=[90,55],marker_color='#F0B90B',text=["90%","55%"],textposition='outside',textfont=dict(color='#F0B90B')),go.Bar(name="张大夫",x=["🤧轻症","🏥重症"],y=[95,61],marker_color='#00B4D8',text=["95%✅","61%✅"],textposition='outside',textfont=dict(color='#00D4AA'))])
        fig2.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35"},yaxis={"gridcolor":"#2A2D35","range":[0,110],"title":"治愈率(%)"},height=300,barmode='group')
        st.plotly_chart(fig2,use_container_width=True)
        st.error("**每种病分开比，张大夫都赢了。但总体华大夫更高。**")
        lr=st.slider("🎚️ 华大夫轻症占比",0.1,0.95,0.8,0.05)
        hua=lr*90+(1-lr)*55;zhang=0.2*95+0.8*61
        st.markdown(f"华大夫总体: **{hua:.1f}%** | 张大夫: **{zhang:.1f}%**")
        reveal_box("你选了华大夫——但每一种病，张大夫都治得更好",f"华大夫总体83% vs 张大夫78%。但<b>每一种病</b>张>华。<br>华大夫只是收了更多轻症(80%)——总体被轻症的高治愈率拉高了。<br>这就是<b>辛普森悖论</b>。","大学录取'歧视女性'？可能只是女性更爱申请竞争激烈的专业。看总体结论前，先问：分组数据是什么样的？",f"辛普森悖论。华总83%张总78%，但每种病张>华。",6)
        math_detail("华总$$=0.8\\times90\\%+0.2\\times55\\%=83\\%$$ 张总$$=0.2\\times95\\%+0.8\\times61\\%=78\\%$$ 组样本不均衡时总体趋势可完全反转。")
        if st.button("🔄 重新选择",key="g06_retry",use_container_width=True): st.session_state.g06_revealed=False;st.session_state.g06_choice=None;st.rerun()
        complete_game(6);update_radar("混淆嗅觉",4)

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
    top_nav(8);chapter_banner(8)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#1a1015 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🩺</span><div><h3 style="color:#00B4D8;margin:0 0 8px 0;">阳性</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">罕见病发病率<b style="color:#FF4757;">0.1%</b>。检测准确率<b>99%</b>。<br>报告：<b style="font-size:20px;color:#FF4757;">阳性</b><br>💓 你心跳加速——99%准确率啊……</p></div></div></div>""",unsafe_allow_html=True)
    prevalence=st.slider("🦠 发病率",0.01,10.0,0.1,0.01,format="%.2f%%")/100
    accuracy=st.slider("🔬 准确率",80.0,99.9,99.0,0.1,format="%.1f%%")/100
    n=1000;ns=max(1,int(n*prevalence));nh=n-ns;fp=int(nh*(1-accuracy));tp_pos=ns+fp;ppv=ns/tp_pos*100 if tp_pos>0 else 0
    st.markdown("### 📊 1000人筛查结果")
    grid='<div style="font-size:7px;line-height:1.1;font-family:monospace;">'
    for i in range(20):
        for j in range(50):
            idx=i*50+j
            if idx<ns: grid+="🟥"
            elif idx<ns+fp: grid+="🩷"
            else: grid+="⬛"
        grid+="<br>"
    grid+='</div>';st.markdown(grid,unsafe_allow_html=True)
    c1,c2,c3=st.columns(3);c1.metric("🟥 真阳性",f"{ns}人");c2.metric("🩷 假阳性",f"{fp}人");c3.metric("❗ PPV",f"{ppv:.1f}%")
    report_color="#FF4757" if ppv<30 else "#F0B90B" if ppv<70 else "#00D4AA"
    st.markdown(f"""<div style="background:#1A1D24;border:2px solid {report_color};border-radius:16px;padding:24px;max-width:500px;margin:16px auto;text-align:center;"><span style="font-size:12px;color:#8B8F98;">医学检测报告</span><hr style="border-color:#2A2D35;margin:8px 0;"><span style="font-size:32px;font-weight:800;color:{report_color};">阳性</span><br><span style="font-size:11px;color:#8B8F98;">实际患病概率</span><br><span style="font-size:28px;font-weight:800;color:{report_color};">{ppv:.1f}%</span></div>""",unsafe_allow_html=True)
    reveal_box("你被99%震撼了——忘了问：这个病本身有多常见？",f"PPV仅<b>{ppv:.1f}%</b>。<br>1000人中只有<b>{ns}</b>个真病人——但检测产生约<b>{fp}</b>个假阳性。<br><b>先问基础概率，再看条件概率。</b>这就是贝叶斯定理的全部。","'这个策略90%准确率'——但90%的策略都亏钱？'测谎通过了'——但对诚实人的误报率有多高？先问基础概率。",f"发病率{prevalence*100:.1f}%，准确率{accuracy*100:.1f}%，PPV={ppv:.1f}%。",8)
    math_detail("**贝叶斯定理** $$P(D\\mid+)=\\frac{P(+\\mid D)P(D)}{P(+\\mid D)P(D)+P(+\\mid\\neg D)P(\\neg D)}$$ 发病率0.1%准确率99%→PPV≈9%。")
    complete_game(8);update_radar("贝叶斯脑",4 if ppv<50 else 2);st.button("🔄 调整重试",key="g08_retry",use_container_width=True,type="primary")

# ═══════════════════════════════════════════════════════════
# 游戏 9: 离奇档案 (虚假相关)
# ═══════════════════════════════════════════════════════════
def show_game_09():
    top_nav(9);chapter_banner(9)
    try: df=pd.read_csv(DATA_DIR/"spurious_correlations.csv")
    except: st.error("数据文件未找到");return
    if "g09_idx" not in st.session_state: st.session_state.g09_idx=0;st.session_state.g09_answers=[];st.session_state.g09_revealed=False
    idx=st.session_state.g09_idx%len(df);row=df.iloc[idx]
    st.markdown(f"#### 📋 档案 #{idx+1}/{len(df)}：{row['title']}")
    np.random.seed(idx+42);years=list(range(2000,2020))
    tx=np.cumsum(np.random.normal(0.5,0.3,len(years)));ty=tx*0.85+np.random.normal(0,0.15,len(years));r=np.corrcoef(tx,ty)[0,1]
    fig=go.Figure()
    fig.add_trace(go.Scatter(y=tx,mode='lines+markers',name=row['var_x'],line=dict(color='#00B4D8',width=2),yaxis='y1'))
    fig.add_trace(go.Scatter(y=ty,mode='lines+markers',name=row['var_y'],line=dict(color='#E07B39',width=2),yaxis='y2'))
    fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"年份"},yaxis=dict(title=row['var_x'],side='left',color='#00B4D8',gridcolor='#2A2D35'),yaxis2=dict(title=row['var_y'],side='right',overlaying='y',color='#E07B39',gridcolor='#2A2D35'),height=300,legend=dict(x=0.01,y=0.99))
    st.plotly_chart(fig,use_container_width=True);st.caption(f"r = {r:.3f}")
    if not st.session_state.g09_revealed:
        c1,c2,c3,c4=st.columns(4)
        if c1.button(f"{row['var_x']}→{row['var_y']}",key="g09_a",use_container_width=True): st.session_state.g09_answers.append("AB");st.session_state.g09_revealed=True;st.rerun()
        if c2.button(f"{row['var_y']}→{row['var_x']}",key="g09_b",use_container_width=True): st.session_state.g09_answers.append("BA");st.session_state.g09_revealed=True;st.rerun()
        if c3.button("巧合·隐藏变量",key="g09_c",use_container_width=True): st.session_state.g09_answers.append("hidden");st.session_state.g09_revealed=True;st.rerun()
        if c4.button("不确定",key="g09_d",use_container_width=True): st.session_state.g09_answers.append("?");st.session_state.g09_revealed=True;st.rerun()
    else:
        ans=st.session_state.g09_answers[-1];correct=(ans=="hidden")
        st.success(f"✅ 正确！隐藏变量'{row['hidden_variable']}'") if correct else st.error(f"❌ 答案是：{row['hidden_variable']}")
        st.info(row['explanation'])
        reveal_box("两条线一起动≠一个导致另一个",f"r={r:.3f}——高得吓人。但<b>相关≠因果</b>。<br><b>{row['var_x']}</b>和<b>{row['var_y']}</b>都受<b>{row['hidden_variable']}</b>驱动。","股市涨了因为超级碗AFC赢了？每当你看到两个趋势一致就联想到因果——先问：有第三个东西在同时推动它们吗？",f"档案{idx+1}:{row['title']},r={r:.3f},隐藏变量={row['hidden_variable']}。",9)
        math_detail("**虚假相关** $$\\text{Corr}(X,Y)>0.9$$但$$X\\not\\rightarrow Y$$ 因果结构：$$X\\leftarrow Z\\rightarrow Y$$ 相关是对称的，因果不是。")
        cc=st.columns(2)
        if cc[0].button("▶ 下一份",key="g09_next",use_container_width=True): st.session_state.g09_idx+=1;st.session_state.g09_revealed=False;st.rerun()
        if cc[1].button("🔄 重置",key="g09_reset",use_container_width=True): st.session_state.g09_idx=0;st.session_state.g09_answers=[];st.session_state.g09_revealed=False;st.rerun()
        complete_game(9);update_radar("因果链条",sum(1 for a in st.session_state.g09_answers if a=="hidden"))

# ═══════════════════════════════════════════════════════════
# 游戏 10: 鸡与蛋 (因果倒置)
# ═══════════════════════════════════════════════════════════
def show_game_10():
    top_nav(10);chapter_banner(10)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#15101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🐔</span><div><h3 style="color:#E07B39;margin:0 0 8px 0;">鸡与蛋</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">三个委托人，三个"确凿的发现"。<br>你的任务：找出谁的因果箭头搞反了。</p></div></div></div>""",unsafe_allow_html=True)
    cases={"A":{"client":"👓 眼镜公司老板","data":"戴眼镜的人智商高8分。p<0.001。","claim":"推广眼镜→下一代都变聪明","truth":"智商高→学习多→容易近视→需要眼镜。不是眼镜让人聪明。"},"B":{"client":"🚒 消防局长","data":"消防员越多，火灾损失越大。","claim":"减少消防员→降低损失","truth":"大火→更多消防员。不是消防员导致损失大。"},"C":{"client":"🏥 医院院长","data":"住院越久，死亡率越高。","claim":"早点出院→减少死亡","truth":"重症→住院久→死亡率高。不是住院害死人。"}}
    if "g10_answers" not in st.session_state: st.session_state.g10_answers={};st.session_state.g10_current="A"
    ck=st.session_state.g10_current
    if ck=="done":
        correct=sum(1 for a in st.session_state.g10_answers.values() if a=="correct");st.success(f"🎉 完成！正确{correct}/3")
        reveal_box("三个委托人全都搞反了因果方向","横截面数据中'A导致B'和'B导致A'在统计上完全一样。<br>只有<b>时间先后</b>或实验干预能告诉我们箭头方向。","喝红酒的人更健康→还是健康的人更有钱喝红酒？下次听到X导致Y——先问：有没有可能是Y导致X？",f"三个委托正确{correct}/3。",10)
        math_detail("横截面数据中$$X$$和$$Y$$的关联无法区分因果方向。$$P(Y\\mid X)\\neq P(Y\\mid do(X))$$——观察≠干预。")
        if st.button("🔄 重新处理",key="g10_retry",use_container_width=True): st.session_state.g10_answers={};st.session_state.g10_current="A";st.rerun()
        complete_game(10);update_radar("因果链条",4 if correct>=2 else 2);return
    case=cases[ck];st.markdown(f"### 📋 委托{ck}：{case['client']}");st.markdown(f"📊 {case['data']}");st.markdown(f"💬 *\"{case['claim']}\"*")
    cc=st.columns(4)
    if cc[0].button("A→B",key=f"g10_{ck}_ab",use_container_width=True): st.session_state.g10_answers[ck]="wrong";st.session_state.g10_current=chr(ord(ck)+1) if ck<"C" else "done";st.rerun()
    if cc[1].button("B→A",key=f"g10_{ck}_ba",use_container_width=True): st.session_state.g10_answers[ck]="correct";st.session_state.g10_current=chr(ord(ck)+1) if ck<"C" else "done";st.rerun()
    if cc[2].button("🔄双向",key=f"g10_{ck}_both",use_container_width=True): st.session_state.g10_answers[ck]="wrong";st.session_state.g10_current=chr(ord(ck)+1) if ck<"C" else "done";st.rerun()
    if cc[3].button("❌无关",key=f"g10_{ck}_none",use_container_width=True): st.session_state.g10_answers[ck]="wrong";st.session_state.g10_current=chr(ord(ck)+1) if ck<"C" else "done";st.rerun()
    if ck in st.session_state.g10_answers: st.success(f"✅ {case['truth']}") if st.session_state.g10_answers[ck]=="correct" else st.error(f"❌ {case['truth']}")

# ═══════════════════════════════════════════════════════════
# 游戏 11: 幕后黑手 (遗漏变量)
# ═══════════════════════════════════════════════════════════
def show_game_11():
    top_nav(11);chapter_banner(11)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#1a1510 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🕵️</span><div><h3 style="color:#E07B39;margin:0 0 8px 0;">幕后黑手</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">咖啡连锁被指控'喝咖啡导致心脏病'——发病率高<b>40%</b>。<br>老板找你危机公关：<i>"去查查数据到底有没有问题。"</i></p></div></div></div>""",unsafe_allow_html=True)
    if "g11_data" not in st.session_state:
        np.random.seed(123);n=500;smoker=np.random.binomial(1,0.3,n)
        coffee=np.where(smoker==1,np.random.normal(5,2,n),np.random.normal(2,1.5,n));coffee=np.clip(coffee,0,10)
        heart=40+coffee*0.1+smoker*15+np.random.normal(0,5,n)
        st.session_state.g11_data=pd.DataFrame({"coffee":coffee,"smoker":smoker,"heart_risk":heart});st.session_state.g11_stage="act1"
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
        st.markdown("### 🎬 第二幕：幕后黑手现身");st.markdown("有个变量他们没给你看——**抽烟**。")
        smokers=df[df["smoker"]==1];nonsmokers=df[df["smoker"]==0]
        fig=go.Figure();fig.add_trace(go.Scatter(x=smokers["coffee"],y=smokers["heart_risk"],mode='markers',marker=dict(color='#FF4757',size=6,opacity=0.5),name='吸烟者'));fig.add_trace(go.Scatter(x=nonsmokers["coffee"],y=nonsmokers["heart_risk"],mode='markers',marker=dict(color='#00B4D8',size=6,opacity=0.5),name='不吸烟者'))
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"每日咖啡杯数"},yaxis={"gridcolor":"#2A2D35","title":"心脏病风险"},height=350)
        st.plotly_chart(fig,use_container_width=True)
        st.success("吸烟组和不吸烟组内部，咖啡与心脏病的关系消失了。吸烟(红色)整体更高——是吸烟同时推高了咖啡消费和心脏病风险。")
        reveal_box("咖啡不是罪魁祸首——是吸烟这个没被看到的变量","第一眼看数据是不是也觉得咖啡有问题？那个+40%是<b>吸烟</b>一手造成的。<br>遗漏变量偏差：大数据时代最常见的陷阱。","'学音乐的孩子成绩好'——漏掉了'有条件的家庭才能让孩子学音乐'。每当你看到X→Y——问自己：有没有Z同时影响X和Y？",f"遗漏变量偏差。玩家判断={st.session_state.g11_judge}。",11)
        math_detail("**DAG** 咖啡$$(X)\\leftarrow$$吸烟$$(Z)\\rightarrow$$心脏病$$(Y)$$ **后门准则**：控制$$Z$$(分层)，伪关联消失。")
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
    top_nav(13);chapter_banner(13)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#15101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🪄</span><div><h3 style="color:#9B59B6;margin:0 0 8px 0;">收缩魔法</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">老板要你同时预测5个完全不相关的东西。<br>💬 实习生：<i>"把每个预测往0缩一点点——反而更准。"</i><br>💬 全办公室：<i>"你疯了？这些数据根本不相关！"</i></p></div></div></div>""",unsafe_allow_html=True)
    if "g13_phase" not in st.session_state: st.session_state.g13_phase="bet";st.session_state.g13_d=5
    if st.session_state.g13_phase=="bet":
        st.markdown("### 🤔 你觉得实习生的'收缩法'靠谱吗？")
        c1,c2,c3=st.columns(3)
        if c1.button("🤬 胡扯！",key="g13_b1",use_container_width=True,type="primary"): st.session_state.g13_bet="mle";st.session_state.g13_phase="experiment";st.rerun()
        if c2.button("🤔 不确定",key="g13_b2",use_container_width=True): st.session_state.g13_bet="unsure";st.session_state.g13_phase="experiment";st.rerun()
        if c3.button("🪄 说不定有理",key="g13_b3",use_container_width=True): st.session_state.g13_bet="js";st.session_state.g13_phase="experiment";st.rerun()
    elif st.session_state.g13_phase=="experiment":
        d=st.slider("同时估计几个参数？",1,800,st.session_state.g13_d,key="g13_ds");st.session_state.g13_d=d
        if st.button("🎲 生成参数并对比",key="g13_gen",type="primary"):
            np.random.seed(int(time.time()));true_theta=np.random.normal(0,3,d);X=true_theta+np.random.normal(0,1,d)
            mle_mse=np.mean((X-true_theta)**2);shrinkage=max(0,1-(d-2)/np.sum(X**2)) if d>=3 else 1.0;js=shrinkage*X;js_mse=np.mean((js-true_theta)**2)
            st.session_state.g13_mle=mle_mse;st.session_state.g13_js=js_mse;st.session_state.g13_d=d
            c1,c2=st.columns(2);c1.metric("🅰️ MLE",f"MSE={mle_mse:.3f}");delta=mle_mse-js_mse;c2.metric("🅱️ JS",f"MSE={js_mse:.3f}",delta=f"低{delta:.3f}" if delta>0 else None)
            if d<3: st.info(f"d={d}<3时JS无优势")
            elif js_mse<mle_mse: st.success(f"✅ d={d}≥3！JS比MLE低{(1-js_mse/mle_mse)*100:.1f}%！实习生的疯子法赢了。")
            d_range=list(range(1,min(d+50,201),max(1,d//30)))
            mle_arr=[];js_arr=[]
            for dd in d_range:
                th=np.random.normal(0,3,dd);x=th+np.random.normal(0,1,dd);mle_arr.append(np.mean((x-th)**2))
                s=max(0,1-(dd-2)/np.sum(x**2)) if dd>=3 else 1.0;js_arr.append(np.mean((s*x-th)**2))
            fig=go.Figure();fig.add_trace(go.Scatter(x=d_range,y=mle_arr,mode='lines',line=dict(color='#FF4757',width=2.5),name='MLE'));fig.add_trace(go.Scatter(x=d_range,y=js_arr,mode='lines',line=dict(color='#9B59B6',width=2.5),name='JS'))
            fig.add_vline(x=3,line_dash="dash",line_color="#F0B90B",annotation_text="d=3→JS反超");fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"维度d"},yaxis={"gridcolor":"#2A2D35","title":"MSE"},height=300)
            st.plotly_chart(fig,use_container_width=True)
            if d>=3 and js_mse<mle_mse:
                if st.button("💡 为什么无关信息反而更准？",key="g13_rev",type="primary",use_container_width=True): st.session_state.g13_phase="final_reveal";st.rerun()
    if st.session_state.g13_phase=="final_reveal":
        d=st.session_state.g13_d;mle=st.session_state.g13_mle;js_mse=st.session_state.g13_js
        reveal_box("偏差换方差——把无关的东西拉在一起反而更准",f"d={d}时JS比MLE低<b>{(1-js_mse/mle)*100:.1f}%</b>。<br>MLE无偏但方差大。JS向0收缩→引入偏差但大幅降低方差。<br><b>MSE=方差+偏差²。方差降得比偏差涨得多→净赚。</b><br>这就是L2正则化/Weight Decay的数学基础。","问5个朋友'今晚几度'——各说各的。把所有人往平均拉一下，反而每个人的答案都更准了。'最优'≠'直观'。",f"JS。d={d},MLE MSE={mle:.3f},JS MSE={js_mse:.3f}。",13)
        math_detail("**JS**($$d\\ge3$$) $$\\hat{\\theta}^{JS}=\\left(1-\\frac{d-2}{\\|X\\|^2}\\right)X$$ $$\\text{MSE}=\\text{方差}+\\text{偏差}^2$$ MLE无偏(方差大)，JS有偏(方差小)→总误差更低。")
        if st.button("🔄 重新实验",key="g13_again",use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("g13_"): del st.session_state[k]
            st.rerun()
        complete_game(13);update_radar("估计智慧",4)

# ═══════════════════════════════════════════════════════════
# 游戏 14: 空心球 (高斯环)
# ═══════════════════════════════════════════════════════════
def show_game_14():
    top_nav(14);chapter_banner(14)
    st.markdown("""<div style="background:linear-gradient(135deg,#1A1D24 0%,#10101a 100%);border:1px solid #2A2D35;border-radius:16px;padding:28px;margin-bottom:20px;"><div style="display:flex;gap:20px;align-items:start;"><span style="font-size:48px;">🍉</span><div><h3 style="color:#9B59B6;margin:0 0 8px 0;">空心球</h3><p style="color:#E4E6EB;font-size:15px;line-height:1.7;">你是游戏开发者。2D地图上NPC散布在圆圈里——正常。<br>升级到100维后，所有NPC挤在一层薄壳上，<b>市中心空无一人</b>。<br>💬 <i>"出bug了？"</i> 没有。数学就是这样。</p></div></div></div>""",unsafe_allow_html=True)
    if "g14_phase" not in st.session_state: st.session_state.g14_phase="low_dim"
    if st.session_state.g14_phase=="low_dim":
        np.random.seed(42);pts_2d=np.random.normal(0,1,(500,2));dists_2d=np.sqrt(np.sum(pts_2d**2,axis=1))
        fig=go.Figure();fig.add_trace(go.Histogram(x=dists_2d,nbinsx=30,marker_color='#00B4D8',opacity=0.7))
        fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"到原点距离"},yaxis={"gridcolor":"#2A2D35"},height=220,title={"text":"d=2：宽分布——各处都有点","font":{"color":"#E4E6EB"}})
        st.plotly_chart(fig,use_container_width=True)
        st.caption(f"d=2：变异系数≈{np.std(dists_2d)/np.mean(dists_2d)*100:.0f}%——分布很宽。")
        st.markdown("#### 🤔 升到100维——点会怎么分布？")
        c1,c2=st.columns(2)
        if c1.button("还是散布各处",key="g14_b1",use_container_width=True): st.session_state.g14_phase="explore";st.rerun()
        if c2.button("挤到边缘上了",key="g14_b2",use_container_width=True,type="primary"): st.session_state.g14_phase="explore";st.rerun()
    elif st.session_state.g14_phase=="explore":
        d=st.slider("🎚️ 维度d",2,1000,10);st.session_state.g14_d=d
        if st.button("🎲 撒1000个点",key="g14_go",type="primary"):
            np.random.seed(42);points=np.random.normal(0,1,(1000,d));distances=np.sqrt(np.sum(points**2,axis=1))
            cv=np.std(distances)/np.mean(distances)*100;theo=np.sqrt(d)
            fig=go.Figure();fig.add_trace(go.Histogram(x=distances,nbinsx=50,marker_color='#9B59B6',opacity=0.7));fig.add_vline(x=theo,line_dash="dash",line_color="#F0B90B",line_width=2,annotation_text=f"√d={theo:.1f}")
            fig.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"到原点距离"},yaxis={"gridcolor":"#2A2D35"},height=280)
            st.plotly_chart(fig,use_container_width=True)
            st.markdown(f"理论≈√{d}=**{theo:.1f}** | 实际均值=**{np.mean(distances):.2f}** | 变异系数=**{cv:.1f}%**")
            if cv<5:
                st.warning("💀 分布变成一根针！所有点在同一壳上。原点空无一人。")
                if st.button("💡 为什么高维空间是空心的？",key="g14_rev",type="primary",use_container_width=True): st.session_state.g14_phase="final_reveal";st.session_state.g14_cv=cv;st.session_state.g14_theo=theo;st.rerun()
            elif cv<20: st.info("📉 开始收窄...")
            else: st.success("🌍 还很宽——低维有'中心'概念。")
    if st.session_state.g14_phase=="final_reveal":
        d=st.session_state.g14_d;cv=st.session_state.g14_cv;theo=st.session_state.g14_theo
        skin=[(1-0.99**dd)*100 for dd in[3,5,10,30,50,100,200,500,1000]]
        fig2=go.Figure();fig2.add_trace(go.Scatter(x=[3,5,10,30,50,100,200,500,1000],y=skin,mode='lines+markers',line=dict(color='#9B59B6',width=2.5),marker=dict(size=10,color='#F0B90B')))
        fig2.update_layout(plot_bgcolor="#1A1D24",paper_bgcolor="#1A1D24",font={"color":"#E4E6EB"},xaxis={"gridcolor":"#2A2D35","title":"维度"},yaxis={"gridcolor":"#2A2D35","title":"皮体积占比(%)"},height=260)
        st.plotly_chart(fig2,use_container_width=True)
        reveal_box("高维空间——球是空的，点全在壳上",f"d={d}维时变异系数仅<b>{cv:.1f}%</b>。<br>所有点距离原点≈√{d}=<b>{theo:.1f}</b>——几乎零波动。<br>原点附近空无一人。球内是<b>空的</b>。<br>这就是embedding维度不能太高的原因。","降维不是妥协，是救命。高维是'极度拥挤又极度空旷'的悖论。",f"高斯环。d={d}，CV={cv:.1f}%。",14)
        math_detail("**高斯环** $$X\\sim\\mathcal{N}(0,I_d)$$ $$\\|X\\|\\approx\\sqrt{d}$$ 变异系数$$\\to0$$ **西瓜皮** $$=1-0.99^d$$")
        check_achievement("空心球发现者") if d>=500 else None
        if st.button("🔄 重新探索",key="g14_again",use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("g14_"): del st.session_state[k]
            st.rerun()
        complete_game(14);update_radar("维度直觉",4)

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
# MAIN + ROUTER
# ═══════════════════════════════════════════════════════════
GAME_ROUTER={"lobby":show_lobby,"1":show_game_01,"2":show_game_02,"3":show_game_03,"4":show_game_04,"5":show_game_05,"6":show_game_06,"7":show_game_07,"8":show_game_08,"9":show_game_09,"10":show_game_10,"11":show_game_11,"12":show_game_12,"13":show_game_13,"14":show_game_14,"15":show_game_15}

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
        st.subheader("🤖 AI 解说")
        st.text_input("API Key",type="password",key="ai_api_key",placeholder="DeepSeek/OpenAI Key")
        st.text_input("API Base URL",value="https://api.deepseek.com",key="ai_base_url")
        st.markdown("---");st.caption("《程序设计与科学计算》期末")
    cur=st.session_state.get("current_game","lobby")
    if cur in GAME_ROUTER: GAME_ROUTER[cur]()
    else: show_lobby()

if __name__=="__main__": main()
