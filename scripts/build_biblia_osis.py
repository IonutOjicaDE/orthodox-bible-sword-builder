#!/usr/bin/env python3
"""Generate a single OSIS Bible document from the Romanian OT and NT UTF-8 text files.

This script is designed for both local use and GitHub Actions. It has no external
Python dependencies and exits with a non-zero status when conversion fails.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

CHAPTER_HEADER_RE = re.compile(r"^(.*?),\s+capitolul\s+(\d+)\s*$")
VERSE_RE = re.compile(r"^(\d+)\t(.+)$")

VT_BOOK_MAP: dict[str, str] = {'Facerea – Întâia carte a lui Moise': 'Gen',
 'Ieşirea – A doua carte a lui Moise': 'Exod',
 'Leviticul – A treia carte a lui Moise': 'Lev',
 'Numerii – A patra carte a lui Moise': 'Num',
 'Deuteronomul – A cincea carte a lui Moise': 'Deut',
 'Cartea lui Iosua Navi': 'Josh',
 'Cartea Judecătorilor': 'Judg',
 'Cartea Rut': 'Ruth',
 'Cartea întâi a Regilor': '1Sam',
 'Cartea a doua a Regilor': '2Sam',
 'Cartea a treia a Regilor': '1Kgs',
 'Cartea a patra a Regilor': '2Kgs',
 'Cartea întâia Paralipomena sau cartea întâi a Cronicilor': '1Chr',
 'Cartea a doua Paralipomena sau cartea a doua a Cronicilor': '2Chr',
 'Cartea întâi a lui Ezdra': 'Ezra',
 'Cartea lui Neemia sau a doua Ezdra': 'Neh',
 'Cartea Esterei': 'Esth',
 'Cartea lui Iov': 'Job',
 'Psalmii': 'Ps',
 'Pildele lui Solomon': 'Prov',
 'Ecclesiastul': 'Eccl',
 'Cântarea Cântărilor': 'Song',
 'Isaia': 'Isa',
 'Ieremia': 'Jer',
 'Plângerile lui Ieremia': 'Lam',
 'Iezechiel': 'Ezek',
 'Daniel': 'Dan',
 'Osea': 'Hos',
 'Ioil': 'Joel',
 'Amos': 'Amos',
 'Avdie': 'Obad',
 'Iona': 'Jonah',
 'Miheia': 'Mic',
 'Naum': 'Nah',
 'Avacum': 'Hab',
 'Sofonie': 'Zeph',
 'Agheu': 'Hag',
 'Zaharia': 'Zech',
 'Maleahi': 'Mal',
 'Cartea lui Tobit': 'Tob',
 'Cartea Iuditei': 'Jdt',
 'Cartea lui Baruh': 'Bar',
 'Epistola lui Ieremia': 'EpJer',
 'Cântarea celor trei tineri': 'PrAzar',
 'Cartea a treia a lui Ezdra': '1Esd',
 'Cartea înțelepciunii lui Solomon': 'Wis',
 'Cartea înțelepciunii lui Isus fiul lui Sirah (Eclesiasticul)': 'Sir',
 'Istoria Susanei': 'Sus',
 'Istoria omorârii balaurului şi a sfărâmării lui Bel': 'Bel',
 'Cartea întâia a Macabeilor': '1Macc',
 'Cartea a doua a Macabeilor': '2Macc',
 'Cartea a treia a Macabeilor': '3Macc',
 'Rugăciunea regelui Manase': 'PrMan'}
NT_BOOK_MAP: dict[str, str] = {'Sfânta Evanghelie după Matei': 'Matt',
 'Sfânta Evanghelie după Marcu': 'Mark',
 'Sfânta Evanghelie după Luca': 'Luke',
 'Sfânta Evanghelie după Ioan': 'John',
 'Faptele Sfinților Apostoli': 'Acts',
 'Epistola către Romani a Sfantului Apostol Pavel': 'Rom',
 'Epistola întâia către Corinteni a Sfântului Apostol Pavel': '1Cor',
 'Epistola a doua către Corinteni a Sfântului Apostol Pavel': '2Cor',
 'Epistola către Galateni a Sfântului Apostol Pavel': 'Gal',
 'Epistola către Efeseni a Sfântului Apostol Pavel': 'Eph',
 'Epistola către Filipeni a Sfântului Apostol Pavel': 'Phil',
 'Epistola către Coloseni a Sfântului Apostol Pavel': 'Col',
 'Epistola întâia către Tesaloniceni a Sfântului Apostol Pavel': '1Thess',
 'Epistola a doua către Tesaloniceni a Sfântului Apostol Pavel': '2Thess',
 'Epistola întâia către Timotei a Sfântului Apostol Pavel': '1Tim',
 'Epistola a doua către Timotei a Sfântului Apostol Pavel': '2Tim',
 'Epistola către Tit a Sfântului Apostol Pavel': 'Titus',
 'Epistola către Filimon a Sfântului Apostol Pavel': 'Phlm',
 'Epistola către Evrei a Sfântului Apostol Pavel': 'Heb',
 'Epistola Sobornicească a Sfântului Apostol Iacov': 'Jas',
 'Întâia Epistolă Sobornicească a Sfântului Apostol Petru': '1Pet',
 'A doua Epistolă Sobornicească a Sfântului Apostol Petru': '2Pet',
 'Întâia Epistolă Sobornicească a Sfântului Apostol Ioan': '1John',
 'A doua Epistolă Sobornicească a Sfântului Apostol Ioan': '2John',
 'A treia Epistolă Sobornicească a Sfântului Apostol Ioan': '3John',
 'Epistola Sobornicească a Sfântului Apostol Iuda': 'Jude',
 'Apocalipsa Sfântului Ioan Teologul': 'Rev'}


@dataclass(frozen=True)
class ConversionStats:
    books: int
    chapters: int
    verses: int
    section_titles: int
    warnings: int
    skipped_lines: int


def normalize_text(value: str) -> str:
    """Normalize Unicode and remove surrounding whitespace."""
    return unicodedata.normalize("NFC", value.strip())


def normalize_book_key(value: str) -> str:
    """Normalize Romanian legacy diacritics, dash variants and whitespace for lookup."""
    value = normalize_text(value).translate(
        str.maketrans({"ş": "ș", "Ş": "Ș", "ţ": "ț", "Ţ": "Ț"})
    )
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s*[‐‑‒–—―-]\s*", " - ", value)
    return value.casefold()


def xml_escape(value: str) -> str:
    return html.escape(value, quote=False)


def emit_warning(input_path: Path, line_number: int, message: str) -> None:
    location = f"{input_path}:{line_number}"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        safe_message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(
            f"::warning file={input_path},line={line_number}::{safe_message}",
            file=sys.stderr,
        )
    else:
        print(f"ATENȚIONARE: {location}: {message}", file=sys.stderr)


def convert_testament(
    input_path: Path,
    book_map: Mapping[str, str],
    subtype: str,
    *,
    lenient: bool,
) -> tuple[list[str], ConversionStats]:
    if not input_path.is_file():
        raise FileNotFoundError(f"Nu găsesc fișierul de intrare: {input_path}")

    normalized_book_map: dict[str, str] = {}
    for title, osis_id in book_map.items():
        key = normalize_book_key(title)
        previous = normalized_book_map.get(key)
        if previous is not None and previous != osis_id:
            raise ValueError(
                f"Mapare ambiguă pentru titlul {title!r}: {previous} / {osis_id}"
            )
        normalized_book_map[key] = osis_id

    lines = input_path.read_text(encoding="utf-8-sig").splitlines()
    output: list[str] = [f'    <div type="bookGroup" subType="{subtype}">']

    current_book_title: str | None = None
    current_book_osis: str | None = None
    current_chapter: int | None = None
    book_open = False
    chapter_open = False
    skip_content = False

    books = chapters = verses = section_titles = 0
    warnings = skipped_lines = 0
    seen_books: set[str] = set()
    seen_chapters: set[str] = set()
    seen_verses: set[str] = set()
    warned_unknown_books: set[str] = set()

    def close_chapter() -> None:
        nonlocal chapter_open
        if chapter_open:
            output.append("        </chapter>")
            chapter_open = False

    def close_book() -> None:
        nonlocal book_open, current_book_title, current_book_osis, current_chapter
        close_chapter()
        if book_open:
            output.append("      </div>")
            book_open = False
        current_book_title = None
        current_book_osis = None
        current_chapter = None

    def handle_problem(line_number: int, message: str) -> None:
        nonlocal warnings, skipped_lines
        full_message = f"{input_path}:{line_number}: {message}"
        if not lenient:
            raise ValueError(full_message)
        warnings += 1
        skipped_lines += 1
        emit_warning(input_path, line_number, message)

    for line_number, raw_line in enumerate(lines, start=1):
        line = normalize_text(raw_line)
        if not line:
            continue

        chapter_match = CHAPTER_HEADER_RE.match(line)
        if chapter_match:
            book_title = normalize_text(chapter_match.group(1))
            chapter_number = int(chapter_match.group(2))
            book_key = normalize_book_key(book_title)
            new_book_osis = normalized_book_map.get(book_key)

            if new_book_osis is None:
                close_book()
                skip_content = True
                if book_key not in warned_unknown_books:
                    warned_unknown_books.add(book_key)
                    handle_problem(
                        line_number,
                        f"carte necunoscută pentru maparea OSIS: {book_title!r}; "
                        "cartea va fi omisă până la următorul antet recunoscut",
                    )
                else:
                    skipped_lines += 1
                continue

            if current_book_osis != new_book_osis:
                close_book()
                if new_book_osis in seen_books:
                    skip_content = True
                    handle_problem(
                        line_number,
                        f"carte repetată: {new_book_osis}; apariția repetată va fi omisă",
                    )
                    continue

                seen_books.add(new_book_osis)
                books += 1
                current_book_title = book_title
                current_book_osis = new_book_osis
                output.append(f'      <div type="book" osisID="{current_book_osis}">')
                output.append(
                    f'        <title type="main">{xml_escape(current_book_title)}</title>'
                )
                book_open = True

            close_chapter()
            current_chapter = chapter_number
            chapter_id = f"{current_book_osis}.{current_chapter}"
            if chapter_id in seen_chapters:
                current_chapter = None
                skip_content = True
                handle_problem(
                    line_number,
                    f"capitol repetat: {chapter_id}; capitolul repetat va fi omis",
                )
                continue

            seen_chapters.add(chapter_id)
            chapters += 1
            skip_content = False
            output.append(f'        <chapter osisID="{chapter_id}">')
            output.append(
                f'          <title type="chapter">'
                f'{xml_escape(book_title)}, capitolul {current_chapter}</title>'
            )
            chapter_open = True
            continue

        if skip_content:
            skipped_lines += 1
            continue

        if line.startswith('"') and line.endswith('"'):
            if not current_book_osis or current_chapter is None:
                handle_problem(
                    line_number,
                    "subtitlu găsit înaintea unui capitol; linia va fi omisă",
                )
                continue
            subtitle = normalize_text(line[1:-1])
            output.append(
                f'          <title type="section">{xml_escape(subtitle)}</title>'
            )
            section_titles += 1
            continue

        verse_match = VERSE_RE.match(line)
        if verse_match:
            if not current_book_osis or current_chapter is None:
                handle_problem(
                    line_number,
                    f"verset găsit înaintea unui capitol: {line!r}; linia va fi omisă",
                )
                continue

            verse_number = int(verse_match.group(1))
            verse_text = normalize_text(verse_match.group(2))
            verse_id = f"{current_book_osis}.{current_chapter}.{verse_number}"
            if verse_id in seen_verses:
                handle_problem(
                    line_number,
                    f"verset repetat: {verse_id}; versetul repetat va fi omis",
                )
                continue

            seen_verses.add(verse_id)
            verses += 1
            output.append(
                f'          <verse osisID="{verse_id}">'
                f'{xml_escape(verse_text)}</verse>'
            )
            continue

        handle_problem(
            line_number,
            f"linie nerecunoscută: {line!r}; linia va fi omisă",
        )

    close_book()
    output.append("    </div>")

    if books == 0 or chapters == 0 or verses == 0:
        raise ValueError(
            f"{input_path}: conversia nu a produs suficiente date "
            f"(cărți={books}, capitole={chapters}, versete={verses})"
        )

    return output, ConversionStats(
        books,
        chapters,
        verses,
        section_titles,
        warnings,
        skipped_lines,
    )


def build_osis(
    vt_input: Path,
    nt_input: Path,
    output_path: Path,
    *,
    lenient: bool,
) -> None:
    vt_xml, vt_stats = convert_testament(
        vt_input, VT_BOOK_MAP, "x-VT", lenient=lenient
    )
    nt_xml, nt_stats = convert_testament(
        nt_input, NT_BOOK_MAP, "x-NT", lenient=lenient
    )

    document = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">',
        '  <osisText osisIDWork="ROOrthodox_exp" osisRefWork="Bible" xml:lang="ro">',
        '    <header>',
        '      <work osisWork="ROOrthodox_exp">',
        '        <title>Biblia Ortodoxă Română</title>',
        '        <identifier type="OSIS">Bible.ro.ROOrthodox_exp</identifier>',
        '        <language type="IETF">ro</language>',
        '        <type type="x-bible">Bible</type>',
        '      </work>',
        '    </header>',
        *vt_xml,
        *nt_xml,
        '  </osisText>',
        '</osis>',
        '',
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text("\n".join(document), encoding="utf-8", newline="\n")
    temporary_path.replace(output_path)

    print(f"OSIS generat: {output_path.resolve()}")
    print(
        "VT: "
        f"{vt_stats.books} cărți, {vt_stats.chapters} capitole, "
        f"{vt_stats.verses} versete, {vt_stats.section_titles} subtitluri, "
        f"{vt_stats.warnings} atenționări, {vt_stats.skipped_lines} linii omise"
    )
    print(
        "NT: "
        f"{nt_stats.books} cărți, {nt_stats.chapters} capitole, "
        f"{nt_stats.verses} versete, {nt_stats.section_titles} subtitluri, "
        f"{nt_stats.warnings} atenționări, {nt_stats.skipped_lines} linii omise"
    )

    total_warnings = vt_stats.warnings + nt_stats.warnings
    total_skipped = vt_stats.skipped_lines + nt_stats.skipped_lines
    if total_warnings:
        summary = (
            f"Conversia TXT → OSIS s-a încheiat cu {total_warnings} atenționări "
            f"și {total_skipped} linii omise. Verifică txt-to-osis.log."
        )
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning::{summary}", file=sys.stderr)
        else:
            print(f"ATENȚIONARE: {summary}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generează un singur document OSIS din fișierele TXT VT și NT."
    )
    parser.add_argument("--vt-input", type=Path, required=True)
    parser.add_argument("--nt-input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--lenient",
        action="store_true",
        help=(
            "Transformă erorile punctuale de conținut în atenționări și omite "
            "liniile/cărțile problematice. Erorile structurale majore rămân fatale."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        build_osis(
            args.vt_input,
            args.nt_input,
            args.output,
            lenient=args.lenient,
        )
    except (OSError, ValueError) as exc:
        print(f"EROARE: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
