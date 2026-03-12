import re
import html
from pathlib import Path

INPUT_FILE = "Vechiul_Testament_UTF8.txt"
OUTPUT_FILE = "Vechiul_Testament_OSIS.xml"

# Mapare din titlul exact al cărții în osisID
BOOK_MAP = {
    "Facerea – Întâia carte a lui Moise": "Gen",
    "Ieşirea – A doua carte a lui Moise": "Exod",
    "Leviticul – A treia carte a lui Moise": "Lev",
    "Numerii – A patra carte a lui Moise": "Num",
    "Deuteronomul – A cincea carte a lui Moise": "Deut",

    "Cartea lui Iosua Navi": "Josh",
    "Cartea Judecătorilor": "Judg",
    "Cartea Rut": "Ruth",

    "Cartea întâi a Regilor": "1Sam",
    "Cartea a doua a Regilor": "2Sam",
    "Cartea a treia a Regilor": "1Kgs",
    "Cartea a patra a Regilor": "2Kgs",

    "Cartea întâia Paralipomena sau cartea întâi a Cronicilor": "1Chr",
    "Cartea a doua Paralipomena sau cartea a doua a Cronicilor": "2Chr",

    "Cartea întâi a lui Ezdra": "Ezra",
    "Cartea lui Neemia sau a doua Ezdra": "Neh",

    "Cartea Esterei": "Esth",
    "Cartea lui Iov": "Job",
    "Psalmii": "Ps",
    "Pildele lui Solomon": "Prov",
    "Ecclesiastul": "Eccl",

    "Cântarea Cântărilor": "Song",
    "Isaia": "Isa",
    "Ieremia": "Jer",
    "Plângerile lui Ieremia": "Lam",
    "Iezechiel": "Ezek",
    "Daniel": "Dan",
    "Osea": "Hos",
    "Ioil": "Joel",
    "Amos": "Amos",
    "Avdie": "Obad",
    "Iona": "Jonah",
    "Miheia": "Mic",
    "Naum": "Nah",
    "Avacum": "Hab",
    "Sofonie": "Zeph",
    "Agheu": "Hag",
    "Zaharia": "Zech",
    "Maleahi": "Mal",

    "Cartea lui Tobit": "Tob",
    "Cartea Iuditei": "Jdt",
    "Cartea lui Baruh": "Bar",
    "Epistola lui Ieremia": "EpJer",
    "Cântarea celor trei tineri": "PrAzar",
    "Cartea a treia a lui Ezdra": "1Esd",
    "Cartea întelepciunii lui Solomon": "Wis",
    "Cartea înţelepciunii lui Solomon": "Wis",
    "Cartea întelepciunii lui Isus fiul lui Sirah (Eclesiasticul)": "Sir",
    "Cartea înţelepciunii lui Isus fiul lui Sirah (Eclesiasticul)": "Sir",
    "Istoria Susanei": "Sus",
    "Istoria omorârii balaurului şi a sfărâmării lui Bel": "Bel",
    "Istoria omorârii balaurului şi a sfarâmării lui Bel": "Bel",
    "Cartea întâia a Macabeilor": "1Macc",
    "Cartea a doua a Macabeilor": "2Macc",
    "Cartea a treia a Macabeilor": "3Macc",
    "Rugăciunea regelui Manase": "PrMan",
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
    out.append('  <osisText osisIDWork="ROOrthodoxVT" osisRefWork="Bible" xml:lang="ro">')
    out.append('    <header>')
    out.append('      <work osisWork="ROOrthodoxVT">')
    out.append('        <title>Vechiul Testament Ortodox Român</title>')
    out.append('        <identifier type="OSIS">Bible.ro.ROOrthodoxVT</identifier>')
    out.append('        <language type="IETF">ro</language>')
    out.append('        <type type="x-bible">Bible</type>')
    out.append('      </work>')
    out.append('    </header>')
    out.append('    <div type="bookGroup" subType="x-VT">')

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
