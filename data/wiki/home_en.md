title: SONAR Help
tags: help

This guide covers the usage and the features of the SONAR application. Professionals and power-users will find more info about the full capabilities of SONAR in the [avanced section](#advanced-help).

## Basic help

A single search field combines all search terms and provides a list of results sorted by relevance. These can then be filtered using [facets](#filter-your-search).

<i class="fa fa-hand-o-right" aria-hidden="true"></i> For more **advanced search** examples, see **[[search|Search documents]]**

### Search tips

| Symbol | Description| Example | Effect |
|:---:|---|---|---|
| `*` | Truncation | `uni*` | will search for resources containing "university", "universal", "unilateral" etc. |
| `+` | Boolean operator AND | `mountain + biology` | will search for resources containing "mountain" and also "biology" |
| `|` | Boolean operator OR | `study | analysis` | will search for resources containing either "study", or "analysis" |
| `-` | Boolean operator NOT | `confederation -swiss` | will search for resources containing "confederation" but not "swiss" |
| `()` | Brackets, to combine operators | `physics + (study | analysis)` | will search for resources containing "physics" and either "study", or "analysis" |
| `""` | Exact expression | `"human resources"` | will search for resources containing the exact expression "human resources" |

### Filter your search

Facets allow you to filter the results according to different criteria such as: _document type_, _affiliation_, _author_, _subject_, etc. With one click, facets can filter out thousands of irrelevant results.

Facets can be combined: selecting multiple facets will refine your query and filter the list of results.

The “Search in full-text” button allows you to search not only in the metadata of documents, but also in their textual content, when they are available in digital format.

### Detailed view of a document

To view detailed information about a document, click on its title in the search results.

* This page displays the document metadata: title, type, authors, abstracts, identifiers, etc.
* You can view (<i class="fa fa-eye"></i>) or download (<i class="fa fa-download"></i>) the files attached to a document.
