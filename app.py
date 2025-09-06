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

# ====== データ ======
QUESTIONS = [
    {"unit":1,"topic":"5大装置","q":"コンピュータの5大装置に含まれないものは？",
     "choices":["制御装置","演算装置","入出力装置","冷却装置"],"a":4,
     "exp":"5大装置は制御・演算・記憶・入力・出力。冷却装置は含まれない。"},
    {"unit":2,"topic":"HTTP","q":"ブラウザ→サーバで送るのはどれ？",
     "choices":["HTML","HTTPリクエスト","HTTPレスポンス","CSS"],"a":2,"exp":"クライアントはリクエスト、サーバはレスポンス。"},
    {"unit":3,"topic":"2進数","q":"10進数の13を2進数にすると？",
     "choices":["1011","1101","1110","1001"],"a":2,"exp":"13(10)=1101(2)。"},
    {"unit":4,"topic":"フローチャート","q":"条件分岐を表す図形は？",
     "choices":["長方形","平行四辺形","ひし形","円"],"a":3,"exp":"判定はひし形。"},
    {"unit":5,"topic":"DX","q":"DXの説明として最も適切なのは？",
     "choices":["紙をPDF化すること","最新AIを購入すること","デジタルで業務・事業を変革","SNS運用を始めること"],"a":3,"exp":"DX=ビジネス変革。"},
    {"unit":6,"topic":"DXメリット","q":"DXの主なメリットは？",
     "choices":["固定費の増加","意思決定の遅延","データ活用で効率化","紙文化の強化"],"a":3,"exp":"効率化・迅速化。"},
    {"unit":7,"topic":"Linuxとは","q":"Linuxの説明として正しいのは？",
     "choices":["商用OS(マイクロソフト)","オープンソースのUNIX系OS","スマホ専用OS","ブラウザの一種"],"a":2,"exp":"OSSのUNIX系OS。"},
    {"unit":8,"topic":"用途","q":"Linuxが広く使われる用途は？",
     "choices":["家電組込み・サーバ","ワープロ専用機","携帯電話のみ","ゲーム機だけ"],"a":1,"exp":"サーバや組込み。"},
    {"unit":9,"topic":"mv","q":"ファイル名を変更するコマンドは？",
     "choices":["cp","mv","rm","cat"],"a":2,"exp":"mv A B でリネーム。"},
    {"unit":10,"topic":"ディレクトリ削除","q":"空でないディレクトリを削除するコマンドは？",
     "choices":["rm -r dir","rm dir","mv dir /dev/null","delete dir"],"a":1,"exp":"再帰削除は rm -r。"},
    {"unit":11,"topic":"RDB","q":"関係データベースの特徴は？",
     "choices":["木構造のみ","テーブル（行・列）で表現","SQLは使えない","画像専用"],"a":2,"exp":"表とSQLが基本。"},
    {"unit":12,"topic":"更新","q":"既存行の値を変更するSQLは？",
     "choices":["INSERT","UPDATE","DELETE","SELECT"],"a":2,"exp":"UPDATE が更新。"},
    {"unit":13,"topic":"並び替え","q":"SQLで並び替えに使う句は？",
     "choices":["GROUP BY","ORDER BY","WHERE","HAVING"],"a":2,"exp":"ORDER BY。"},
    {"unit":14,"topic":"結合","q":"共通キーで行を組み合わせる基本結合は？",
     "choices":["INNER JOIN","CROSS JOINのみ","FULL JOINのみ","SELF JOINのみ"],"a":1,"exp":"基本は INNER JOIN。"},
    {"unit":15,"topic":"技術","q":"クラウド実現の中核技術は？",
     "choices":["仮想化","手作業運用","磁気テープ","真空管"],"a":1,"exp":"仮想化・自動化。"},
    {"unit":16,"topic":"優位点","q":"クラウドの優位点として適切なのは？",
     "choices":["初期投資の増大","弾力的スケール","オンプレ固定資産化","保守の手作業化"],"a":2,"exp":"必要時にスケール。"},
    {"unit":17,"topic":"AWS名","q":"Amazonのクラウドサービス名称は？",
     "choices":["Azure","GCP","AWS","Salesforce"],"a":3,"exp":"Amazon Web Services。"},
    {"unit":18,"topic":"サーバ","q":"AWSで仮想サーバに相当するサービスは？",
     "choices":["EC2","S3","RDS","Lambda"],"a":1,"exp":"VMはEC2。"},
    {"unit":19,"topic":"終了","q":"EC2を完全に消す操作は？",
     "choices":["Stop","Reboot","Hibernate","Terminate"],"a":4,"exp":"Terminateで破棄。"},
    {"unit":20,"topic":"S3","q":"S3の特徴は？",
     "choices":["ブロック","ファイル","オブジェクト","メモリ"],"a":3,"exp":"S3=オブジェクト。"},
    {"unit":21,"topic":"C変数","q":"Cでint aを10で初期化する宣言は？",
     "choices":["int a = 10;","int a := 10;","var a = 10;","let a = 10;"],"a":1,"exp":"int a = 10;"},
    {"unit":22,"topic":"C配列","q":"Cで要素5のint配列の宣言は？",
     "choices":["int a(5);","int a[5];","array<int> a(5);","int[5] a;"],"a":2,"exp":"型 名[要素数]。"},
    {"unit":23,"topic":"C for","q":"Cのfor文は？",
     "choices":["for i=0 to 9","for(i=0;i<10;i++)","for i in range(10)","foreach i in 10"],"a":2,"exp":"for(init;cond;post)"},
    {"unit":24,"topic":"プロトタイプ","q":"Cのプロトタイプ宣言の例は？",
     "choices":["int f(x);","int f(int);","def f(int x);","function f(int);"],"a":2,"exp":"戻り値 型名(引数型);"},
    {"unit":25,"topic":"センサー","q":"水耕栽培に有用なのは？",
     "choices":["加速度","水位/湿度","ジャイロ","照度のみ"],"a":2,"exp":"水位・湿度・温度など。"},
    {"unit":26,"topic":"電波","q":"IoTで近距離低電力として広く使われるのは？",
     "choices":["BLE","有線LAN","5Gのみ","赤外線のみ"],"a":1,"exp":"Bluetooth Low Energy。"},
    {"unit":27,"topic":"コンパイル","q":"LinuxでCをコンパイルするコマンドは？",
     "choices":["make only","gcc","ls","run"],"a":2,"exp":"gcc main.c -o main。"},
    {"unit":28,"topic":"GPIO","q":"Raspberry Pi OSでGPIOのモード切替に使うのは？",
     "choices":["wiringPi/gpio","DirectX","OpenGL","CUDA"],"a":1,"exp":"wiringPi, RPi.GPIO など。"},
    {"unit":29,"topic":"if","q":"Pythonのif文で正しいのは？",
     "choices":["if x > 0:","if (x > 0) then","if x > 0 then:","if x > 0 {}"],"a":1,"exp":"コロン＋インデント。"},
    {"unit":30,"topic":"for","q":"Pythonで0〜4を繰り返すのは？",
     "choices":["for i in 0..4:","for (i=0;i<5;i++):","for i in range(5):","foreach 0..4 as i:"],"a":3,"exp":"range(5)。"},
    {"unit":31,"topic":"関数","q":"xを1増やす関数定義は？",
     "choices":["def f(x): return x+1","function f(x){return x+1}","def f(x) { x+1 }","let f = x+1"],"a":1,"exp":"def f(x): return x+1"},
    {"unit":32,"topic":"コレクション","q":"リスト末尾に要素を追加するメソッドは？",
     "choices":["push","append","add","insert_end"],"a":2,"exp":"list.append。"},
    {"unit":33,"topic":"標準偏差","q":"標準偏差は何の平方根？",
     "choices":["相関係数","分散","平均","中央値"],"a":2,"exp":"√(分散)。"},
    {"unit":34,"topic":"回帰直線","q":"単回帰の回帰直線の一般形は？",
     "choices":["y=ax+b","x=by+a","xy=a+b","y=a/x+b"],"a":1,"exp":"y=ax+b。"},
    {"unit":35,"topic":"Excel関数","q":"Excelで相関係数を求める関数は？",
     "choices":["=VAR()","=STDEV()","=CORREL()","=SLOPE()"],"a":3,"exp":"CORREL。"},
    {"unit":36,"topic":"相関範囲","q":"相関係数の取りうる範囲は？",
     "choices":["0〜1","-1〜1","-∞〜∞","0〜100"],"a":2,"exp":"-1〜+1。"},
    {"unit":37,"topic":"ML流れ","q":"機械学習の一般的な流れで最初に来るのは？",
     "choices":["モデル学習","前処理","データ収集","評価"],"a":3,"exp":"収集→前処理→学習→評価。"},
    {"unit":38,"topic":"MLライブラリ","q":"MLでよく使われるPythonライブラリは？",
     "choices":["pandas, scikit-learn","NumPy以外不可","OpenGLのみ","Flaskのみ"],"a":1,"exp":"pandas, scikit-learn, NumPy等。"},
    {"unit":39,"topic":"DataFrame","q":"pandasで空のDataFrameを作るコードは？",
     "choices":["DataFrame()","pd.DataFrame()","pandas.frame()","np.dataframe()"],"a":2,"exp":"import pandas as pd; pd.DataFrame()"},
    {"unit":40,"topic":"fit","q":"scikit-learnで学習を実行するメソッドは？",
     "choices":["train()","fit()","learn()","run()"],"a":2,"exp":"学習は fit()、予測は predict()。"},
]

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
    pool = QUESTIONS[:]
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
