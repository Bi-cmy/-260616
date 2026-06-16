"""插入数学公式 - 使用 complete_game(X, score= 精确匹配"""
import re

formulas = {}
formulas[1] = r"""**几何分布** $$P(X=k)=(1-p)^{k-1}p$$
**累积概率** $$P(X \le k)=1-(1-p)^k$$
**期望** $$E[X]=\frac{1}{p}=100$$ **中位数 P50** $$\approx 69$$
**无记忆性** $$P(X>k+m\mid X>k)=P(X>m)$$——每次独立，"垫刀"是错觉。"""
formulas[2] = r"""**贝叶斯推导**：钥匙在初选盒子概率 $$P(C=K)=\frac{1}{3}$$
主持人永远不开有钥匙的盒子 → 换盒获胜 $$P(\text{换盒赢})=\frac{2}{3}$$
$$P(\text{换盒赢}\mid H=h)=\frac{P(H=h\mid C\neq K)P(C\neq K)}{P(H=h)}=\frac{2}{3}$$"""
formulas[3] = r"""$$P(\text{碰撞})=1-\frac{365\cdot364\cdots(365-N+1)}{365^N}\approx 1-e^{-N(N-1)/730}$$
23人→253对→50.7% | 50人→1225对→97%
比较的不是"你vs某人"，而是所有 $$C(N,2)=\frac{N(N-1)}{2}$$ 对。"""
formulas[4] = r"""**系综平均**（平行宇宙）：$$E[R]=0.5\times1.5+0.5\times0.6=1.05$$ 每局+5%
**时间平均**（你的轨迹）：几何均值 $$G=\sqrt{1.5\times0.6}=\sqrt{0.9}\approx0.949$$
n局后余额 $$\approx 1000\times(1.5\cdot0.6)^{n/2}=1000\times0.9^{n/2}$$
算术平均为正，几何均值<1 → **非各态历经**：时间平均≠系综平均。"""
formulas[5] = r"""**模型**：$$X_i=\theta_i+\varepsilon_i$$，$$\theta_i\sim\mathcal{N}(75,10^2)$$ 真实能力，$$\varepsilon_i\sim\mathcal{N}(0,8^2)$$ 运气。
极端值=中等$$\theta$$+同向大噪声，噪声下赛季独立抽取→趋于0→"回归"。
$$E[\theta\mid X_1=x_1]=\mu+\frac{\sigma_\theta^2}{\sigma_\theta^2+\sigma_\varepsilon^2}(x_1-\mu)$$ 收缩因子<1。"""
formulas[6] = r"""华总 $$=0.8\times90\%+0.2\times55\%=83\%$$
张总 $$=0.2\times95\%+0.8\times61\%=78\%$$
每种病张>华，但总体华>张——轻症占比80% vs 20%扭曲了总体排名。
**辛普森悖论**：组样本量严重不均衡时，总体趋势可与每组内趋势完全相反。"""
formulas[7] = r"""观测成功率 $$=\frac{\#\{成功\land发声\}}{\#\{发声\}}\approx100\%$$
真实成功率 $$=\frac{\#\{成功\}}{N}=0.5\%$$
$$P(发声\mid成功)\approx1$$ 但 $$P(发声\mid失败)\approx0$$——失败者天然不发声。"""
formulas[8] = r"""**贝叶斯定理** $$P(D\mid+)=\frac{P(+\mid D)P(D)}{P(+\mid D)P(D)+P(+\mid \neg D)P(\neg D)}$$
发病率0.1%准确率99%：$$P(D\mid+)=\frac{0.99\times0.001}{0.99\times0.001+0.01\times0.999}\approx9.0\%$$
**PPV**=真阳性÷总阳性。先问基础概率，再看条件概率。"""
formulas[9] = r"""**虚假相关**：$$\text{Corr}(X,Y)>0.9$$ 但 $$X\not\rightarrow Y$$
因果结构：$$X\leftarrow Z\rightarrow Y$$（冰淇淋←气温→溺水）
相关是对称的（$$\text{Corr}(X,Y)=\text{Corr}(Y,X)$$），因果不是。"""
formulas[10] = r"""横截面数据中，$$X$$和$$Y$$的统计关联无法区分 $$X\rightarrow Y$$ 还是 $$Y\rightarrow X$$。
只有**时间先后**或**实验干预**能确定因果方向。
$$P(Y\mid X)\neq P(Y\mid do(X))$$——观察数据≠干预结果。"""
formulas[11] = r"""**DAG**：咖啡$$(X)\leftarrow$$吸烟$$(Z)\rightarrow$$心脏病$$(Y)$$
$$Z$$是混淆因子——同时影响$$X$$和$$Y$$。
**后门准则**：控制$$Z$$（分层），$$X$$与$$Y$$的虚假关联消失。"""
formulas[12] = r"""全部报名者：$$\text{Corr}(B,T)=0$$（颜值与演技独立）
控制对撞条件后：$$\text{Corr}(B,T\mid B+T\geq\theta)<0$$（伪负相关！）
$$B\rightarrow[\text{录取}]\leftarrow T$$——控制对撞变量在两个独立变量间打开了伪相关路径。"""
formulas[13] = r"""**MLE**：$$\hat{\theta}_i^{MLE}=X_i$$（无偏，方差=1）
**James-Stein**($$d\ge3$$)：$$\hat{\theta}^{JS}=\left(1-\frac{d-2}{\|X\|^2}\right)X$$
$$\text{MSE}=\text{方差}+\text{偏差}^2$$——向0收缩引入偏差但大幅降低方差。
$$d\ge3$$时 JS的MSE **始终**低于 MLE——用"无关"信息帮忙反而更准。"""
formulas[14] = r"""**高斯环**：$$X\sim\mathcal{N}(0,I_d)$$，模长 $$\|X\|\approx\sqrt{d}$$，变异系数$$\to0$$
**距离集中**：所有点互相距离趋于相等——"最近邻"在高维失去意义。
**西瓜皮**：$$d$$维球皮厚1%半径，皮体积占比 $$=1-0.99^d$$，d=1000时占99.997%。"""
formulas[15] = r"""**Cover定理**：$$N$$个点在$$d$$维空间中被随机超平面线性可分的概率随$$d$$增大。
当$$d>N$$时，几乎任意两组点集都线性可分。
每增加一个噪声维度，数据获得额外的分离自由度——"垃圾特征"堆在一起构建了分离能力。"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find complete_game(X, score= lines with their line numbers
targets = {}
for i, line in enumerate(lines):
    m = re.match(r'^(\s+)complete_game\((\d+), score=', line)
    if m:
        gid = int(m.group(2))
        if gid not in targets:  # Only match first occurrence per game
            targets[gid] = (i, m.group(1))

# Insert in reverse order to preserve line numbers
for gid in sorted(targets.keys(), reverse=True):
    if gid not in formulas:
        continue
    line_no, indent = targets[gid]
    formula = formulas[gid]
    block = f'''{indent}with st.expander("📐 数学细节"):
{indent}    st.markdown(r"""
{formula}
{indent}""")
'''
    lines.insert(line_no, block)
    print(f'Game {gid}: inserted at line {line_no}')

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('All done')
