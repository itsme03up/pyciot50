import json
import random
import streamlit as st
from dataclasses import dataclass

# ====== ページ設定 ======
st.set_page_config(page_title="勇者の冒険：CBTクエスト", page_icon="🐉", layout="centered")

# ====== ドラクエ風UI用CSS ======
DQ_CSS = """
.dq-window-1 {
  background-color: black;
  padding: 0.15rem;
  width: fit-content;
  border-radius: 0.4rem;
}

.dq-window-2 {
  background-color: white;
  padding: 0.2rem;
  border-radius: 0.3rem;
  width: fit-content;
}

.dq-window-3 {
  color: white;
  background-color: black;
  font-family: "Courier New", monospace;
  border-radius: 0.3rem;
  padding: 1.0rem 0.75rem;
  line-height: 2;
  width: fit-content;
  font-weight: bold;
}

/* 背景：ドラクエ風の青いグラデーション */
html, body, [data-testid="stAppViewContainer"] {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%) !important;
  color: #ffffff !important;
  font-family: "Courier New", monospace !important;
  font-weight: bold;
}

/* 見出し：ドラクエ風のタイトル */
h1, h2, h3, h4, h5 {
  color: #ffff00 !important;
  text-shadow: 2px 2px 0px #000000, -1px -1px 0px #000000, 1px -1px 0px #000000, -1px 1px 0px #000000;
  letter-spacing: .02em;
  text-align: center;
  font-family: "Courier New", monospace !important;
}

/* メインコンテナ */
.block-container { 
  padding-top: 2rem !important;
  max-width: 800px !important;
}

/* Streamlitのアラート要素をドラクエ風に */
.stAlert {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  color: #ffffff !important;
  font-family: "Courier New", monospace !important;
  font-weight: bold !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* ラジオボタン：コマンド風 */
[data-testid="stRadio"] {
  background: transparent;
  border: none;
  padding: 1rem 0;
}

[data-testid="stRadio"] label {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  padding: 0 !important;
  margin-bottom: 0.5rem !important;
  color: #ffffff !important;
  font-family: "Courier New", monospace !important;
  font-weight: bold !important;
  cursor: pointer;
  display: block !important;
}

/* ボタン：透明化 */
button[kind="primary"], button {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  color: transparent !important;
  font-family: "Courier New", monospace !important;
  font-weight: bold !important;
  font-size: 16px !important;
  padding: 0 !important;
  box-shadow: none !important;
  transition: none !important;
  height: 0px !important;
  min-height: 0px !important;
  visibility: hidden !important;
  position: absolute !important;
}

/* HPバー：ドラクエ風 */
.dq-hpbar-container {
  background-color: black;
  padding: 0.15rem;
  border-radius: 0.4rem;
  margin: 8px 0;
}

.dq-hpbar-border {
  background-color: white;
  padding: 0.2rem;
  border-radius: 0.3rem;
}

.dq-hpbar {
  background: black;
  border-radius: 0.3rem;
  height: 24px;
  position: relative;
  overflow: hidden;
  padding: 2px;
}

.dq-hpbar-fill {
  height: 100%;
  background: var(--hp-color);
  width: var(--w, 100%);
  transition: width .6s ease;
  position: relative;
  border-radius: 2px;
}

.dq-hpbar-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ffffff;
  font-family: "Courier New", monospace;
  font-weight: bold;
  font-size: 12px;
  text-shadow: 1px 1px 0px #000000;
  z-index: 10;
}

/* ダメージテキスト：ドラクエ風 */
.dq-damage {
  color: #ff0000;
  font-family: "Courier New", monospace;
  font-weight: bold;
  font-size: 24px;
  text-shadow: 2px 2px 0px #000000, -1px -1px 0px #000000, 1px -1px 0px #000000, -1px 1px 0px #000000;
  animation: dq-float 1.2s ease forwards;
  text-align: center;
}

@keyframes dq-float {
  0% { transform: translateY(0px); opacity: 1; }
  50% { transform: translateY(-20px); opacity: 1; }
  100% { transform: translateY(-40px); opacity: 0; }
}

/* 区切り線 */
hr, [data-testid="stDivider"] {
  border: 2px solid #ffffff !important;
  margin: 2rem 0 !important;
}

/* ステータス表示 */
.dq-status {
  background: transparent;
  margin: 1rem 0;
}

.dq-character {
  text-align: center;
  font-size: 2rem;
  margin: 0.5rem 0;
}

/* メッセージの▼マーク */
.dq-continue {
  text-align: center;
  color: #ffff00;
  font-size: 20px;
  animation: blink 1.5s infinite;
  margin-top: 1rem;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}
"""

DRAGON_QUEST_CSS = f"<style>{DQ_CSS}</style>"
st.markdown(DRAGON_QUEST_CSS, unsafe_allow_html=True)

