import re
import html
from pathlib import Path

INPUT_FILE = "Noul_Testament_UTF8.txt"
OUTPUT_FILE = "Noul_Testament_OSIS.xml"

# Mapare din titlul exact al cărții în osisID
BOOK_MAP = {
    "Sfânta Evanghelie după Matei": "Matt",
    "Sfânta Evanghelie după Marcu": "Mark",
    "Sfânta Evanghelie după Luca": "Luke",
    "Sfânta Evanghelie după Ioan": "John",
    "Faptele Sfinţilor Apostoli": "Acts",
    "Epistola către Romani a Sfantului Apostol Pavel": "Rom",
    "Epistola întâia către Corinteni a Sfântului Apostol Pavel": "1Cor",
    "Epistola a doua către Corinteni a Sfântului Apostol Pavel": "2Cor",
    "Epistola către Galateni a Sfântului Apostol Pavel": "Gal",
    "Epistola către Efeseni a Sfântului Apostol Pavel": "Eph",
    "Epistola către Filipeni a Sfântului Apostol Pavel": "Phil",
    "Epistola către Coloseni a Sfântului Apostol Pavel": "Col",
    "Epistola întâia către Tesaloniceni a Sfântului Apostol Pavel": "1Thess",
    "Epistola a doua către Tesaloniceni a Sfântului Apostol Pavel": "2Thess",
    "Epistola întâia către Timotei a Sfântului Apostol Pavel": "1Tim",
    "Epistola a doua către Timotei a Sfântului Apostol Pavel": "2Tim",
    "Epistola către Tit a Sfântului Apostol Pavel": "Titus",
    "Epistola către Filimon a Sfântului Apostol Pavel": "Phlm",
    "Epistola către Evrei a Sfântului Apostol Pavel": "Heb",
    "Epistola Sobornicească a Sfântului Apostol Iacov": "Jas",
    "Întâia Epistolă Sobornicească a Sfântului Apostol Petru": "1Pet",
    "A doua Epistolă Sobornicească a Sfântului Apostol Petru": "2Pet",
    "Întâia Epistolă Sobornicească a Sfântului Apostol Ioan": "1John",
    "A doua Epistolă Sobornicească a Sfântului Apostol Ioan": "2John",
    "A treia Epistolă Sobornicească a Sfântului Apostol Ioan": "3John",
    "Epistola Sobornicească a Sfântului Apostol Iuda": "Jude",
    "Apocalipsa Sfântului Ioan Teologul": "Rev",
}

# Pattern pentru linia de început de capitol:
# ex: "Sfânta Evanghelie după Matei, capitolul 2"
CHAPTER_HEADER_RE = re.compile(r"^(.*?),\s+capitolul\s+(\d+)\s*$")

# Pattern pentru un verset: "12\tText..."
VERSE_RE = re.compile(r"^(\d+)\t(.+)$")

def xml_escape(text: str) -> str:
    return html.escape(text, quote=False)

def main():
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    if not input_path.exists():
        raise FileNotFoundError(f"Nu găsesc fișierul de intrare: {input_path}")

    lines = input_path.read_text(encoding="utf-8").splitlines()

    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">')
    out.append('  <osisText osisIDWork="ROOrthodoxNT" osisRefWork="Bible" xml:lang="ro">')
    out.append('    <header>')
    out.append('      <work osisWork="ROOrthodoxNT">')
    out.append('        <title>Noul Testament Ortodox Român</title>')
    out.append('        <identifier type="OSIS">Bible.ro.ROOrthodoxNT</identifier>')
    out.append('        <language type="IETF">ro</language>')
    out.append('        <type type="x-bible">Bible</type>')
    out.append('      </work>')
    out.append('    </header>')
    out.append('    <div type="bookGroup" subType="x-NT">')

    current_book_title = None
    current_book_osis = None
    current_chapter = None
    book_open = False
    chapter_open = False

    pending_subtitle = None

    def close_chapter():
        nonlocal chapter_open
        if chapter_open:
            out.append('        </chapter>')
            chapter_open = False

    def close_book():
        nonlocal book_open, current_book_title, current_book_osis
        close_chapter()
        if book_open:
            out.append('      </div>')
            book_open = False
        current_book_title = None
        current_book_osis = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        # Antet de capitol
        m = CHAPTER_HEADER_RE.match(line)
        if m:
            book_title = m.group(1).strip()
            chapter_num = int(m.group(2))

            if book_title not in BOOK_MAP:
                raise ValueError(f"Carte necunoscută pentru mapare OSIS: {book_title}")

            new_book_osis = BOOK_MAP[book_title]

            # Dacă s-a schimbat cartea, închidem cartea precedentă
            if current_book_osis != new_book_osis:
                close_book()
                current_book_title = book_title
                current_book_osis = new_book_osis
                out.append(f'      <div type="book" osisID="{current_book_osis}">')
                out.append(f'        <title type="main">{xml_escape(current_book_title)}</title>')
                book_open = True

            # Închidem capitolul precedent și deschidem unul nou
            close_chapter()
            current_chapter = chapter_num
            out.append(f'        <chapter osisID="{current_book_osis}.{current_chapter}">')
            out.append(f'          <title type="chapter">{xml_escape(book_title)}, capitolul {current_chapter}</title>')
            chapter_open = True
            pending_subtitle = None
            continue

        # Subtitlu între ghilimele
        if line.startswith('"') and line.endswith('"') and current_book_osis and current_chapter:
            subtitle = line.strip('"').strip()
            pending_subtitle = subtitle
            out.append(f'          <title type="section">{xml_escape(pending_subtitle)}</title>')
            continue

        # Verset
        m = VERSE_RE.match(line)
        if m:
            if not current_book_osis or not current_chapter:
                raise ValueError(f"Verset găsit înainte de antetul de capitol: {line}")

            verse_num = int(m.group(1))
            verse_text = m.group(2).strip()

            out.append(
                f'          <verse osisID="{current_book_osis}.{current_chapter}.{verse_num}">{xml_escape(verse_text)}</verse>'
            )
            continue

        # Dacă ajunge aici, linia n-a fost recunoscută
        # O poți trata ca notă, comentariu sau eroare:
        raise ValueError(f"Linie nerecunoscută: {line}")

    close_book()

    out.append('    </div>')
    out.append('  </osisText>')
    out.append('</osis>')

    output_path.write_text("\n".join(out), encoding="utf-8")
    print(f"Gata. Fișier generat: {output_path.resolve()}")

if __name__ == "__main__":
    try:
        main()
        print("\nScriptul s-a terminat cu succes.")
    except Exception as e:
        print("\nA apărut o eroare:")
        print(e)

    input("\nApasă Enter pentru a închide programul...")
