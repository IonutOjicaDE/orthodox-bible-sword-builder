# Orthodox Bible SWORD Builder

![Logo Orthodox Bible SWORD Builder](assets/logo.png)

Repository pentru sursele și automatizarea necesare construirii unui modul
**SWORD** pentru Biblia Ortodoxă Română.

Sursele versionate ale textului biblic sunt exclusiv cele două fișiere TXT
UTF-8. Documentul OSIS XML necesar pentru `osis2mod` este generat în timpul
build-ului și nu este păstrat în repository.

Scopul proiectului este:

- păstrarea surselor într-un format text ușor de verificat și versionat;
- generarea automată a documentului OSIS și a modulului SWORD;
- verificarea modulului rezultat;
- publicarea automată a arhivei într-un GitHub Release.

## Structura repository-ului

### `sources/`

Conține singurele surse ale textului biblic folosite de build:

- `Vechiul_Testament_UTF8.txt` — textul UTF-8 al Vechiului Testament;
- `Noul_Testament_UTF8.txt` — textul UTF-8 al Noului Testament.

### `scripts/`

- `build_biblia_osis.py` — validează și combină cele două surse TXT într-un
  document OSIS XML temporar.

### `mods.d/`

- `roorthodox_exp.conf` — configurația modulului SWORD, inclusiv versiunea
  publicată.

### `reference/`

Conține materiale păstrate pentru consultare, care nu sunt folosite în build:

- `Cartile_VT_NT.txt` — inventarul istoric al titlurilor cărților biblice;
- `osis2mod.output` — ieșirea unei rulări anterioare `osis2mod`, utilă pentru
  analiza mapărilor de versificare.

### `.github/workflows/`

- `build-release.yml` — automatizarea completă pentru generarea, verificarea,
  arhivarea și publicarea modulului.

## Fluxul de build

1. Sunt validate cele două surse TXT, scriptul de conversie și configurația
   modulului.
2. `scripts/build_biblia_osis.py` generează
   `build/generated/biblia.xml`.
3. XML-ul generat este verificat cu `xmllint`.
4. `osis2mod` construiește modulul SWORD folosind versificarea `Orthodox`.
5. Configurația modulului este copiată în structura instalabilă și primește
   data build-ului.
6. Modulul este detectat și testat cu `diatheke`.
7. Se generează arhiva instalabilă `roorthodox_exp-sword.zip` și suma sa
   SHA-256.
8. Arhiva, logurile și XML-ul generat sunt încărcate ca artifacts; când
   publicarea este activă, arhiva și suma SHA-256 sunt atașate unui GitHub
   Release.

## Declanșarea workflow-ului

Un push pe ramura `main` pornește automat workflow-ul numai când se modifică
una dintre sursele:

```text
sources/Vechiul_Testament_UTF8.txt
sources/Noul_Testament_UTF8.txt
```

La un asemenea push este publicat automat un Release. Înainte de publicarea
unei surse modificate trebuie incrementată valoarea `Version=` din
`mods.d/roorthodox_exp.conf`; workflow-ul oprește build-ul dacă Release-ul
versiunii există deja.

Workflow-ul poate fi pornit și manual:

- implicit construiește și verifică modulul fără să publice un Release;
- opțional poate publica un Release;
- opțional poate înlocui un Release existent, dar numai la o rulare manuală.

## Generarea locală a documentului OSIS

Documentul intermediar poate fi generat local cu Python:

```bash
python scripts/build_biblia_osis.py \
  --vt-input sources/Vechiul_Testament_UTF8.txt \
  --nt-input sources/Noul_Testament_UTF8.txt \
  --output build/generated/biblia.xml \
  --lenient
```

Directorul `build/` este ignorat de Git. Fișierele XML generate, modulele
compilate și logurile de build nu trebuie comise în repository.

## Unde se găsesc rezultatele

- Arhiva publicată: `GitHub → Repository → Releases`
- Rulări și loguri: `GitHub → Repository → Actions`
- Artifacts temporare: în pagina fiecărei rulări a workflow-ului

## Securitate

Workflow-ul folosește `GITHUB_TOKEN`, furnizat automat de GitHub Actions, și nu
necesită un token personal.

Nu trebuie introduse în repository parole, tokenuri, chei API sau informații
private. Sursele, logurile, artifacts și release-urile trebuie considerate
informații destinate publicării.

## Licență și drepturi

Repository-ul nu presupune implicit că textele biblice sunt oferite sub o
licență software permisivă. O eventuală licență pentru cod trebuie clarificată
separat de drepturile asupra conținutului din `sources/`.

## Stare proiect

Proiect în lucru. Structura actuală este pregătită pentru:

- administrarea surselor TXT;
- generarea și validarea automată a documentului OSIS;
- construirea și testarea modulului SWORD;
- publicarea automată a release-urilor.

🍓☕ Proiectul este one-man-show și orice donație mă motivează să țin proiectul
actual 😃

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/ionutojica)
