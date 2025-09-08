import json
import random
import streamlit as st
from dataclasses import dataclass
import os

# ====== バランス定数（基準は40問） ======
BASELINE_QUESTIONS = 40
PLAYER_BASE_HP = 120
BOSS_BASE_HP = 200
PLAYER_ATK = 20
BOSS_ATK = 18
# 追加倍率（環境変数で上書き可: HP_SCALE）
try:
    EXTRA_HP_SCALE = float(os.getenv("HP_SCALE", "1.0"))
except Exception:
    EXTRA_HP_SCALE = 1.0
# ====== ページ設定 ======
st.set_page_config(page_title="勇者の冒険：CBTクエスト", layout="wide")

# ====== ドラクエ風UI用CSS（見た目と操作性を改善） ======
DQ_CSS = """
/* Retro JP font (細字で省スペース) */
@import url('https://fonts.googleapis.com/css2?family=DotGothic16&display=swap');

:root {
  --dq-font: 'DotGothic16', 'Noto Sans JP', system-ui, sans-serif;
  --dq-white: #ffffff;
  --dq-black: #000000;
}

/* 1画面表示 → 余白縮小 + スクロール抑制 */
html, body {
  background: var(--dq-black) !important;
  color: var(--dq-white) !important;
  font-family: var(--dq-font) !important;
  font-weight: 700;
  height: 100%;
  overflow: hidden; /* 極力スクロールさせない */
}
[data-testid="stAppViewContainer"] {
  height: 100vh;
  overflow: hidden;
}

/* Streamlit UIの余白/ヘッダ類を隠す */
#MainMenu {visibility: hidden;}
header {visibility: hidden; height: 0;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {display:none}

/* 見出し（白のみ） */
h1, h2, h3, h4, h5 {
  color: var(--dq-white) !important;
  text-shadow: 2px 2px 0 #000;
  letter-spacing: .02em;
  text-align: center;
  font-family: var(--dq-font) !important;
  margin: .25rem 0 .5rem 0 !important;
}

/* メインコンテナ幅と余白（高さに合わせて縮むフォント） */
.block-container {
  padding-top: .5rem !important;
  padding-bottom: .5rem !important;
  max-width: 1100px !important;
}
body { font-size: clamp(12px, 1.8vh, 16px); }

/* アラート：モノクロで控えめ */
.stAlert {
  background: rgba(255,255,255,.04) !important;
  border: 2px solid #fff !important;
  border-radius: 4px !important;
  color: #fff !important;
  font-family: var(--dq-font) !important;
  font-weight: 700 !important;
  box-shadow: none !important;
}

/* ラジオ（コマンド風・省スペース） */
[data-testid="stRadio"] { padding: .25rem 0 .1rem 0; }
[data-testid="stRadio"] label {
  color: #fff !important;
  padding: .15rem 0 !important;
  margin-bottom: .15rem !important;
  display: block !important;
}

/* ボタン：モノクロDQ風 */
.stButton > button {
  background: #000 !important;
  color: #fff !important;
  border: 2px solid #fff !important;
  border-radius: 4px !important;
  font-family: var(--dq-font) !important;
  font-weight: 800 !important;
  font-size: clamp(12px, 1.8vh, 16px) !important;
  padding: .45rem .7rem !important;
  box-shadow: 0 0 0 3px #000, 0 0 0 5px #fff !important;
}
.stButton > button:hover { filter: brightness(1.1) contrast(1.05); }
.stButton > button:active { transform: translateY(1px); }
.stButton > button:disabled { opacity: .5 !important; cursor: not-allowed !important; }

/* HPバー（省スペース） */
.dq-hpbar-container { background-color: black; padding: 0.12rem; border-radius: 0.35rem; margin: 4px 0; }
.dq-hpbar-border { background-color: white; padding: 0.16rem; border-radius: 0.25rem; }
.dq-hpbar { background: black; border-radius: 0.25rem; height: 18px; position: relative; overflow: hidden; padding: 2px; }
.dq-hpbar-fill { height: 100%; background: var(--hp-color); width: var(--w, 100%); transition: width .4s ease; border-radius: 2px; }
.dq-hpbar-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #fff; font-family: var(--dq-font); font-weight: 800; font-size: 11px; text-shadow: 1px 1px 0px #000; z-index: 10; }

/* 3層ウィンドウ（白黒） */
.dq-window-1 { background-color: black; padding: 0.12rem; width: 100%; border-radius: 0.35rem; }
.dq-window-2 { background-color: white; padding: 0.16rem; border-radius: 0.25rem; }
.dq-window-3 { color: white; background-color: black; border-radius: 0.25rem; padding: 0.6rem 0.6rem; line-height: 1.5; font-family: var(--dq-font); font-weight: 800; }

/* ダメージテキスト */
.dq-damage { color: #ffffff; font-family: var(--dq-font); font-weight: 900; font-size: clamp(16px, 2.2vh, 22px); text-shadow: 2px 2px 0 #000; animation: dq-float 1.0s ease forwards; text-align: center; }
@keyframes dq-float { 0% { transform: translateY(0px); opacity: 1; } 50% { transform: translateY(-14px); opacity: 1; } 100% { transform: translateY(-28px); opacity: 0; } }

/* 区切り線 */
hr, [data-testid="stDivider"] { border: 2px solid #ffffff !important; margin: .6rem 0 !important; }

/* ステータス：アイコン領域をフレックスにして省スペース */
.dq-status { background: transparent; margin: .35rem 0; }
.dq-status-wrap { display: flex; align-items: center; gap: .5rem; }
.dq-character { text-align: center; font-size: 1.6rem; margin: 0; }
.dq-character-img { width: 40px; height: 40px; image-rendering: pixelated; filter: grayscale(1) brightness(1.2) contrast(1.2); }

/* メッセージの▼マーク（白） */
.dq-continue { text-align: center; color: #fff; font-size: 16px; animation: blink 1.2s infinite; margin-top: 0.25rem; }
@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0.35; } }
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
    questions = load_questions()
    if not questions:
        st.error("問題が読み込めませんでした。ゲームを開始できません。")
        return
    n = len(questions)
    # 問題数に応じてHPをスケーリング（基準=40問、40未満でも下げない）
    hp_scale = max(1.0, n / BASELINE_QUESTIONS) * EXTRA_HP_SCALE
    player_hp = int(round(PLAYER_BASE_HP * hp_scale))
    boss_hp = int(round(BOSS_BASE_HP * hp_scale))

    st.session_state.player = Fighter("勇者", max_hp=player_hp, atk=PLAYER_ATK)
    st.session_state.boss   = Fighter("タイポ魔王", max_hp=boss_hp, atk=BOSS_ATK)
    pool = questions[:]
    random.shuffle(pool)
    st.session_state.qs = pool
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.streak = 0    # 連続正解でクリティカル
    st.session_state.last = None   # ("correct"/"wrong", 正解番号, 解説)
    st.session_state.state = "asking"

def dq_hp_bar(name: str, current: int, maximum: int, character: str, icon_path: str | None = None):
    """ドラクエ風HPバー表示（3層構造）"""
    pct = max(0, min(1, current/maximum))
    width = f"{pct*100:.1f}%"

    # HP割合に応じて色を変更（ドラクエ風）
    # モノクロでも識別できるように白濃淡（ただしHPバーだけは視認性重視で灰～白）
    if pct > 0.6:
        hp_color = "#e6e6e6"  # 明るい灰
    elif pct > 0.3:
        hp_color = "#bfbfbf"  # 中間灰
    else:
        hp_color = "#808080"  # 濃い灰

    # アイコン（任意のPNGがあれば使用、なければ絵文字）
    img_html = ""
    if icon_path and os.path.exists(icon_path):
        img_html = f'<img class="dq-character-img" src="{icon_path}" alt="{name}">'

    html = f"""
    <div class="dq-status">
        <div class="dq-status-wrap">
            {img_html if img_html else f'<div class="dq-character">{character}</div>'}
            <div style="flex:1">
                <div class="dq-window-1">
                    <div class="dq-window-2">
                        <div class="dq-window-3" style="text-align: center; margin: 0; padding: 0.35rem;">
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
st.markdown("## CBTクエスト")
# st.caption("正解で攻撃 / 不正解で被弾。3連続正解で会心！")

