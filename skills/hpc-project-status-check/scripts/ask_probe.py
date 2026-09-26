"""햇소자 상담 경로(/api/ai/chat → GPU 엔진)에 질문을 UTF-8로 N회씩 보내 답함/근거없음을 센다.

Git Bash의 curl은 한글을 CP949로 보내 엔진이 깨진 질문을 받는다(9/25 오진). 시험 호출은 이 스크립트로.

  python ask_probe.py --live-presets            # 라이브 햇소자 #/mem/ask 예시 질문 전부
  python ask_probe.py -q "질문1" -q "질문2" -n 3
  python ask_probe.py --live-presets --json     # 편지함·서면용
"""
import argparse, io, json, re, sys, time, urllib.request

BASE = "https://sakyowon.co.kr"
CTX = ("햇소자(햇빛소득마을 통합 운영 플랫폼) 이용자 상담 — 마을협동조합 설립·운영·발전사업"
       " (사용자가 직전에 보던 화면: GPU 엔진 질문 모음)")


def live_presets():
    h = urllib.request.urlopen(f"{BASE}/hatsoja/index.html?v={int(time.time())}", timeout=30).read().decode("utf-8")
    blk = h[h.index("const ASK_GROUPS"):h.index("function memAsk")]
    return re.findall(r"^\s+'([^']+)',$", blk, re.M)


def ask(q, ctx):
    body = json.dumps({"prompt": q, "history": [], "context": ctx}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/ai/chat", body, {"Content-Type": "application/json; charset=utf-8"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=120))
    except Exception as e:
        return {"ok": False, "err": str(e)[:80], "sources": 0, "request_id": None, "backend": None}
    return {"ok": not d.get("insufficient"), "sources": len(d.get("sources") or []),
            "request_id": d.get("request_id"), "backend": d.get("backend")}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", action="append", default=[], help="질문 (여러 번)")
    ap.add_argument("--live-presets", action="store_true", help="라이브 #/mem/ask 예시 질문")
    ap.add_argument("-n", type=int, default=1, help="질문당 반복 횟수")
    ap.add_argument("--context", default=CTX)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    qs = (live_presets() if a.live_presets else []) + a.q
    if not qs:
        ap.error("질문이 없다: -q 또는 --live-presets")
    rows, tot = [], 0
    for q in qs:
        rs = [ask(q, a.context) for _ in range(a.n)]
        c = sum(r["ok"] for r in rs)
        tot += c
        rows.append({"question": q, "answered": c, "runs": rs})
        if not a.json:
            ids = " ".join(("O" if r["ok"] else "x") + f":{r['request_id']}" for r in rs)
            print(f"{c}/{a.n} src={max(r['sources'] for r in rs):2} {ids} | {q[:40]}")
    if a.json:
        print(json.dumps({"total": tot, "of": len(qs) * a.n, "rows": rows}, ensure_ascii=False, indent=1))
    else:
        print(f"TOTAL {tot}/{len(qs) * a.n}  backend={rows[0]['runs'][0]['backend']}")


if __name__ == "__main__":
    main()
