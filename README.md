# Orthodox Bible SWORD Builder

Repository pentru sursele și automatizarea necesare construirii unui modul **SWORD** pentru Biblia Ortodoxă, pornind de la fișiere **UTF-8 text** și **OSIS XML**.

Scopul acestui proiect este:
- păstrarea surselor într-un format ușor de verificat și versionat;
- conversia automată către formatul SWORD;
- publicarea automată a rezultatului într-un **GitHub Release** atunci când se actualizează fișierul XML principal.

## Conținutul repository-ului

### `sources/`
Conține fișierele sursă folosite pentru conversie și verificare:

- `biblia.xml` — fișierul XML principal folosit în build-ul automat;
- `Cartile_VT_NT.txt` — listă / structură auxiliară pentru cărțile Vechiului și Noului Testament;
- `Noul_Testament_OSIS.xml` — OSIS pentru Noul Testament;
- `Noul_Testament_UTF8.txt` — text UTF-8 pentru Noul Testament;
- `Vechiul_Testament_OSIS.xml` — OSIS pentru Vechiul Testament;
- `Vechiul_Testament_UTF8.txt` — text UTF-8 pentru Vechiul Testament;
- `txt_to_osis_NT.py` — script auxiliar pentru conversia / generarea OSIS pentru Noul Testament;
- `txt_to_osis_VT.py` — script auxiliar pentru conversia / generarea OSIS pentru Vechiul Testament.

### `mods.d/`
Conține fișierul de configurare al modulului SWORD (`.conf`).

### `.github/workflows/`
Va conține workflow-ul GitHub Actions care:
- rulează automat la actualizarea fișierului XML principal;
- execută conversia cu `osis2mod`;
- salvează logul build-ului ca artifact;
- publică arhiva rezultată într-un GitHub Release.

## Flux de lucru propus

1. Se editează și verifică sursele din `sources/`.
2. Fișierul principal pentru build este `sources/biblia.xml`.
3. La actualizarea lui, GitHub Actions pornește automat build-ul.
4. Se generează modulul SWORD.
5. Se publică o arhivă a rezultatului într-un Release GitHub.
6. Logul `osis2mod` rămâne disponibil în pagina workflow-ului, pentru analiză ulterioară.

## Build automat

Workflow-ul GitHub Actions este gândit să ruleze **doar** când se modifică:

```text
sources/biblia.xml
```

Astfel, modificările auxiliare din alte fișiere nu generează automat un nou Release până când nu este actualizat și XML-ul principal.

## Unde se vede rezultatul

### Release publicat

După un build reușit, arhiva modulului generat va apărea în:

`GitHub → Repository → Releases`

## Logul build-ului

Pentru debugging și verificare, logul complet al rulării se poate vedea în:

`GitHub → Repository → Actions → workflow run → job / artifact`

## Observații importante

- Directorul `build/` **nu** este versionat în Git; el este generat automat în timpul workflow-ului.
- Fișierele generate și logurile nu trebuie comise în repository.
- Repository-ul păstrează doar sursele, scripturile și configurația necesară pentru build.

## Securitate

Acest repository este conceput astfel încât:

- să nu fie necesară adăugarea manuală a unui token personal pentru publicarea Release-ului;
- workflow-ul să folosească `GITHUB_TOKEN`, generat automat de GitHub Actions;
- logurile să fie disponibile pentru analiză, fără a fi comise în istoricul Git.

Totuși, nu trebuie introduse în repository:

- parole;
- tokenuri;
- chei API;
- informații private sau confidențiale.

Orice informație aflată în surse, loguri, artifacte sau release-uri trebuie tratată ca fiind destinată publicării.

## Licență și drepturi

În acest moment, repository-ul nu presupune implicit că fișierele sursă biblice sunt oferite sub o licență software permisivă.

Dacă ulterior se va adăuga o licență pentru codul din repository, aceasta ar trebui clarificată separat față de drepturile asupra conținutului biblic din `sources/`.

## Stare proiect

Proiect în lucru. Structura actuală este pregătită pentru:

- organizarea surselor text și OSIS;
- validarea și conversia automată;
- publicarea automată a build-urilor SWORD.

🍓☕ Proiectul este one-man-show și orice donație mă motivează să țin proiectul actual 😃

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/ionutojica)