# ====== 問題データ読み込み ======
def load_questions(fp="questions.json"):
    """JSONファイルから問題データを読み込む"""
    try:
        with open(fp, encoding="utf-8") as f:
            qs = json.load(f)
        # バリデーション（aは1-4、choices4つ等）
        ok = [q for q in qs if 1 <= int(q["a"]) <= 4 and len(q["choices"]) == 4]
        if len(ok) != len(qs):
            st.warning(f"構文エラーのある問題をスキップしました（{len(qs) - len(ok)}問）")
        return ok
    except FileNotFoundError:
        st.error(f"問題ファイル '{fp}' が見つかりません。")
        return []
    except json.JSONDecodeError:
        st.error(f"問題ファイル '{fp}' のJSON形式が正しくありません。")
        return []
    except Exception as e:
        st.error(f"問題ファイルの読み込みでエラーが発生しました: {e}")
        return []

# ====== モデル ======
@dataclass
class Fighter:
    name: str
    max_hp: int
    atk: int
    hp: int | None = None

    def __post_init__(self):
        if self.hp is None:
            self.hp = self.max_hp

    def alive(self) -> bool:
        return self.hp > 0

# ====== ユーティリティ ======
def init_game():
    st.session_state.player = Fighter("勇者", max_hp=120, atk=20)
    st.session_state.boss   = Fighter("タイポ魔王", max_hp=200, atk=18)
    questions = load_questions()
    if not questions:
        st.error("問題が読み込めませんでした。ゲームを開始できません。")
        return
    pool = questions[:]
    random.shuffle(pool)
    st.session_state.qs = pool
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.streak = 0    # 連続正解でクリティカル
    st.session_state.last = None   # ("correct"/"wrong", 正解番号, 解説)
    st.session_state.state = "asking"

def dq_hp_bar(name: str, current: int, maximum: int, character: str):
    """ドラクエ風HPバー表示（3層構造）"""
    pct = max(0, min(1, current/maximum))
    width = f"{pct*100:.1f}%"
    
    # HP割合に応じて色を変更（ドラクエ風）
    if pct > 0.6:
        hp_color = "#00ff00"  # 緑
    elif pct > 0.3:
        hp_color = "#ffff00"  # 黄
    else:
        hp_color = "#ff0000"  # 赤
    
    html = f"""
    <div class="dq-status">
        <div class="dq-character">{character}</div>
        <div class="dq-window-1">
            <div class="dq-window-2">
                <div class="dq-window-3" style="text-align: center; margin: 0; padding: 0.5rem;">
                    {name}
                </div>
            </div>
        </div>
        <div class="dq-hpbar-container">
            <div class="dq-hpbar-border">
                <div class="dq-hpbar">
                    <div class="dq-hpbar-fill" style="--w:{width}; --hp-color:{hp_color};"></div>
                    <div class="dq-hpbar-text">HP: {current} / {maximum}</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dq_message_box(message: str, title: str = ""):
    """ドラクエ風メッセージボックス（3層構造）"""
    title_html = f"""
    <div class="dq-window-1">
        <div class="dq-window-2">
            <div class="dq-window-3" style="color: #ffff00; text-align: center; margin: 0;">
                {title}
            </div>
        </div>
    </div>
    """ if title else ""
    
    html = f"""
    {title_html}
    <div class="dq-window-1">
        <div class="dq-window-2">
            <div class="dq-window-3">
                {message}
                <div class="dq-continue">▼</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dq_damage_text(text: str, is_damage: bool = True):
    """ドラクエ風ダメージ/回復テキスト"""
    css_class = "dq-damage"
    html = f'<div class="{css_class}">{text}</div>'
    st.markdown(html, unsafe_allow_html=True)

# ====== 初期化 ======
if "qs" not in st.session_state:
    init_game()

player = st.session_state.player
boss = st.session_state.boss

# ====== ヘッダ ======
st.markdown("## 🐉 勇者の冒険：CBTクエスト")
st.caption("正解で魔物を攻撃！ 不正解で反撃を受ける。3連続正解で **会心の一撃**！")

# リセットボタンも3層構造
reset_button_html = """
<div class="dq-window-1" style="margin: 1rem 0;">
    <div class="dq-window-2">
        <div class="dq-window-3" style="text-align: center; cursor: pointer;">
            冒険をやり直す
        </div>
    </div>
</div>
"""
st.markdown(reset_button_html, unsafe_allow_html=True)

if st.button("実行", key="reset"):
    init_game()
    st.rerun()

# HPバー（ドラクエ風）
c1, c2 = st.columns(2)
with c1:
    dq_hp_bar("勇者", player.hp, player.max_hp, "🧙‍♂️")
with c2:
    dq_hp_bar("タイポ魔王", boss.hp, boss.max_hp, "👾")

st.divider()

