title: Aide SONAR
tags: aide

Ce guide couvre l'utilisation et les fonctionnalités de l'application SONAR. Les professionnels et les utilisateurs chevronnés trouveront plus d'informations sur les capacités complètes de SONAR dans la [section avancée](#aide-avancee).

## Aide de base

Un champ de recherche unique combine tous les termes de recherche et fournit une liste de résultats triés par pertinence. Ceux-ci peuvent ensuite être filtrés à l'aide de [facettes](#filtrer-la-recherche).

<i class="fa fa-hand-o-right" aria-hidden="true"></i> Pour plus d'exemples de **recherche avancée**, voir **[[search|Recherche de documents]]**.

### Trucs de recherche

| Symbole | Description | Exemple | Effet |
|:---:|---|---|---|
| `*` | Troncature | `uni*` | recherchera les ressources contenant "université", "universel", "unilatéral", etc. |
`+` | Opérateur booléen ET | `montagne + biologie` | recherchera les ressources contenant "montagne" et aussi "biologie" |
| `|` | Opérateur booléen OU | `étude | analyse` | recherche les ressources contenant soit "étude", soit "analyse".
| `-` | Opérateur booléen ET PAS | `confédération -suisse` | recherche les ressources contenant "confédération" mais pas "suisse".
| `()` | Parenthèses, pour combiner des opérateurs | `physique + (étude | analyse)` | recherchera les ressources contenant "physique" et soit "étude", soit "analyse" |
| `""` | Expression exacte | `"ressources humaines"` | recherchera les ressources contenant l'expression exacte "ressources humaines" |

### Filtrer votre recherche

Les facettes vous permettent de filtrer les résultats en fonction de différents critères tels que : _type de document_, _affiliation_, _auteur_, _sujet_, etc. En un seul clic, les facettes peuvent retirer des milliers de résultats non pertinents.

Les facettes peuvent être combinées : la sélection de plusieurs facettes permet d'affiner la recherche et de filtrer la liste des résultats.

Le bouton "Recherche dans texte intégral" permet de rechercher non seulement dans les métadonnées des documents, mais aussi dans leur contenu textuel, lorsqu'ils sont disponibles au format numérique.

### Vue détaillée d'un document

Pour obtenir des informations détaillées sur un document, cliquez sur son titre dans les résultats de la recherche.

* Cette page affiche les métadonnées du document : titre, type, auteurs, résumés, identifiants, etc.
* Vous pouvez visualiser (<i class="fa fa-eye"></i>) ou télécharger (<i class="fa fa-download"></i>) les fichiers attachés à un document.
