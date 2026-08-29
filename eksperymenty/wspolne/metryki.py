"""Ekstrakcja skalarow z odpowiedzi /nawigator/mapa.

Podzial na trzy klasy, bo tylko jedna z nich nadaje sie na funkcje celu:

BEZWZGLEDNE (kandydaci na funkcje celu -- hipoteza W9, weryfikuje E01)
    zmian_pod_gatunek   ile pozycji kanal gatunku chce jeszcze zmienic pod P1
    blad_odtworzenia    bezwzgledny blad rekonstrukcji tej sekwencji
    nie_rekonstruuje    ile pozycji nie odtwarza sie z samych kodow
    rekon_frakcja       udzial pozycji odtwarzanych
    dzwignie_*          rozklad liczby warstw na pozycje
  Legenda API zastrzega nieporownywalnosc WYLACZNIE dla `wagaP`, wiec te pola
  moga byc porownywalne miedzy sekwencjami. To wlasnie sprawdza E01.

WZGLEDNE (uzyteczne tylko wewnatrz jednej sekwencji)
    wagaP na pozycji    min-max w tej sekwencji -> nie porownywac wprost

NIEZMIENNIKI ROZKLADU (proba obejscia normalizacji min-max)
    masa_rdzenia        udzial sumy wagaP w oknie 783-800 w calej sumie
    srodek_masy         centroid rozkladu wagaP wzdluz sekwencji
    argmax              pozycja maksimum
  Sa to ILORAZY wielkosci znormalizowanych tak samo, wiec skala sie skraca.
  Nie jest to dowod porownywalnosci, ale jest to najlepszy dostepny kandydat
  na niezmiennik -- i dokladnie o to pyta otwarte pytanie 11 z briefu.
  `srodek_masy` jest glowna metryka eksperymentu E02.
"""

from __future__ import annotations

RDZEN_OD = 783
RDZEN_DO = 800

POLA_NAGLOWKA = (
    "zmian_pod_gatunek",
    "blad_odtworzenia",
    "nie_rekonstruuje",
    "rekon_frakcja",
)


def srodek_masy(wagi: list[float]) -> float:
    """Centroid rozkladu wzdluz sekwencji, w pozycjach 1-based.

    Dla rozkladu plaskiego wynosi ~400,5. Dla dzikiego, gdzie 32 % masy siedzi
    w oknie 783-800, jest silnie przesuniety w prawo. To jedna liczba mowiaca
    "gdzie model patrzy" i -- w przeciwienstwie do surowej wagaP -- da sie ja
    porownywac miedzy sekwencjami, bo min-max skraca sie w ilorazie.
    """
    s = sum(wagi)
    if s <= 0:
        return float("nan")
    return sum((i + 1) * w for i, w in enumerate(wagi)) / s


def metryki_mapy(odp: dict, *, rdzen_od: int = RDZEN_OD, rdzen_do: int = RDZEN_DO) -> dict:
    """Splaszcza odpowiedz /nawigator/mapa do slownika skalarow."""
    # API zwraca pola naglowka na NAJWYZSZYM poziomie odpowiedzi, nie w podslowniku
    # "naglowek". Fallback na `odp` zostawiamy dla atrap w testach offline.
    nag = odp.get("naglowek") or odp
    poz = odp.get("pozycje", [])
    wagi = [p.get("wagaP", 0.0) for p in poz]
    n = len(wagi)

    out: dict = {k: nag.get(k) for k in POLA_NAGLOWKA}
    out["gatunek"] = nag.get("gatunek")
    out["gatunek_kod"] = nag.get("gatunek_kod")

    rozklad = nag.get("rozklad_warstw") or {}
    for k in ("0", "1", "2", "3"):
        out[f"dzwignie_{k}"] = rozklad.get(k)

    out["n_pozycji"] = n
    if not n:
        return out

    suma = sum(wagi)
    w_rdzeniu = sum(wagi[rdzen_od - 1: rdzen_do])
    out["suma_wagaP"] = round(suma, 4)
    out["srednia_wagaP"] = round(suma / n, 5)
    out["mediana_wagaP"] = round(sorted(wagi)[n // 2], 5)
    out["masa_rdzenia"] = round(w_rdzeniu / suma, 5) if suma else None
    out["srodek_masy"] = round(srodek_masy(wagi), 2)
    out["argmax"] = max(range(n), key=lambda i: wagi[i]) + 1

    # gdzie siedzi 40 najwiekszych wag -- odporniejsze na pojedynczy odstajacy szczyt
    top40 = sorted(range(n), key=lambda i: -wagi[i])[:40]
    out["srednia_pozycja_top40"] = round(sum(i + 1 for i in top40) / len(top40), 1)
    out["top40_w_rdzeniu"] = sum(1 for i in top40 if rdzen_od <= i + 1 <= rdzen_do)

    # rekomendacje gatunkowe: gdzie i ile
    rek = [p["poz"] for p in poz if p.get("zmien_na", ".") != "."]
    out["rekomendacji"] = len(rek)
    out["pozycje_rekomendacji"] = rek

    # pozycje swobodne i nadpisywane -- budzet edycji recznych
    out["swobodnych"] = sum(1 for p in poz if p.get("rekon") == 0)
    out["nadpisywanych"] = sum(
        1 for p in poz if p.get("rekon") == 1 and sum(p.get("warstwy", [])) == 0
    )
    return out


def profil_wagap(odp: dict) -> list[float]:
    return [p.get("wagaP", 0.0) for p in odp.get("pozycje", [])]


def wagi_w_oknach(wagi: list[float], szerokosc: int = 50) -> list[tuple[int, float]]:
    """[(poczatek_okna_1based, srednia_wagaP)] -- do wykresow slupkowych."""
    out = []
    for start in range(0, len(wagi), szerokosc):
        kawalek = wagi[start: start + szerokosc]
        out.append((start + 1, sum(kawalek) / len(kawalek)))
    return out
