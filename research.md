# Rapport de recherche — Issue #777 : Révision de la hiérarchie des types de documents

**Date :** 2026-03-09
**Référence :** <https://github.com/rero/sonar/issues/777>
**Branche analysée :** `rep-coar`

---

## 1. Contexte et objectif

L'issue #777 concerne la mise à jour de la hiérarchie des types de documents dans SONAR pour la rendre conforme à la version 3.2 du vocabulaire COAR Resource Types (<https://vocabularies.coar-repositories.org/resource_types/3.2/>, publié le 2024-12-03).

Entre COAR v2 et COAR v3, plusieurs types utilisés par SONAR ont été **dépréciés**.

---

## 2. Fichier central : `type-v1.0.0.json`

**Chemin :** `sonar/jsonschemas/common/type-v1.0.0.json`

Ce fichier est l'unique source de vérité pour les types de documents dans SONAR. Il est utilisé par **référence `$ref`** dans deux schémas :

- `sonar/modules/documents/jsonschemas/documents/document-v1.0.0.json` (ligne 274)
- `sonar/modules/deposits/jsonschemas/deposits/deposit-v1.0.0.json` (ligne 306)

Le fichier définit :

1. Un tableau `enum` de 53 valeurs acceptables (43 codes COAR + 4 types personnalisés SONAR + 6 types dépréciés COAR)
2. Un widget `tree-select` Angular Formly avec une hiérarchie parent/enfant pour l'interface utilisateur

### Structure actuelle de l'arbre dans SONAR

```
Book (c_2f33)
Book chapter (c_3248)
Conference output (c_c94f)  [parent — 6 enfants]
  ├── Conference paper in proceedings (c_5794)
  ├── Conference paper not in proceedings (c_18cp)
  ├── Conference poster (c_6670)
  ├── Conference poster not in proceedings (c_18co)
  ├── Conference proceedings (c_f744)
  └── Conference presentation (R60J-J5BD)
Dataset (c_ddb1)
Journal contribution (c_3e5a)  [DÉPRÉCIÉ — parent — 4 enfants]
  ├── Data paper (c_beb9)
  ├── Journal article (c_6501)
  ├── Newspaper article (c_998f)
  └── Review article (c_dcae04bc)
Book review (c_ba08)
Lecture (c_8544)
Non textual object [CUSTOM — parent — 6 enfants]
  ├── Film (c_8a7e)
  ├── Image (c_ecc8)
  ├── Cartographic material (c_12cc)
  ├── Sound (c_18cc)
  ├── Score (c_18cw)
  └── Software (c_5ce6)
Patent (c_15cd)
Periodical (c_2659)  [DÉPRÉCIÉ — parent — 3 enfants]
  ├── Journal (c_0640)
  ├── Magazine (c_2cd9)
  └── Newspaper (c_2fe3)
Preprint (c_816b)
Report (c_93fc)  [parent — 9 enfants]
  ├── Internal report (c_18ww)  [DÉPRÉCIÉ]
  ├── Memorandum (c_18wz)
  ├── Other type of report (c_18wq)  [DÉPRÉCIÉ]
  ├── Policy report (c_186u)
  ├── Project deliverable (c_18op)
  ├── Report part (c_ba1f)  [DÉPRÉCIÉ]
  ├── Report to funding agency (c_18hj)  [DÉPRÉCIÉ]
  ├── Research report (c_18ws)
  └── Technical report (c_18gh)
Thesis (c_46ec)  [parent — 6 enfants]
  ├── Bachelor thesis (c_7a1f)
  ├── Doctoral thesis (c_db06)
  ├── Master thesis (c_bdcc)
  ├── Habilitation thesis [CUSTOM]
  ├── Advanced studies thesis [CUSTOM]
  └── Other thesis [CUSTOM]
Working paper (c_8042)
Other (c_1843)
```

---

## 3. Types dépréciés : analyse détaillée

### 3.1 Tableau des types dépréciés utilisés dans SONAR

| ID COAR | Label SONAR | Statut COAR v3.2 | Remplacement suggéré |
|---|---|---|---|
| `coar:c_3e5a` | Journal contribution | **DÉPRÉCIÉ** | `coar:c_6501` (Journal article) ou `coar:c_0640` (Journal) selon contexte |
| `coar:c_2659` | Periodical | **DÉPRÉCIÉ** | `coar:c_0640` (Journal), `coar:c_2cd9` (Magazine), `coar:c_2fe3` (Newspaper), ou `QX5C-AR31` (Other Periodical) |
| `coar:c_18ww` | Internal report | **DÉPRÉCIÉ** | `coar:c_18ws` (Research report) ou `coar:c_18gh` (Technical report) |
| `coar:c_18wq` | Other type of report | **DÉPRÉCIÉ** | `coar:c_93fc` (Report) |
| `coar:c_ba1f` | Report part | **DÉPRÉCIÉ** | `coar:c_93fc` (Report) ou `coar:c_3248` (Book chapter) |
| `coar:c_18hj` | Report to funding agency | **DÉPRÉCIÉ** | `coar:c_186u` (Policy report) ou `coar:c_18op` (Project deliverable) |

