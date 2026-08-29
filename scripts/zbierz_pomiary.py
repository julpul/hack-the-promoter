#!/usr/bin/env python3
"""Zbiera wszystkie pomiary do data/pomiary.json -- zeby notebook byl szybki.

    python scripts/zbierz_pomiary.py            # pelny zbior
    python scripts/zbierz_pomiary.py --szybko   # pomija drogie eksperymenty

Cache jest deterministyczny (stale ziarna), wiec da sie odtworzyc.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hyppe import Client  # noqa: E402
from hyppe import fasta as F  # noqa: E402
from hyppe import seq as S  # noqa: E402
from hyppe.config import REPO_ROOT  # noqa: E402

WYJSCIE = REPO_ROOT / "data" / "pomiary.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--szybko", action="store_true")
    a = ap.parse_args()

    c = Client.from_env()
    dane: dict = {}

    print("[1/8] dziki + mapa")
    d = c.dziki()
    dziki = d["sekwencja"]
    dane["dziki"] = {"sekwencja": dziki, "meta": {k: v for k, v in d.items()
                                                  if k != "sekwencja"}}
    m = c.mapa(dziki, od=0, ile=800)
    dane["mapa"] = {
        "naglowek": {k: v for k, v in m.items() if k not in ("pozycje", "kompakt")},
        "pozycje": m["pozycje"],
    }

    print("[2/8] motywy w dzikim")
    dane["motywy"] = {n: S.znajdz_iupac(dziki, w) for n, w in S.MOTYWY.items()}

    print("[3/8] edycje: poziomy x ile_kodow")
    siatka = []
    for poziom in (0, 1, 2):
        for ile_kodow in (1, 2, 4, 8, 16):
            e = c.edycje(dziki, poziom=poziom, ile_kodow=ile_kodow, opcji=6, ziarno=5)
            for o in e["opcje"]:
                zmiany = S.rozne_pozycje(dziki, o["sekwencja"])
                siatka.append({
                    "poziom": poziom, "warstwa": e["warstwa"],
                    "slotow": e["slotow"], "alfabet": e["alfabet"],
                    "ile_kodow": ile_kodow, "nr": o["nr"],
                    "dystans": len(zmiany),
                    "pozycje_zmian": [p for p, _, _ in zmiany],
                    "blad_rekonstrukcji": e["blad_rekonstrukcji_pozycji"],
                })
            print(f"      poziom {poziom} ile_kodow {ile_kodow}: gotowe")
    dane["edycje_siatka"] = siatka

    print("[4/8] prog czulosci Sedziego -- losowe mutacje")
    titr = []
    for n in (1, 2, 5, 10, 20, 40, 80, 160, 320, 640):
        for z in range(8):
            w = S.mutuj(dziki, ile=n, ziarno=1000 * n + z)
            titr.append({"zmian": n, "proba": z, "bije": c.lepsza(dziki, w)})
        print(f"      {n} zmian: {sum(1 for t in titr if t['zmian']==n and t['bije'])}/8")
    dane["titracja_losowa"] = titr

    print("[5/8] warianty z dekodera vs dziki")
    dek = []
    for poziom in (0, 1, 2):
        e = c.edycje(dziki, poziom=poziom, ile_kodow=8, opcji=8, ziarno=77)
        for o in e["opcje"]:
            dek.append({
                "poziom": poziom,
                "dystans": S.hamming(dziki, o["sekwencja"]),
                "bije": c.lepsza(dziki, o["sekwencja"]),
            })
    print(f"      dekoder bije dzikiego: {sum(1 for x in dek if x['bije'])}/{len(dek)}")
    dane["dekoder_vs_dziki"] = dek

    print("[6/8] iteracyjne dopasowanie gatunkowe (hipoteza priorytetowa)")
    iteracje, biezaca = [], dziki
    for krok in range(8):
        mm = c.mapa(biezaca, od=0, ile=800)
        rek = [w for w in mm["pozycje"] if w["zmien_na"] != "."]
        iteracje.append({
            "krok": krok,
            "rekomendacji": len(rek),
            "dystans_od_dzikiego": S.hamming(dziki, biezaca),
            "bije_dzikiego": c.lepsza(dziki, biezaca) if krok else False,
            "pozycje_rekomendacji": [w["poz"] for w in rek],
            "sekwencja": biezaca,
        })
        print(f"      krok {krok}: {len(rek)} rekomendacji, "
              f"dystans {iteracje[-1]['dystans_od_dzikiego']}, "
              f"bije={iteracje[-1]['bije_dzikiego']}")
        if not rek:
            break
        biezaca = c.zastosuj_rekomendacje(biezaca, mm)
    dane["gatunkowa_iteracja"] = iteracje

    if not a.szybko:
        print("[7/8] wspinaczka po kodach latentu (iterowana ewolucja)")
        wspin, baza_w, przyjete = [], dziki, 0
        for krok in range(1, 21):
            e = c.edycje(baza_w, poziom=2, ile_kodow=6, opcji=6, ziarno=krok)
            najlepszy = None
            for o in e["opcje"]:
                if c.lepsza(baza_w, o["sekwencja"]):
                    najlepszy = o["sekwencja"]
                    break
            if najlepszy:
                baza_w = najlepszy
                przyjete += 1
            wspin.append({
                "krok": krok, "przyjeto": bool(najlepszy),
                "dystans_od_dzikiego": S.hamming(dziki, baza_w),
                "bije_dzikiego": c.lepsza(dziki, baza_w),
                "przyjetych_lacznie": przyjete,
            })
            print(f"      krok {krok:2d}: {'PRZYJETO' if najlepszy else 'odrzucono'}"
                  f"  dystans {wspin[-1]['dystans_od_dzikiego']}"
                  f"  bije_dzikiego={wspin[-1]['bije_dzikiego']}")
        dane["wspinaczka"] = wspin
        dane["wspinaczka_wynik"] = baza_w
    else:
        dane["wspinaczka"] = []

    print("[8/8] nasza wgrana pula")
    p = REPO_ROOT / "runs" / "julian" / "pula.fasta"
    if p.exists():
        rek = F.czytaj(p)
        dane["pula"] = [{"nazwa": r.nazwa, "dystans": S.hamming(dziki, r.seq),
                         "gc": S.gc(r.seq),
                         "zmian_w_rdzeniu": sum(1 for i in range(782, 800)
                                                if r.seq[i] != dziki[i])}
                        for r in rek]
    else:
        dane["pula"] = []

    WYJSCIE.parent.mkdir(exist_ok=True)
    WYJSCIE.write_text(json.dumps(dane, ensure_ascii=False), encoding="utf-8")
    print(f"\nzapisano {WYJSCIE} ({WYJSCIE.stat().st_size // 1024} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
