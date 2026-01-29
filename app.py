from flask import Flask, render_template, request, jsonify
import difflib
import re

app = Flask(__name__)

# -----------------------------
# DATA KAMUS (contoh)
# Format: (bugis, indonesia)
# Kamu bisa tambah sebanyak yang kamu mau.
# -----------------------------
KAMUS = [
    ("iye", "ya"),
    ("tania", "tidak"),
    ("makanja", "enak/baik"),
    ("sipakatau", "saling memanusiakan"),
    ("mappasitinaja", "mengucapkan terima kasih"),
    ("sitinaja", "terima kasih"),
    ("assalamu alaikum", "salam"),
    ("waalaikumsalam", "balasan salam"),
    ("bajik", "baik"),
    ("malebbi", "sopan/beradab"),
    ("pake", "pakai"),
    ("riolo", "dulu"),
    ("rioloe", "yang dahulu"),
]

def normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text

def search_kamus(query: str, direction: str, max_results: int = 25):
    q = normalize(query)
    if not q:
        return []

    # arah pencarian
    if direction == "bugis->id":
        src_idx, tgt_idx = 0, 1
    else:
        src_idx, tgt_idx = 1, 0

    src_words = [normalize(row[src_idx]) for row in KAMUS]

    results = []
    seen = set()

    # 1) EXACT
    for i, src in enumerate(src_words):
        if src == q:
            bugis, indo = KAMUS[i]
            key = (bugis, indo)
            if key not in seen:
                seen.add(key)
                results.append({
                    "type": "EXACT",
                    "bugis": bugis,
                    "indo": indo
                })

    # 2) CONTAINS (substring)
    for i, src in enumerate(src_words):
        if q in src and src != q:
            bugis, indo = KAMUS[i]
            key = (bugis, indo)
            if key not in seen:
                seen.add(key)
                results.append({
                    "type": "CONTAINS",
                    "bugis": bugis,
                    "indo": indo
                })

    # 3) FUZZY (mendekati)
    close = difflib.get_close_matches(q, src_words, n=10, cutoff=0.6)
    for cand in close:
        i = src_words.index(cand)
        bugis, indo = KAMUS[i]
        key = (bugis, indo)
        if key not in seen:
            seen.add(key)
            results.append({
                "type": "FUZZY",
                "bugis": bugis,
                "indo": indo
            })

    return results[:max_results]

@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "")
    direction = request.args.get("direction", "bugis->id")
    results = search_kamus(q, direction) if q else []
    return render_template("index.html", q=q, direction=direction, results=results)

# Optional: endpoint JSON (kalau mau dipakai frontend / mobile)
@app.route("/api/search", methods=["GET"])
def api_search():
    q = request.args.get("q", "")
    direction = request.args.get("direction", "bugis->id")
    return jsonify({
        "query": q,
        "direction": direction,
        "results": search_kamus(q, direction)
    })

if __name__ == "__main__":
    # akses di http://127.0.0.1:5000
    app.run(debug=True)
