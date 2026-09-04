title: Search documents
tags: help

## The engine (Elasticsearch)

<div class="alert-secondary alert" role="alert">The underlying search functionnality is the same for all resource types: documents, deposits, users, etc. Only the JSONSchema-based data structure is different from one resource to another.</div>

SONAR uses [Elasticsearch](https://www.elastic.co/what-is/elasticsearch), a fast and powerful search engine. The key to its performance is that it doesn't query a database directly, but rather text indexes in JSON format, enabling it to find information quickly even among very large quantities of data. Its various mechanisms make it a Google-like search engine, flexible and easy to use for the uninitiated, while offering more advanced functions for technical users as well.

Elasticsearch uses mathematical vectors to assign scores to the resources returned by a query and rank them by relevance.

## Boolean operators and search tips

By default, spaces between words are treated as `AND` operators. Search modifiers and other boolean operators can be used with [Elasticsearch's simple query string][1] syntax.

<i class="fa fa-hand-o-right"></i> See the **[[home|basic help]]** for examples of boolean search shortcuts.

[1]: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html#simple-query-string-syntax "Simple query string syntax documentation"

## Building advanced searches

To build an advanced search, two tools are available and can be combined:

* **URL parameters** are predefined by the system to facilitate frequent queries. These parameters also control the display of search results and the filtering facets. In the URL, the parameters are separated by a `&` symbol.
* **Elasticsearch query string queries** target one or more fields in the index, and are entered after the `q=` parameter.

### URL parameters

Parameters are the elements in the URL after the question mark. They are combined with each other using the `&` symbol.

| Parameter | Use | API example | Interface examples |
| - | - | - | - |
| Resource *PID* | Accesses a specific resource<br/>The user interfaces return the detailed view of the resource, and the API returns the raw record as stored in the database without indexing enrichments. | [`api/documents/111874`](/api/items/1000) | [public](/documents/111874) / [admin](/manage/records/documents/detail/111874) |
| `q` | Introduce an Elasticsearch query | [`api/documents/?q=mountain`](/api/documents/?q=mountain) | [public](/global/search/documents?q=mountain) / [admin](/manage/records/documents?q=mountain) |
| `page` | Set the results page number | [`api/documents?q=mountain&page=5`](/api/documents?q=mountain&page=5) | [public](/global/search/documents?q=mountain&page=5) / [admin](/manage/records/documents?q=mountain&page=5) |
| `size` | Set the number of elements displayed in each results page | [`api/documents?q=mountain&size=25`](/api/documents?q=mountain&size=25) | [public](/global/search/documents?q=mountain&size=25) / [admin](/manage/records/documents?q=mountain&size=25) |
| `sort` | Define how the results are sorted. The possible sort options may vary for different resources. | [`api/documents?q=mountain&sort=title`](/api/documents?q=mountain&sort=title) | [public](/global/search/documents?q=mountain&sort=title) / [admin](/manage/records/documents?q=mountain&sort=title) |
| `prettyprint` | Format the JSON display | [`api/documents/?q=mountain&prettyprint=1`](/api/documents/?q=mountain&prettyprint=1) | only available in the API |
| *Other preset filter* | Apply a filter/facet preset by the system. | [`api/documents?q=mountain&document_type=coar:c_6501`](/api/documents?q=mountain&document_type=coar:c_6501) | [public](/global/search/documents?q=mountain&document_type=coar:c_6501) / [admin](/manage/records/documents?q=mountain&document_type=coar:c_6501) |

### Query syntax

A query is entered using the `q` parameter. The possibilities of the query syntax are described in detail in the Elasticsearch documentation: [Query String Syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax).

A query allows you to target fields or sub-fields of the resource using the index names of these fields. Each `.` in a query indicates that a sub-field is being searched, and the `:` introduces the value sought. It is therefore important to be familiar with the structure of the [[document_fields|document fields]] when constructing a query. For example, `provisionActivity.statement.value:Zürich` searches for *Zürich* in `value` which is a subfield of `statement`, itself a subfield of `provisionActivity` in the document index.

In some cases, the backslash is used in queries, to allow certain characters to escape processing by Elasticsearch. In a browser's address bar, this backslash must be encoded in URL format: `%5C`. For example, the `*` operator, which searches in all subfields of a structured field, must be escaped: `%5c*`.

#### Operators

| Operator | Description | API example | Interface Examples |
|-|-|-|-|
| Search in multiple subfields (`\*`) | Includes all subfields of `title`, including subtitles and additional titles | [`api/documents/?q=title.\*:study`](/api/documents/?q=title.%5c*:study) | [public](/global/search/documents?q=title.%5c*:study) / [admin](/manage/records/documents?q=title.%5c*:study) |
| `*` | Truncation of a word within a search | [`api/documents/?q=title.mainTitle.value:"myopath*"`](/api/documents/?q=title.mainTitle.value:"myopath*") | [public](/global/search/documents?q=title.mainTitle.value:"myopath*") / [admin](/manage/records/documents?q=title.mainTitle.value:"myopath*") |
| `AND` | Boolean AND operator | [`api/documents/?q=title.\*:(mountain AND biology)`](/api/documents/?q=title.%5c*:(mountain AND biology)) | [public](/global/search/documents?q=title.%5c*:(mountain AND biology)) / [admin](/manage/records/documents?q=title.%5c*:(mountain AND biology)) |
| `OR` | Boolean OR operator | [`api/documents/?q=title.\*:(mountain OR biology)`](/api/documents/?q=title.%5c*:(mountain OR biology)) | [public](/global/search/documents?q=title.%5c*:(mountain OR biology)) / [admin](/manage/records/documents?q=title.%5c*:(mountain OR biology)) |
| `NOT` | Boolean NOT operator | [`api/documents/?q=title.\*:(mountain NOT biology))`](/api/documents/?q=title.%5c*:(mountain NOT biology)) | [public](/global/search/documents?q=title.%5c*:(mountain NOT biology)) / [admin](/manage/records/documents?q=title.%5c*:(mountain NOT biology)) |
| (`_exists_:<field name>`) | Search resources where a specific field is present | [`api/documents/?q=_exists_:partOf`](/api/documents/?q=_exists_:partOf) | [public](/global/search/documents?q=_exists_:partOf) / [admin](/manage/records/documents?q=_exists_:partOf) |
| Quotes `""` | Search for resources containing an expression | [`api/documents/?q=title.\*:"à la recherche du temps"`](/api/documents/?q=title.%5c*:%22à la recherche du temps%22) | [public](/global/search/documents?q=title.%5c*:%22à la recherche du temps%22) / [admin](/manage/records/documents?q=title.%5c*:%22à la recherche du temps%22) |

<div class="alert alert-secondary">Operators can combine multiple query terms in a subfield (<code>?q=subjects.\*:(moutain AND Matterhorn)</code> : documents with "mountain" AND "Matterhorn" in the subject field) or multiple subqueries (<code>?q=subjects.\*:moutain AND contribution.\*:"ramuz"</code> : documents with "mountain" in the subjects field AND "ramuz" in the contribution field).</div>

## Search examples

| Query description | Syntax | Example |
|-|-|-|
| everywhere | - | [`?q=study`](/global/search/documents?q=study) |
| by title | `title.\*:` | [`?q=title.\*:study`](/global/search/documents?q=title.%5c*:study) |
| by author | `contribution.\*:` | [`?q=contribution.\*:(rené schneider)`](/global/search/documents?q=contribution.%5c*:(rené schneider)) |
| in the fulltext | `fulltext:` | [`?q=fulltext:remerciements`](/global/search/documents?q=fulltext:remerciements) |
| by identifier | `identifiers.\*:` | [`?q=identifiers.\*:333332`](/global/search/documents?q=identifiers.%5c*:333332) |
| by type of diploma | `dissertation.degree:` | [`?q=dissertation.degree:(Mémoire de bachelor)`](/global/search/documents?q=dissertation.degree:(Mémoire de bachelor)) |
| by place, editor or date | `provisionActivity.\*:` | [`?q=provisionActivity.\*:(Fribourg 2022)`](/global/search/documents?q=provisionActivity.%5c*:(Fribourg 2022)) |
| By record creation date range (square brackets are inclusive) | `[*date* TO *date*]` | [`?q=_created:[2022-01-01 TO 2022-12-31]`](/global/search/documents?q=_created:[2022-01-01 TO 2022-12-31]) |
| By record update date range (brackets are exclusiv) | `{*date* TO *date*}` | [`?q=_updated:{2021-10-24 TO *}`](/global/search/documents?q=_updated:{2021-10-24 TO *}) |