# ====== ゲーム終了判定 ======
if st.session_state.state == "finished":
    if boss.alive() and not player.alive():
        dq_message_box("勇者は力尽きた…", "😵 GAME OVER")
        st.error("💀 あなたは倒れてしまった… 期末までにもうひと踏ん張り！")
        st.snow()
    elif player.alive() and not boss.alive():
        dq_message_box("タイポ魔王をたおした！", "🏆 VICTORY!")
        st.success("🎉 勝利！ タイポ魔王は霧散した。知識の力で勝利を掴んだ！")
        st.balloons()
    else:
        if boss.hp < player.hp:
            dq_message_box("時間切れだが優勢！よく戦った！", "⌛ 引き分け")
        else:
            dq_message_box("時間切れで痛み分け。復習して再挑戦！", "⌛ 引き分け")
    
    # スコア表示をドラクエ風に（3層構造）
    score_html = f"""
    <div class="dq-window-1">
        <div class="dq-window-2">
            <div class="dq-window-3">
                <div style="color: #ffff00; text-align: center; font-size: 1.2em; margin-bottom: 1rem;">
                    冒険の結果
                </div>
                <div style="margin-bottom: 0.5rem;">
                    正答数: {st.session_state.score} / {len(st.session_state.qs)}
                </div>
                <div>
                    正答率: {st.session_state.score / len(st.session_state.qs) * 100:.1f}%
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(score_html, unsafe_allow_html=True)
    st.stop()

# ====== 出題 ======
idx = st.session_state.idx
if idx >= len(st.session_state.qs):
    st.session_state.state = "finished"
    st.rerun()

q = st.session_state.qs[idx]

# ドラクエ風の問題表示（3層構造）
html = f"""
<div class="dq-window-1">
    <div class="dq-window-2">
        <div class="dq-window-3">
            <div style="color: #ffff00; text-align: center; font-size: 1.2em; margin-bottom: 1rem;">
                ターン {idx+1}
            </div>
            <div style="margin-bottom: 0.5rem;">
                <strong>[Unit {q['unit']}] {q['topic']}</strong>
            </div>
            <div>
                {q["q"]}
            </div>
        </div>
    </div>
</div>
"""
st.markdown(html, unsafe_allow_html=True)

# 選択肢も3層構造で表示
choice = st.radio(
    "コマンドを選択せよ",
    options=[f"{i+1}) {c}" for i, c in enumerate(q["choices"])],
    index=None
)

# ====== 判定 ======
if st.session_state.state == "asking":
    disabled = choice is None
    # ドラクエ風ボタン（3層構造）
    button_html = f"""
    <div class="dq-window-1" style="margin: 1rem 0;">
        <div class="dq-window-2">
            <div class="dq-window-3" style="text-align: center; cursor: {'not-allowed' if disabled else 'pointer'}; opacity: {'0.5' if disabled else '1'};">
                ⚔️ たたかう
            </div>
        </div>
    </div>
    """
    st.markdown(button_html, unsafe_allow_html=True)
    
    if not disabled and st.button("実行", key="battle"):
        picked = None if choice is None else int(choice.split(")")[0])
        if picked == q["a"]:
            # 連続正解判定（3連続で会心の一撃）
            st.session_state.streak += 1
            crit = (st.session_state.streak >= 3)
            dmg = player.atk * (2 if crit else 1)
            boss.hp -= dmg
            st.session_state.score += 1
            st.session_state.last = ("correct", q["a"], q.get("exp",""), dmg, crit)
        else:
            st.session_state.streak = 0
            player.hp -= boss.atk
            st.session_state.last = ("wrong", q["a"], q.get("exp",""), boss.atk, False)
        st.session_state.state = "judged"
        st.rerun()

elif st.session_state.state == "judged":
    result, ans_idx, exp, amount, crit = st.session_state.last
    if result == "correct":
        crit_msg = "会心の一撃だ！" if crit else ""
        dq_message_box(f"正解！ {crit_msg}{boss.name}に {amount} のダメージを与えた！", "🗡️ 攻撃成功")
        dq_damage_text(f"-{amount}", True)
        if crit:
            st.toast("💥 会心の一撃！", icon="🔥")
    else:
        dq_message_box(f"不正解… {boss.name}の反撃！ {amount} のダメージを受けた！", "💀 被弾")
        
        # 正解表示をドラクエ風に（3層構造）
        correct_html = f"""
        <div class="dq-window-1">
            <div class="dq-window-2">
                <div class="dq-window-3">
                    <div style="margin-bottom: 0.5rem;">
                        <strong>正解は：</strong> {ans_idx}) {q['choices'][ans_idx-1]}
                    </div>
                    {f'<div><strong>解説：</strong> {exp}</div>' if exp else ''}
                </div>
            </div>
        </div>
        """
        st.markdown(correct_html, unsafe_allow_html=True)
        dq_damage_text(f"-{amount}", True)

    # 終了チェック
    end = (not player.alive()) or (not boss.alive())

    # 次へボタンも3層構造
    next_button_html = f"""
    <div class="dq-window-1" style="margin: 1rem 0;">
        <div class="dq-window-2">
            <div class="dq-window-3" style="text-align: center; cursor: pointer;">
                ▶ つぎへ
            </div>
        </div>
    </div>
    """
    st.markdown(next_button_html, unsafe_allow_html=True)
    
    if st.button("実行", key="next"):
        st.session_state.idx += 1
        st.session_state.state = "finished" if end else "asking"
        st.rerun()