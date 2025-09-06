import json
import random
import streamlit as st
from dataclasses import dataclass

# ====== ページ設定 ======
st.set_page_config(page_title="川田の冒険：CBTクイズRPG", page_icon="🗡️", layout="centered")

# ====== ダークUI用CSS ======
DARK_CSS = """
<style>
/* 背景：ダーク＋グラデーション */
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 20% 0%, #1d1f2a 0%, #0f1117 60%, #0b0d12 100%) !important;
  color: #e2e8f0 !important;
  font-weight: 480;
}

/* 見出し */
h1, h2, h3, h4, h5 {
  color: #f8fafc !important;
  letter-spacing: .02em;
}

/* カード/メッセージのコントラスト */
.block-container { padding-top: 2rem !important; }
.stAlert {
  background: rgba(25, 30, 45, .65) !important;
  border: 1px solid rgba(148,163,184,.25) !important;
  border-radius: 12px !important;
}

/* ラジオ・ボタン */
[data-testid="stRadio"] label {
  background: rgba(148,163,184,.08);
  border: 1px solid rgba(148,163,184,.18);
  border-radius: 10px;
  padding: .45rem .7rem;
  margin-bottom: .35rem;
}
button[kind="primary"] {
  border-radius: 10px !important;
  border: 1px solid rgba(148,163,184,.25) !important;
}

/* HPバー（カスタム） */
.rpgbar {
  width: 100%;
  background: linear-gradient(90deg, rgba(148,163,184,.12), rgba(148,163,184,.05));
  border: 1px solid rgba(148,163,184,.25);
  border-radius: 10px;
  height: 20px;
  position: relative;
  overflow: hidden;
}
.rpgbar-fill {
  height: 100%;
  border-radius: 10px;
  background: linear-gradient(90deg, var(--c1), var(--c2));
  box-shadow: 0 0 12px var(--c2, #22c55e88);
  width: var(--w, 100%);
  transition: width .45s ease;
}
.rpgbar-gloss {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, rgba(255,255,255,.18), rgba(255,255,255,0));
  mix-blend-mode: soft-light;
}

/* ダメージ/ヒールの浮遊テキスト */
.float-dmg {
  color: #fca5a5; font-weight: 700;
  text-shadow: 0 0 8px rgba(220,38,38,.75);
  animation: rise 900ms ease forwards;
}
.float-heal {
  color: #86efac; font-weight: 700;
  text-shadow: 0 0 8px rgba(34,197,94,.7);
  animation: rise 900ms ease forwards;
}
@keyframes rise {
  from { transform: translateY(0); opacity: .0; }
  to   { transform: translateY(-18px); opacity: 1; }
}

/* 区切り線を控えめに */
hr, [data-testid="stDivider"] {
  border-color: rgba(148,163,184,.2) !important;
}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

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
    st.session_state.player = Fighter("あなた", max_hp=120, atk=20)
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

def hp_bar(label: str, current: int, maximum: int, color1: str, color2: str):
    pct = max(0, min(1, current/maximum))
    width = f"{pct*100:.1f}%"
    html = f"""
      <div style="margin-bottom:.25rem;font-weight:700">{label}: {current} / {maximum}</div>
      <div class="rpgbar">
        <div class="rpgbar-fill" style="--w:{width}; --c1:{color1}; --c2:{color2};"></div>
        <div class="rpgbar-gloss"></div>
      </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def float_text(text: str, kind: str = "dmg"):
    cls = "float-dmg" if kind == "dmg" else "float-heal"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)

# ====== 初期化 ======
if "qs" not in st.session_state:
    init_game()

player = st.session_state.player
boss = st.session_state.boss

# ====== ヘッダ ======
st.markdown("## 🗡️ 川田の冒険：CBTクイズRPG")
st.caption("正解で攻撃 / 不正解で被弾。3連続正解で **クリティカル**！")

# リセット
colA, colB = st.columns([1,1])
with colA:
    if st.button("🔄 ゲームをリセット", use_container_width=True):
        init_game()
        st.rerun()

# HPバー（ダーク仕様）
c1, c2 = st.columns(2)
with c1:
    hp_bar("🧙 あなた", player.hp, player.max_hp, "#22c55e", "#16a34a")  # 緑系
with c2:
    hp_bar("👾 タイポ魔王", boss.hp, boss.max_hp, "#ef4444", "#b91c1c")   # 赤系

st.divider()

# ====== ゲーム終了判定 ======
if st.session_state.state == "finished":
    if boss.alive() and not player.alive():
        st.error("❌ あなたは倒れてしまった… 期末までにもうひと踏ん張り！")
        st.snow()  # 敗北エフェクト（雪を悲壮感に見立てる）
    elif player.alive() and not boss.alive():
        st.success("🏆 勝利！ タイポ魔王は霧散した。『愚直にやるしかないっすよ』の勝利だ！")
        st.balloons()  # 勝利演出
    else:
        if boss.hp < player.hp:
            st.info("⌛ 時間切れだが優勢！よく戦った！")
        else:
            st.warning("⌛ 時間切れで痛み分け。復習して再挑戦！")
    st.metric("スコア", f"{st.session_state.score} / {len(st.session_state.qs)}")
    st.stop()

# ====== 出題 ======
idx = st.session_state.idx
if idx >= len(st.session_state.qs):
    st.session_state.state = "finished"
    st.rerun()

q = st.session_state.qs[idx]

st.subheader(f"ターン {idx+1}")
st.write(f"**[Unit {q['unit']}] {q['topic']}**")
st.write(q["q"])

choice = st.radio(
    "選択肢を選んでください",
    options=[f"{i+1}) {c}" for i, c in enumerate(q["choices"])],
    index=None,
    label_visibility="collapsed"
)

# ====== 判定 ======
if st.session_state.state == "asking":
    disabled = choice is None
    if st.button("⚔️ 判定する", type="primary", disabled=disabled, use_container_width=True):
        picked = None if choice is None else int(choice.split(")")[0])
        if picked == q["a"]:
            # 連続正解判定（3連続でクリティカル）
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
        msg = f"✅ 正解！ {('💥 クリティカル！ ' if crit else '')}{boss.name}に **{amount}** ダメージ！ 残HP: {max(boss.hp,0)}"
        st.success(msg)
        float_text(f"-{amount}", "dmg")
        if crit:
            st.toast("💥 クリティカルヒット！", icon="🔥")
    else:
        st.error(f"❌ 不正解… {boss.name}の反撃！ あなたは **{amount}** ダメージ。残HP: {max(player.hp,0)}")
        st.info(f"正解は {ans_idx}) {q['choices'][ans_idx-1]}")
        if exp: st.caption(f"補足：{exp}")
        float_text(f"-{amount}", "dmg")

    # 終了チェック
    end = (not player.alive()) or (not boss.alive())

    if st.button("▶ 次へ", use_container_width=True):
        st.session_state.idx += 1
        st.session_state.state = "finished" if end else "asking"
        st.rerun()
