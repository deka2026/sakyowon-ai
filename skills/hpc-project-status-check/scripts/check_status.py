#!/usr/bin/env python3
"""NIPA HPC project status check: frontend, backend AI route, engine, dashboard.

Read-only. Standard library only. Prints a markdown table.

Usage:
    python check_status.py                 # full check
    python check_status.py --no-dashboard  # skip nexus dashboard scrape
    python check_status.py --json          # machine-readable

Exit code 0 always (this is a report, not a gate). Look at the table.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HATSOJA = "https://sakyowon.co.kr/hatsoja/"
AI_CHAT = "https://sakyowon.co.kr/api/ai/chat"
ENGINE_STATUS = "https://chat.solarshare.kr/api/status"
ENGINE_HEALTH = "https://chat.solarshare.kr/api/v1/health"
DASHBOARD = "https://nexus.poomasi.org/"
TIMEOUT = 15


# Cloudflare fronts the engine and dashboard and rejects the default urllib
# user agent with error 1010 (HTTP 403). curl passes; so does a browser UA.
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) hpc-status-check/1.0"


def get(url, data=None, headers=None):
    h = {"User-Agent": UA}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:  # network, dns, timeout
        return 0, {}, str(e).encode()


def strip_html(b):
    s = b.decode("utf-8", "ignore")
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s)


def check_frontend():
    code, hdr, body = get(HATSOJA)
    html = body.decode("utf-8", "ignore") if code == 200 else ""
    return {
        "status": code,
        "last_modified": hdr.get("Last-Modified", ""),
        "size_kb": round(len(body) / 1024) if code == 200 else 0,
        "calls_api_ai": len(re.findall(r"api/ai(?![a-z/])", html)),
        "calls_api_ai_chat": len(re.findall(r"api/ai/chat", html)),
        "calls_api_v1": len(re.findall(r"/api/v1/", html)),
    }


def check_backend_ai():
    payload = json.dumps({"prompt": "ping", "history": []}).encode()
    code, _, body = get(AI_CHAT, data=payload, headers={"content-type": "application/json"})
    text = body.decode("utf-8", "ignore")[:300]
    if "SAKYOWON_ANTHROPIC_KEY" in text or "연결되지 않았" in text:
        state = "NOT_CONNECTED (no key / bad key — message says why)"
    elif code == 500:
        # Seen 2026-09-20~23: env held a non-ASCII placeholder for the Anthropic key and the
        # server still ran code older than commit 1d2b1db (which turns this into a message).
        state = "SERVER_ERROR 500 (likely bad key value + old server code; pull main & fix env)"
    elif code == 200 and '"answer"' in text:
        state = "ANSWERING"
    else:
        state = f"UNEXPECTED ({code})"
    backend = re.search(r'"backend"\s*:\s*"([^"]+)"', text)
    # adapter deployed? (feat/poome-engine-adapter adds GET /api/ai/health)
    hcode, _, hbody = get(AI_CHAT.rsplit("/", 1)[0] + "/health")
    adapter = "deployed" if hcode == 200 else f"not deployed ({hcode})"
    return {"status": code, "state": state, "backend_field": backend.group(1) if backend else "(none)",
            "adapter": adapter, "adapter_body": hbody.decode("utf-8", "ignore")[:160]}


def check_engine():
    code_s, _, body_s = get(ENGINE_STATUS)
    code_h, _, body_h = get(ENGINE_HEALTH)
    return {
        "status_endpoint": code_s,
        "status_body": body_s.decode("utf-8", "ignore")[:120],
        "v1_health": code_h,
        "v1_health_body": body_h.decode("utf-8", "ignore")[:120],
    }


def check_dashboard():
    code, _, body = get(DASHBOARD)
    if code != 200:
        return {"status": code}
    t = strip_html(body)

    def grab(pattern, default=""):
        m = re.search(pattern, t)
        return m.group(1).strip() if m else default

    return {
        "status": code,
        "as_of": grab(r"기준일:\s*([0-9-]+)"),
        # 9/23 개편 문구: "실부하 GPU Util 15.9%" (6/27판은 "~8% GPU Util 평균")
        "gpu_util_avg": grab(r"실부하 GPU Util\s*([\d.]+%)") or grab(r"~?([\d.]+%)\s*GPU Util 평균"),
        "reclaim_incidents": grab(r"회수 사고\s*(\d+)회"),
        "accuracy": grab(r"공고문 질의 정답률[^%]*?([\d.]+%)"),
        "dataset": grab(r"인스트럭션 데이터셋[^0-9]*([\d,]+건)"),
        "pilot_villages": grab(r"실증 마을[^0-9]*(\d+개)"),
        "v1_api_mentioned": "/api/v1" in t,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-dashboard", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    out = {
        "frontend": check_frontend(),
        "backend_ai": check_backend_ai(),
        "engine": check_engine(),
    }
    if not a.no_dashboard:
        out["dashboard"] = check_dashboard()

    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    f, b, e = out["frontend"], out["backend_ai"], out["engine"]
    rows = [
        ("hatsoja front", f"{f['status']} · {f['size_kb']}KB · {f['last_modified']}"),
        ("front AI calls", f"/api/ai x{f['calls_api_ai']} · /api/ai/chat x{f['calls_api_ai_chat']} · /api/v1 x{f['calls_api_v1']}"),
        ("backend /api/ai/chat", f"{b['state']} · backend={b['backend_field']}"),
        ("engine adapter on server", f"{b['adapter']} · {b['adapter_body']}"),
        ("engine /api/status", f"{e['status_endpoint']} · {e['status_body']}"),
        ("engine /api/v1/health", f"{e['v1_health']} · {e['v1_health_body']}"),
    ]
    if "dashboard" in out:
        d = out["dashboard"]
        if d.get("status") == 200:
            rows += [
                ("dashboard as-of", d["as_of"] or "(not found)"),
                ("GPU util avg", d["gpu_util_avg"] or "(not found)"),
                ("reclaim incidents", d["reclaim_incidents"] or "(not found)"),
                ("accuracy", d["accuracy"] or "(not found)"),
                ("dataset", d["dataset"] or "(not found)"),
                ("pilot villages", d["pilot_villages"] or "(not found)"),
            ]
        else:
            rows.append(("dashboard", f"HTTP {d.get('status')}"))

    print("| item | value |\n|---|---|")
    for k, v in rows:
        print(f"| {k} | {v} |")

    # one-line verdict — 어댑터 health(backend:poome, ok:true)와 상담 응답의 backend 값으로 판정
    ah = b.get("adapter_body", "")
    adapter_on = '"backend":"poome"' in ah.replace(" ", "") and '"ok":true' in ah.replace(" ", "")
    chat_engine = b["state"] == "ANSWERING" and b["backend_field"] not in ("(none)", "anthropic", "none")
    print()
    if adapter_on and chat_engine:
        print(f"VERDICT: hatsoja chat tab LINKED to HPC engine (backend={b['backend_field']})")
    elif adapter_on:
        print("VERDICT: adapter ON but chat answered by non-engine backend — check POOME_API_KEY / engine 5xx")
    else:
        print("VERDICT: hatsoja NOT linked to HPC engine"
              + ("" if e["v1_health"] == 200 else " (engine /api/v1/health not up)")
              + ("" if b["state"] == "ANSWERING" else " (backend AI not answering)")
              + (" (adapter deployed, POOME_API_BASE unset)" if b.get("adapter", "").startswith("deployed") else ""))


if __name__ == "__main__":
    main()