### 3.2 Documents de fixtures utilisant des types dépréciés

Le fichier de fixtures `data/documents/data.json` contient des enregistrements avec les types suivants (présence confirmée) :

- `coar:c_3e5a` — 2 occurrences (lignes 1199, 7024)
- `coar:c_2659` — 2 occurrences (lignes 2852, 8678)
- `coar:c_18ww` — 1 occurrence (ligne 3577)
- `coar:c_18wq` — 1 occurrence (ligne 3797)
- `coar:c_ba1f` — 1 occurrence (ligne 4146)
- `coar:c_18hj` — 1 occurrence (ligne 4256)

Le fichier `data/deposits.json` contient : `"documentType": "coar:c_3e5a"`.

---

## 4. Impact dans le code

### 4.1 Importateur SRU (`sonar/modules/documents/dojson/sru/model.py`)

L'importateur SRU génère activement deux types dépréciés depuis les codes MARC21 leader :

```python
# Ligne 543-544 : MARC21 leader 07 = "b" → Contribution to journal
if leader_07 == "b":
    return "coar:c_3e5a"  # DÉPRÉCIÉ

# Ligne 551-552 : MARC21 leader 07 = "s" → Periodical
if leader_07 == "s":
    return "coar:c_2659"  # DÉPRÉCIÉ
```

**Impact :** Tout import SRU de périodiques ou articles de journaux produit des types dépréciés.

### 4.3 Sérialiseur schema.org (`sonar/modules/documents/serializers/schemas/schemaorg.py`)

Tous les types dépréciés sont mappés dans `TYPE_MAPPING` :

```python
"coar:c_3e5a": "Article",    # DÉPRÉCIÉ
"coar:c_2659": "Periodical", # DÉPRÉCIÉ
"coar:c_18ww": "Report",     # DÉPRÉCIÉ
"coar:c_18wq": "Report",     # DÉPRÉCIÉ
"coar:c_ba1f": "Report",     # DÉPRÉCIÉ
"coar:c_18hj": "Report",     # DÉPRÉCIÉ
```

### 4.4 Sérialiseur Dublin Core / OAI-PMH (`sonar/modules/documents/serializers/schemas/dc.py`)

La méthode `get_types()` (lignes 296–305) convertit le `documentType` en URL COAR :

```python
# "coar:c_3e5a" → "http://purl.org/coar/resource_type/c_3e5a"
```

Si un document garde un type déprécié, l'URL COAR générée sera invalide dans le contexte de COAR v3.2.

### 4.5 Expressions de visibilité dans les schémas (Formly `hideExpressions`)

Dans `document-v1.0.0.json` et `deposit-v1.0.0.json`, `coar:c_3e5a` apparaît dans plusieurs expressions conditionnelles Angular Formly qui contrôlent l'affichage de champs :

**`document-v1.0.0.json` :**

- Ligne 612 : `provisionActivity` requis — exclut `c_3e5a`
- Ligne 1800 : visibilité champ `numberingVolume` — inclut `c_3e5a`
- Ligne 1812 : visibilité champ `numberingIssue` — inclut `c_3e5a`
- Ligne 2144 : `partOf` requis — inclut `c_3e5a`

**`deposit-v1.0.0.json` :**

- Lignes 606, 621, 735 : visibilité champs de publication — inclut `c_3e5a`

**Impact :** La suppression de `coar:c_3e5a` sans mise à jour de ces expressions cassera la logique conditionnelle des formulaires.

---

## 5. Comparaison SONAR vs COAR v3.2 — types manquants

COAR v3.2 propose de nouveaux types qui ne sont **pas encore** dans SONAR :

### Sous-types de Journal (enfants de `c_0640`)

En COAR v3.2, `c_0640` (Journal) a des enfants qui ne sont pas dans SONAR :

- `c_b239` — Editorial
- `c_545b` — Letter to the Editor
- (+ les enfants de `c_6501` Journal Article : `c_2df8fbb1` Research Article, `c_7acd` Corrigendum, `c_7bab` Software Paper)