# リセット（本物のボタンをDQ風にスタイル）
if st.button("🔄 冒険をやり直す", key="reset_btn", use_container_width=True):
    init_game()
    st.rerun()

# HPバー（ドラクエ風）
c1, c2 = st.columns(2)
with c1:
    dq_hp_bar("勇者", player.hp, player.max_hp, "🧙‍♂️", icon_path="assets/player.png")
with c2:
    dq_hp_bar("タイポ魔王", boss.hp, boss.max_hp, "👾", icon_path="assets/boss.png")

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

html = f"""
<div class=\"dq-window-1\">
  <div class=\"dq-window-2\">
    <div class=\"dq-window-3\">
      <div style=\"display:flex; justify-content:space-between; align-items:center; margin-bottom:.35rem;\">
        <span>ターン {idx+1}</span>
        <span><strong>[Unit {q['unit']}] {q['topic']}</strong></span>
      </div>
      <div>{q['q']}</div>
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
    # ドラクエ風の本物のボタン
    if st.button("⚔️ たたかう", key="battle_btn", disabled=disabled, use_container_width=True):
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
        dq_message_box(f"正解！ {crit_msg}{boss.name}に {amount} のダメージ！", "🗡️ 攻撃成功")
        dq_damage_text(f"-{amount}", True)
        if crit:
            st.toast("💥 会心の一撃！", icon="🔥")
    else:
        dq_message_box(f"不正解… {boss.name}の反撃！ {amount} のダメージ…", "💀 被弾")

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

    # 次へ（本物のボタン）
    if st.button("▶ つぎへ", key="next_btn", use_container_width=True):
        st.session_state.idx += 1
        st.session_state.state = "finished" if end else "asking"
        st.rerun()
