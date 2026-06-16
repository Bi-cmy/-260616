from pathlib import Path

path = Path('app.py')
lines = path.read_text(encoding='utf-8').splitlines()
start = 1407  # line 1408
end = 1434    # before show_game_11
new_block = '''def show_game_10():
    top_nav(10)
    chapter_banner(10)

    st.markdown(
        """
        <div class="game-card">
            <h3>🐔 鸡与蛋</h3>
            <p style="color:#E4E6EB;font-size:15px;line-height:1.7;">
            三位委托人，各自拿着一份“看起来很有道理”的数据结论来找你。<br>
            你的任务不是只答题，而是要像侦探一样识别：<br>
            <b>这句话到底是真的找到了因果，还是把箭头画反了？</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cases = {
        "A": {"client": "👓 眼镜公司老板", "data": "戴眼镜的人，平均智商高出 8 分。p<0.001。", "claim": "推广眼镜→让下一代更聪明。", "truth": "高智商 → 更爱学习 → 更容易近视 → 需要眼镜。不是眼镜让人聪明。", "timeline": ["👶 童年视力习惯", "👓 近视形成 / 配眼镜", "📚 长期学习", "🧠 智力测验更高"]},
        "B": {"client": "🚒 消防局长", "data": "派出去的消防员越多，火灾财产损失越大。", "claim": "减少消防员→降低损失。", "truth": "大火 → 派出更多消防员 → 财产损失更大。不是消防员导致损失上升。", "timeline": ["🔥 火势扩大", "🚒 派出更多消防员", "🏚️ 财产损失上升"]},
        "C": {"client": "🏥 医院院长", "data": "住院时间越长的人，死亡率越高。", "claim": "尽早出院→减少死亡。", "truth": "病情更重 → 住院更久 → 死亡率更高。不是住院害死人。", "timeline": ["🧬 基础病情严重", "🏥 住院时间更长", "☠️ 死亡率更高"]},
    }

    if "g10_phase" not in st.session_state:
        st.session_state.g10_phase = "desk"
        st.session_state.g10_current = None
        st.session_state.g10_results = {}
        st.session_state.g10_first_impression = {}
        st.session_state.g10_arrow_choice = {}

    if st.session_state.g10_phase not in ("desk", "case", "reveal", "summary"):
        st.session_state.g10_phase = "desk"

    if st.session_state.g10_phase == "desk":
        st.markdown("### 🗂️ 案件桌面")
        st.caption("请选择一个案卷开始调查。处理完一个案卷后，会自动回到这里。")
        cols = st.columns(3)
        for i, key in enumerate(["A", "B", "C"]):
            case = cases[key]
            done = key in st.session_state.g10_results
            border = "#00D4AA" if done else "#2A2D35"
            with cols[i]:
                st.markdown(f'''<div style="background:#1A1D24;border:2px solid {border};border-radius:14px;padding:18px;min-height:170px;"><span style="font-size:28px;">{case['client'].split()[0]}</span><br><span style="color:#E4E6EB;font-weight:800;font-size:18px;">案卷 {key}</span><br><span style="color:#8B8F98;font-size:13px;">{case['client']}</span><br><br><span style="color:#E4E6EB;font-size:13px;">{case['data']}</span><br><span style="color:{'#00D4AA' if done else '#8B8F98'};font-size:12px;">{'✅ 已处理' if done else '待调查'}</span></div>''', unsafe_allow_html=True)
                if st.button(f"打开案卷 {key}", key=f"g10_open_{key}", use_container_width=True):
                    st.session_state.g10_current = key
                    st.session_state.g10_phase = "case"
                    st.rerun()
        if len(st.session_state.g10_results) == 3:
            if st.button("📊 查看结案总结", key="g10_to_summary", type="primary", use_container_width=True):
                st.session_state.g10_phase = "summary"
                st.rerun()

    elif st.session_state.g10_phase == "case":
        ck = st.session_state.g10_current
        case = cases[ck]
        st.markdown(f"### 📋 案卷 {ck}：{case['client']}")
        st.markdown(f"📊 **数据摘要**：{case['data']}")
        st.markdown(f"💬 **委托人结论**：*{case['claim']}*")

        if ck not in st.session_state.g10_first_impression:
            st.markdown("#### 第一反应：这个结论看起来靠谱吗？")
            c1, c2, c3 = st.columns(3)
            if c1.button("✅ 好像有道理", key=f"g10_impression_yes_{ck}", use_container_width=True):
                st.session_state.g10_first_impression[ck] = "seems_right"
                st.rerun()
            if c2.button("🤔 感觉有问题", key=f"g10_impression_maybe_{ck}", use_container_width=True):
                st.session_state.g10_first_impression[ck] = "suspicious"
                st.rerun()
            if c3.button("❓ 我不确定", key=f"g10_impression_unsure_{ck}", use_container_width=True):
                st.session_state.g10_first_impression[ck] = "unsure"
                st.rerun()
            return

        st.info(f"你的第一反应：**{st.session_state.g10_first_impression[ck]}**")
        st.markdown("#### 现在真正判断：因果箭头怎么画？")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("A → B", key=f"g10_arrow_ab_{ck}", use_container_width=True):
            st.session_state.g10_arrow_choice[ck] = "AB"
            st.session_state.g10_results[ck] = False
            st.session_state.g10_phase = "reveal"
            st.rerun()
        if c2.button("B → A", key=f"g10_arrow_ba_{ck}", use_container_width=True, type="primary"):
            st.session_state.g10_arrow_choice[ck] = "BA"
            st.session_state.g10_results[ck] = True
            st.session_state.g10_phase = "reveal"
            st.rerun()
        if c3.button("🔄 双向", key=f"g10_arrow_both_{ck}", use_container_width=True):
            st.session_state.g10_arrow_choice[ck] = "both"
            st.session_state.g10_results[ck] = False
            st.session_state.g10_phase = "reveal"
            st.rerun()
        if c4.button("❌ 无关", key=f"g10_arrow_none_{ck}", use_container_width=True):
            st.session_state.g10_arrow_choice[ck] = "none"
            st.session_state.g10_results[ck] = False
            st.session_state.g10_phase = "reveal"
            st.rerun()

    elif st.session_state.g10_phase == "reveal":
        ck = st.session_state.g10_current
        case = cases[ck]
        correct = st.session_state.g10_results[ck]
        if correct:
            st.success("✅ 你看出来了：他们把箭头画反了。")
        else:
            st.error("❌ 问题不在相关本身，而在于因果方向被画反了。")
        st.markdown("### ⏱️ 时间轴揭示")
        html = '<div style="background:#1A1D24;border:1px solid #2A2D35;border-radius:12px;padding:18px;">'
        for i, item in enumerate(case['timeline']):
            html += f'<div style="color:#E4E6EB;font-size:15px;line-height:1.8;">{item}</div>'
            if i < len(case['timeline']) - 1:
                html += '<div style="color:#8B8F98;font-size:20px;">↓</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
        st.markdown(f"### 🔍 真相\n**{case['truth']}**")
        if len(st.session_state.g10_results) < 3:
            if st.button("📂 回到案件桌面，处理下一案", key="g10_back_to_desk", type="primary", use_container_width=True):
                st.session_state.g10_phase = "desk"
                st.session_state.g10_current = None
                st.rerun()
        else:
            if st.button("📊 查看结案总结", key="g10_summary_now", type="primary", use_container_width=True):
                st.session_state.g10_phase = "summary"
                st.rerun()

    elif st.session_state.g10_phase == "summary":
        st.markdown("### 🧾 结案总结")
        rows = []
        for ck, case in cases.items():
            first = st.session_state.g10_first_impression.get(ck, '-')
            arrow = st.session_state.g10_arrow_choice.get(ck, '-')
            ok = '✅' if st.session_state.g10_results.get(ck) else '❌'
            rows.append(f"| {ck} | {case['client']} | {first} | {arrow} | {ok} |")
        table = '| 案卷 | 委托人 | 你第一反应 | 你最终判断 | 结果 |\n|------|--------|------------|------------|------|\n' + '\n'.join(rows)
        st.markdown(table)
        correct_n = sum(1 for v in st.session_state.g10_results.values() if v)
        reveal_box("横截面相关无法告诉你因果方向", f"你共处理了 3 个案子，答对了 <b>{correct_n}/3</b>。<br>真正的问题不是相关强不强，而是：<b>谁先发生，谁后发生？</b><br>时间顺序和干预，才是决定箭头方向的关键。", "喝红酒的人更健康？加班多的人升职更快？看到相关，先问：箭头凭什么这样画？",)
        math_detail(r"""在横截面数据里，$$X$$ 与 $$Y$$ 的统计关联并不能区分：
$$X \to Y \quad \text{还是} \quad Y \to X$$
只有时间顺序（temporal ordering）或实验干预（intervention）能帮助识别因果方向。
$$P(Y\mid X) \neq P(Y\mid do(X))$$""")
        if st.button("🔄 重新办案", key="g10_retry", use_container_width=True):
            reset_game("g10_")
            st.rerun()
        complete_game(10)
        update_radar("因果链条", 4 if correct_n >= 2 else 2)