### Sous-types de Review (enfants de `c_efa0` Review)

- `c_ba08` Book review — **déjà dans SONAR** mais sans parent `c_efa0`
- `D97F-VB57` Commentary
- `H9BQ-739P` Peer Review

### Sous-types de Conference Proceedings (enfants de `c_f744`)

- `c_5794` Conference paper — **déjà dans SONAR** (mais rattaché à `c_c94f` au lieu de `c_f744`)
- `c_6670` Conference poster — **déjà dans SONAR** (idem)

### Problème de hiérarchie Conference Output

Dans SONAR, `c_5794` (Conference paper) et `c_6670` (Conference poster) sont enfants directs de `c_c94f` (Conference output). Dans COAR v3.2, ils sont enfants de `c_f744` (Conference Proceedings), qui est lui-même enfant de `c_c94f`. SONAR a aplati cette hiérarchie.

### Nouveaux types de premier niveau en COAR v3.2

Absents de SONAR :

- `F8RT-TJK0` — Artistic Work
- `YC9F-HGCF` — Archival Collection (enfant de Collection)
- `1YTN-RJZE` — Court Documents (enfant de Collection)
- `S7R1-K5P0` — Physical Sample
- `8KJG-QS0Y` — Research Instrument
- `H6QP-SC1X` — Trademark
- `QX5C-AR31` — Other Periodical (successeur potentiel de `c_2659`)

---

## 7. Restructuration nécessaire de la hiérarchie

### 7.1 Cas `coar:c_3e5a` → à supprimer

`c_3e5a` est un parent déprécié. Ses 4 enfants dans SONAR doivent être rattachés à un nouveau parent. En COAR v3.2, ces types sont organisés ainsi :

- `c_6501` (Journal Article) → enfant de `c_0640` (Journal) → enfant de Text
- `c_beb9` (Data Paper) → enfant de `c_6501` (Journal Article)
- `c_dcae04bc` (Review Article) → enfant de `c_6501` (Journal Article)
- `c_998f` (Newspaper Article) → enfant de `c_2fe3` (Newspaper)

Dans SONAR, le plus simple serait de faire de `c_0640` (Journal) le nouveau parent de `c_6501`, `c_beb9`, `c_dcae04bc`. Et `c_998f` resterait enfant de `c_2fe3` ou deviendrait autonome.

### 7.2 Cas `coar:c_2659` → à supprimer

`c_2659` (Periodical) est le parent de `c_0640` (Journal), `c_2cd9` (Magazine), `c_2fe3` (Newspaper). Ces 3 sous-types sont **valides** dans COAR v3.2 et deviennent des types de premier niveau (enfants de Text).

### 7.3 Cas des types de rapport dépréciés → à supprimer de l'`enum`

- `c_18ww` (Internal report) → remplacer par `c_18ws` (Research report) dans les données existantes
- `c_18wq` (Other type of report) → remplacer par `c_93fc` (Report) dans les données existantes
- `c_ba1f` (Report part) → cas ambigu, remplacer par `c_93fc` (Report) ou `c_3248` (Book chapter)
- `c_18hj` (Report to funding agency) → remplacer par `c_186u` (Policy report)

---

## 10. Résumé des changements COAR v3 pertinents pour SONAR

### Types dépréciés utilisés dans SONAR

```
c_3e5a  Contribution to journal  → supprimé de COAR v3
c_ba1f  Report part              → supprimé de COAR v3
c_18ww  Internal report          → supprimé de COAR v3
c_18wq  Other type of report     → supprimé de COAR v3
c_18hj  Report to funding agency → supprimé de COAR v3
c_2659  Periodical               → supprimé de COAR v3
```

### Nouveaux types pertinents pour SONAR dans COAR v3.2

```
c_2df8fbb1  Research Article  (enfant de c_6501 Journal Article)
c_7acd      Corrigendum        (enfant de c_6501 Journal Article)
c_7bab      Software Paper     (enfant de c_6501 Journal Article)
c_b239      Editorial          (enfant de c_0640 Journal)
c_545b      Letter to Editor   (enfant de c_0640 Journal)
D97F-VB57   Commentary         (enfant de c_efa0 Review)
H9BQ-739P   Peer Review        (enfant de c_efa0 Review)
QX5C-AR31   Other Periodical   (successeur de c_2659)
DX5J-TA9R   Knowledge Synthesis Protocol (enfant de c_93fc Report)
YZ1N-ZFT9   Research Protocol  (enfant de c_93fc Report)
c_7877      Clinical Study     (enfant de c_93fc Report)
c_ab20      Data Management Plan (enfant de c_93fc Report)
```
