"""FASTA: wczytywanie, zapis i walidacja wg regul serwera."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DLUGOSC = 800
ALFABET = set("ACGTN")
MAX_N_FRAKCJA = 0.10
LIMIT_OCENIANYCH = 100


@dataclass
class Rekord:
    nazwa: str
    seq: str


def czytaj(sciezka: Path | str) -> list[Rekord]:
    rekordy: list[Rekord] = []
    nazwa, kawalki = None, []
    for linia in Path(sciezka).read_text(encoding="utf-8").splitlines():
        linia = linia.strip()
        if not linia:
            continue
        if linia.startswith(">"):
            if nazwa is not None:
                rekordy.append(Rekord(nazwa, "".join(kawalki)))
            nazwa, kawalki = linia[1:].strip() or f"seq{len(rekordy) + 1}", []
        else:
            kawalki.append(linia.upper())
    if nazwa is not None:
        rekordy.append(Rekord(nazwa, "".join(kawalki)))
    return rekordy


def zapisz(sciezka: Path | str, rekordy: list[Rekord] | list[tuple[str, str]]) -> Path:
    sciezka = Path(sciezka)
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    linie = []
    for r in rekordy:
        nazwa, seq = (r.nazwa, r.seq) if isinstance(r, Rekord) else r
        linie += [">" + nazwa, seq]
    sciezka.write_text("\n".join(linie) + "\n", encoding="utf-8")
    return sciezka


def na_tekst(rekordy: list[Rekord] | list[tuple[str, str]]) -> str:
    linie = []
    for r in rekordy:
        nazwa, seq = (r.nazwa, r.seq) if isinstance(r, Rekord) else r
        linie += [">" + nazwa, seq]
    return "\n".join(linie)


def problemy(seq: str) -> list[str]:
    """Lista powodow, dla ktorych serwer pominalby te sekwencje."""
    bledy = []
    if len(seq) != DLUGOSC:
        bledy.append(f"dlugosc {len(seq)} != {DLUGOSC}")
    zle = sorted(set(seq.upper()) - ALFABET)
    if zle:
        bledy.append("znaki spoza ACGTN: " + ",".join(zle))
    if seq:
        udzial_n = seq.upper().count("N") / len(seq)
        if udzial_n > MAX_N_FRAKCJA:
            bledy.append(f"N = {udzial_n:.1%} > 10%")
    return bledy


@dataclass
class Raport:
    ok: list[Rekord]
    odrzucone: list[tuple[str, str]]  # (nazwa, powod)
    duplikaty: list[str]

    @property
    def ocenionych(self) -> int:
        return min(len(self.ok), LIMIT_OCENIANYCH)

    def podsumowanie(self) -> str:
        linie = [
            f"wczytanych OK   : {len(self.ok)}",
            f"do oceny        : {self.ocenionych} (limit {LIMIT_OCENIANYCH})",
            f"duplikaty       : {len(self.duplikaty)}",
            f"odrzucone       : {len(self.odrzucone)}",
        ]
        for nazwa, powod in self.odrzucone[:20]:
            linie.append(f"   - {nazwa}: {powod}")
        if len(self.odrzucone) > 20:
            linie.append(f"   ... i {len(self.odrzucone) - 20} wiecej")
        if len(self.ok) < LIMIT_OCENIANYCH:
            brak = LIMIT_OCENIANYCH - len(self.ok)
            linie.append(
                f"UWAGA: brakuje {brak} sekwencji do pelnych 100 "
                f"-> ALL100 traci ~{brak}% mozliwej puli (dzielnik jest staly)."
            )
        return "\n".join(linie)


def waliduj(rekordy: list[Rekord]) -> Raport:
    """Odtwarza filtry serwera: dlugosc, duplikaty, alfabet, udzial N."""
    ok: list[Rekord] = []
    odrzucone: list[tuple[str, str]] = []
    duplikaty: list[str] = []
    widziane: set[str] = set()
    for r in rekordy:
        seq = r.seq.upper()
        bledy = problemy(seq)
        if bledy:
            odrzucone.append((r.nazwa, "; ".join(bledy)))
            continue
        if seq in widziane:
            duplikaty.append(r.nazwa)
            continue
        widziane.add(seq)
        ok.append(Rekord(r.nazwa, seq))
    return Raport(ok=ok, odrzucone=odrzucone, duplikaty=duplikaty)
