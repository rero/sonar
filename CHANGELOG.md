# Changelog

## [v1.4.0](https://github.com/rero/sonar/tree/v1.4.0) (2021-11-10)

[Full Changelog](https://github.com/rero/sonar/compare/v1.3.0...v1.4.0)

**Implemented enhancements:**

- Allow document visibility to be set during deposit \[3\] [\#640](https://github.com/rero/sonar/issues/640)
- Allow to display documents only for allowed IP addresses [\#632](https://github.com/rero/sonar/issues/632)
- Remove the moderator/administrator name in the e-mails of the validation process [\#551](https://github.com/rero/sonar/issues/551)
- The semi-controlled suggestions should be activated for contributors [\#542](https://github.com/rero/sonar/issues/542)
- Call to action button for submitting a deposit [\#366](https://github.com/rero/sonar/issues/366)
- Messages sent for "Forgot password" should be improved. [\#343](https://github.com/rero/sonar/issues/343)

**Fixed bugs:**

- Impossible to save a document after opening it for editing [\#689](https://github.com/rero/sonar/issues/689)
- A moderator cannot select an existing collection in the document editor [\#683](https://github.com/rero/sonar/issues/683)
- Error in swisscovery metadata import \[2\] [\#674](https://github.com/rero/sonar/issues/674)
- Fix responsive menu \(TEST env\) \[2\] [\#667](https://github.com/rero/sonar/issues/667)
- Facet display conditions need adjustments [\#634](https://github.com/rero/sonar/issues/634)
- Display facets depending on context [\#623](https://github.com/rero/sonar/issues/623)
- Number/pages missing in OAI export \(oai\_dc\), field `dc:source` when no volume exists [\#370](https://github.com/rero/sonar/issues/370)

**Closed issues:**

- Import faculty and department data from RERO DOC for FOLIA [\#691](https://github.com/rero/sonar/issues/691)
- Field `publication.publisher` to be renamed \(with description\) in the deposit [\#690](https://github.com/rero/sonar/issues/690)
- Allow each dedicated repository to configure its footer links [\#682](https://github.com/rero/sonar/issues/682)
- Display Series fields in the detailed view [\#660](https://github.com/rero/sonar/issues/660)
- Identify all DOIs imported from RERO DOC [\#659](https://github.com/rero/sonar/issues/659)
- Make a real test with an external domain name \[1\] [\#647](https://github.com/rero/sonar/issues/647)
- Make the organisation home page multilingual \[3\] [\#639](https://github.com/rero/sonar/issues/639)
- ROAR: Load documents from RERO DOC and from the provided export [\#620](https://github.com/rero/sonar/issues/620)
- FOLIA: Load documents from RERO DOC [\#619](https://github.com/rero/sonar/issues/619)
- Import publications from swisscovery [\#610](https://github.com/rero/sonar/issues/610)
- Export usage data for invoicing [\#562](https://github.com/rero/sonar/issues/562)
- Option to sort results by publication year, date added and relevance \(ev. title\) [\#402](https://github.com/rero/sonar/issues/402)
- Group users by sections [\#145](https://github.com/rero/sonar/issues/145)

**Merged pull requests:**

- Change color scheme for two dedicated repositories \(tentative\) [\#700](https://github.com/rero/sonar/pull/700) ([mmo](https://github.com/mmo))
- deposit: improve document type detection. [\#698](https://github.com/rero/sonar/pull/698) ([Garfield-fr](https://github.com/Garfield-fr))
- deposit: fix moderator validation [\#697](https://github.com/rero/sonar/pull/697) ([jma](https://github.com/jma))
- Identify DOI in RERO DOC field 775 $o [\#696](https://github.com/rero/sonar/pull/696) ([mmo](https://github.com/mmo))
- documents: import faculty and department from RERO DOC for UNIFR [\#695](https://github.com/rero/sonar/pull/695) ([mmo](https://github.com/mmo))
- deposits: fix swisscovery import [\#694](https://github.com/rero/sonar/pull/694) ([Garfield-fr](https://github.com/Garfield-fr))
- deposits: change title and add description on publisher field [\#693](https://github.com/rero/sonar/pull/693) ([Garfield-fr](https://github.com/Garfield-fr))
- documents: fix document edition [\#692](https://github.com/rero/sonar/pull/692) ([jma](https://github.com/jma))
- collections: allow submitter to search in collections. [\#688](https://github.com/rero/sonar/pull/688) ([jma](https://github.com/jma))
- organisations: implement multilingual footer for dedicated [\#687](https://github.com/rero/sonar/pull/687) ([Garfield-fr](https://github.com/Garfield-fr))
- dependencies: fix several packages version for security reasons [\#686](https://github.com/rero/sonar/pull/686) ([jma](https://github.com/jma))
- application: fix responsive design menu [\#685](https://github.com/rero/sonar/pull/685) ([Garfield-fr](https://github.com/Garfield-fr))
- subdivisions: fix moderator access bug [\#678](https://github.com/rero/sonar/pull/678) ([mmo](https://github.com/mmo))
- documents: improve custom field import from RERO DOC for ROAR [\#658](https://github.com/rero/sonar/pull/658) ([mmo](https://github.com/mmo))
- dependencies: fix pillow version for security reasons [\#657](https://github.com/rero/sonar/pull/657) ([mmo](https://github.com/mmo))
- documents: fill out custom fields for ROAR during RERO DOC import [\#656](https://github.com/rero/sonar/pull/656) ([mmo](https://github.com/mmo))
- deposit: allow to set document visibility [\#654](https://github.com/rero/sonar/pull/654) ([jma](https://github.com/jma))
- documents: try to parse the thesis note from RERO DOC more precisely [\#650](https://github.com/rero/sonar/pull/650) ([mmo](https://github.com/mmo))
- documents: adapt import from HEP BEJUNE [\#649](https://github.com/rero/sonar/pull/649) ([mmo](https://github.com/mmo))
- search: aggregations order endpoint [\#645](https://github.com/rero/sonar/pull/645) ([jma](https://github.com/jma))
- organisations: fix export serialization [\#637](https://github.com/rero/sonar/pull/637) ([sebdeleze](https://github.com/sebdeleze))
- translations: update catalog [\#636](https://github.com/rero/sonar/pull/636) ([sebdeleze](https://github.com/sebdeleze))
- documents: import `unifr` records from RERO DOC [\#635](https://github.com/rero/sonar/pull/635) ([sebdeleze](https://github.com/sebdeleze))
- documents: `masked` property enhancement [\#633](https://github.com/rero/sonar/pull/633) ([sebdeleze](https://github.com/sebdeleze))
- records: configure sorting behavior [\#631](https://github.com/rero/sonar/pull/631) ([sebdeleze](https://github.com/sebdeleze))
- api: search swisscovery records [\#630](https://github.com/rero/sonar/pull/630) ([sebdeleze](https://github.com/sebdeleze))
- deposit: add a call to action [\#629](https://github.com/rero/sonar/pull/629) ([sebdeleze](https://github.com/sebdeleze))
- documents: import records from HEP BEJUNE [\#628](https://github.com/rero/sonar/pull/628) ([sebdeleze](https://github.com/sebdeleze))
- docker: change always to unless-stopped on restart parameter [\#627](https://github.com/rero/sonar/pull/627) ([Garfield-fr](https://github.com/Garfield-fr))
- accounts: password forgotten emails [\#615](https://github.com/rero/sonar/pull/615) ([sebdeleze](https://github.com/sebdeleze))
- documents: fix `partOf` format [\#614](https://github.com/rero/sonar/pull/614) ([sebdeleze](https://github.com/sebdeleze))
- deposits: change validation process emails [\#613](https://github.com/rero/sonar/pull/613) ([sebdeleze](https://github.com/sebdeleze))
- contributors: add suggestions for name [\#612](https://github.com/rero/sonar/pull/612) ([sebdeleze](https://github.com/sebdeleze))
- subdivisions: create resource [\#606](https://github.com/rero/sonar/pull/606) ([sebdeleze](https://github.com/sebdeleze))
- stats: collect and display stats for organisations [\#594](https://github.com/rero/sonar/pull/594) ([sebdeleze](https://github.com/sebdeleze))

# Changelog

## [v1.3.0](https://github.com/rero/sonar/tree/v1.3.0) (2021-08-03)

[Full Changelog](https://github.com/rero/sonar/compare/v1.2.0...v1.3.0)

**Fixed bugs:**

- Error after PDF extraction in deposits [\#603](https://github.com/rero/sonar/issues/603)

**Closed issues:**

- Create Uni Fribourg dedicated view [\#605](https://github.com/rero/sonar/issues/605)
- Mask a document from the public view [\#570](https://github.com/rero/sonar/issues/570)

**Merged pull requests:**

- translations: update catalog [\#618](https://github.com/rero/sonar/pull/618) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalog [\#617](https://github.com/rero/sonar/pull/617) ([sebastiendeleze](https://github.com/sebastiendeleze))
- security: update dependencies [\#616](https://github.com/rero/sonar/pull/616) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: remove an organisation [\#611](https://github.com/rero/sonar/pull/611) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: dedicated view for `bcufr` [\#608](https://github.com/rero/sonar/pull/608) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: fix PDF date extraction [\#604](https://github.com/rero/sonar/pull/604) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: add `masked` property [\#601](https://github.com/rero/sonar/pull/601) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v1.2.0](https://github.com/rero/sonar/tree/v1.2.0) (2021-07-14)

[Full Changelog](https://github.com/rero/sonar/compare/v1.1.1...v1.2.0)

**Implemented enhancements:**

- Keywords and classifications are clickable [\#367](https://github.com/rero/sonar/issues/367)

**Fixed bugs:**

- Facets are not translated when the language is changed [\#598](https://github.com/rero/sonar/issues/598)
- Research projects  not correct in document editor [\#593](https://github.com/rero/sonar/issues/593)
- Hide the Dewey classification [\#550](https://github.com/rero/sonar/issues/550)

**Closed issues:**

- Create dedicated view HEP-BEJUNE [\#571](https://github.com/rero/sonar/issues/571)

**Merged pull requests:**

- translations: update catalog [\#602](https://github.com/rero/sonar/pull/602) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: subjects search [\#599](https://github.com/rero/sonar/pull/599) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: hide Dewey classification [\#597](https://github.com/rero/sonar/pull/597) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: fix projects typehead [\#595](https://github.com/rero/sonar/pull/595) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: dedicated view for HEP BEJUNE. [\#591](https://github.com/rero/sonar/pull/591) ([sebastiendeleze](https://github.com/sebastiendeleze))
- vge: add sources for OAI harvesting from RERO DOC [\#590](https://github.com/rero/sonar/pull/590) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v1.1.1](https://github.com/rero/sonar/tree/v1.1.1) (2021-06-16)

[Full Changelog](https://github.com/rero/sonar/compare/v1.1.0...v1.1.1)

**Merged pull requests:**

- documents: fix license for RERO DOC publications [\#587](https://github.com/rero/sonar/pull/587) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v1.1.0](https://github.com/rero/sonar/tree/v1.1.0) (2021-06-16)

[Full Changelog](https://github.com/rero/sonar/compare/v1.0.0...v1.1.0)

**Implemented enhancements:**

- Hide `hiddenFromPublic` field on document editor [\#537](https://github.com/rero/sonar/issues/537)
- Improve monitoring [\#502](https://github.com/rero/sonar/issues/502)

**Fixed bugs:**

- Facets with `invenio-records-resources` don't work as expected [\#554](https://github.com/rero/sonar/issues/554)
- Controlled affiliations are not shown in the interface and can be edited [\#541](https://github.com/rero/sonar/issues/541)
- Button "Search in full-text" is ineffective [\#510](https://github.com/rero/sonar/issues/510)
- Dedicated context is lost, when coming back to public interface from administration. [\#499](https://github.com/rero/sonar/issues/499)
- The language change in the admin interface does not work properly. [\#493](https://github.com/rero/sonar/issues/493)
- The admin has no full permissions to update his/her own organisation. [\#492](https://github.com/rero/sonar/issues/492)
- The suppression of a user as an admin does not really delete the user. [\#491](https://github.com/rero/sonar/issues/491)

**Closed issues:**

- Custom homepage template for organisation [\#583](https://github.com/rero/sonar/issues/583)
- Improve deposit editor [\#569](https://github.com/rero/sonar/issues/569)
- Remove default project entry in deposit process [\#560](https://github.com/rero/sonar/issues/560)
- Mark documents as `harvested` when they are import from an external source [\#556](https://github.com/rero/sonar/issues/556)
- Set the current language based on the `lang` cookie [\#535](https://github.com/rero/sonar/issues/535)
- Import BGE records from RERODOC [\#528](https://github.com/rero/sonar/issues/528)
- Change the way select options are hierarchized [\#530](https://github.com/rero/sonar/issues/530)
- Allow the definition of custom collections [\#521](https://github.com/rero/sonar/issues/521)
- Allow the definition of custom metadata fields and facets \[5\] [\#512](https://github.com/rero/sonar/issues/512)
- Add "Open access" button above the facets [\#511](https://github.com/rero/sonar/issues/511)
- Organisation editor: adjust the caption text of the field "Allowed IP addresses" [\#495](https://github.com/rero/sonar/issues/495)
- Create maintenance page [\#481](https://github.com/rero/sonar/issues/481)
- Create dedicated view HEP-VS [\#459](https://github.com/rero/sonar/issues/459)
- Authentication by API key for requesting API endpoints. [\#415](https://github.com/rero/sonar/issues/415)
- Every deposited document is assigned a persistent identifier \(ARK\) \[5\] [\#399](https://github.com/rero/sonar/issues/399)
- Record validation workflow [\#457](https://github.com/rero/sonar/issues/457)
- Export search results in CSV [\#456](https://github.com/rero/sonar/issues/456)
- Adapt detailed views for projects [\#455](https://github.com/rero/sonar/issues/455)
- Add / Edit custom project [\#454](https://github.com/rero/sonar/issues/454)

**Merged pull requests:**

- homepage: custom description for organisations [\#585](https://github.com/rero/sonar/pull/585) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalog [\#584](https://github.com/rero/sonar/pull/584) ([sebastiendeleze](https://github.com/sebastiendeleze))
- ui: update scripts [\#580](https://github.com/rero/sonar/pull/580) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: configure markdown fields [\#579](https://github.com/rero/sonar/pull/579) ([sebastiendeleze](https://github.com/sebastiendeleze))
- json schemas: force the cache to be cleared. [\#578](https://github.com/rero/sonar/pull/578) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: improve editor and process [\#577](https://github.com/rero/sonar/pull/577) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: fix controlled affiliations [\#574](https://github.com/rero/sonar/pull/574) ([sebastiendeleze](https://github.com/sebastiendeleze))
- tests: fix temporarly safety check [\#572](https://github.com/rero/sonar/pull/572) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: add `collection` resource [\#566](https://github.com/rero/sonar/pull/566) ([sebastiendeleze](https://github.com/sebastiendeleze))
- templates: add language value filter [\#565](https://github.com/rero/sonar/pull/565) ([sebastiendeleze](https://github.com/sebastiendeleze))
- assets: remove manifest fix [\#564](https://github.com/rero/sonar/pull/564) ([sebastiendeleze](https://github.com/sebastiendeleze))
- assets: copy manifest.json to fix webpack error [\#563](https://github.com/rero/sonar/pull/563) ([sebastiendeleze](https://github.com/sebastiendeleze))
- identifiers: add ARK identifiers [\#561](https://github.com/rero/sonar/pull/561) ([jma](https://github.com/jma))
- translations: update catalog [\#558](https://github.com/rero/sonar/pull/558) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: flag record as `harvested` [\#557](https://github.com/rero/sonar/pull/557) ([sebastiendeleze](https://github.com/sebastiendeleze))
- resources: apply filters [\#555](https://github.com/rero/sonar/pull/555) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: CSV export for projects [\#553](https://github.com/rero/sonar/pull/553) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: dedicated view for HEP Valais. [\#552](https://github.com/rero/sonar/pull/552) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: validation workflow [\#549](https://github.com/rero/sonar/pull/549) ([sebastiendeleze](https://github.com/sebastiendeleze))
- view: change the view routes [\#533](https://github.com/rero/sonar/pull/533) ([jma](https://github.com/jma))
- json schemas: configure options tree for select [\#531](https://github.com/rero/sonar/pull/531) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: import BGE set from RERODOC [\#529](https://github.com/rero/sonar/pull/529) ([sebastiendeleze](https://github.com/sebastiendeleze))
- search: suggestions completion API endpoint [\#527](https://github.com/rero/sonar/pull/527) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: create custom resource for HEP-VS [\#526](https://github.com/rero/sonar/pull/526) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: custom fields for documents [\#525](https://github.com/rero/sonar/pull/525) ([sebastiendeleze](https://github.com/sebastiendeleze))
- dependencies: fix security issues [\#524](https://github.com/rero/sonar/pull/524) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalog [\#520](https://github.com/rero/sonar/pull/520) ([sebastiendeleze](https://github.com/sebastiendeleze))
- search: add filter for open access documents [\#519](https://github.com/rero/sonar/pull/519) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: editor for HEP Valais [\#517](https://github.com/rero/sonar/pull/517) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: improve indexing [\#513](https://github.com/rero/sonar/pull/513) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalog [\#509](https://github.com/rero/sonar/pull/509) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: refactor resource [\#508](https://github.com/rero/sonar/pull/508) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: upgrade to Invenio 3.4 [\#505](https://github.com/rero/sonar/pull/505) ([sebastiendeleze](https://github.com/sebastiendeleze))
- monitoring: improve returned information [\#503](https://github.com/rero/sonar/pull/503) ([sebastiendeleze](https://github.com/sebastiendeleze))
- stats: configure stats for documents and files [\#501](https://github.com/rero/sonar/pull/501) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: update `allowedIps` description [\#500](https://github.com/rero/sonar/pull/500) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: remove Flask user [\#498](https://github.com/rero/sonar/pull/498) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: fix editor with admin role [\#497](https://github.com/rero/sonar/pull/497) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: create REST endpoint [\#494](https://github.com/rero/sonar/pull/494) ([sebastiendeleze](https://github.com/sebastiendeleze))
- user: enable applications menu entry [\#490](https://github.com/rero/sonar/pull/490) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: theme for VGE [\#488](https://github.com/rero/sonar/pull/488) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v1.0.0](https://github.com/rero/sonar/tree/v1.0.0) (2021-02-16)

[Full Changelog](https://github.com/rero/sonar/compare/v0.7.0...v1.0.0)

**Implemented enhancements:**

- Improve responsive display [\#474](https://github.com/rero/sonar/issues/474)
- Set a limit for upload size to 500 Mo [\#412](https://github.com/rero/sonar/issues/412)
- DOI are clickable in the detailed views \(public and pro\) [\#403](https://github.com/rero/sonar/issues/403)
- Classification must NOT be required in document editor [\#395](https://github.com/rero/sonar/issues/395)
- Adjustments in the deposit form [\#387](https://github.com/rero/sonar/issues/387)
- Display a small header for SONAR when we are in organisation's view [\#385](https://github.com/rero/sonar/issues/385)
- A "Back to results" button is missing in the detailed record view [\#383](https://github.com/rero/sonar/issues/383)
- Correct message "Welcome on SONAR" [\#350](https://github.com/rero/sonar/issues/350)
- Provision activity in deposit editor must be improved. [\#310](https://github.com/rero/sonar/issues/310)
- Explode last name and first name for users. [\#222](https://github.com/rero/sonar/issues/222)
- permissions: improve permissions checks [\#482](https://github.com/rero/sonar/pull/482) ([sebastiendeleze](https://github.com/sebastiendeleze))
- design: improve responsive display [\#477](https://github.com/rero/sonar/pull/477) ([sebastiendeleze](https://github.com/sebastiendeleze))
- HEG import: split files [\#468](https://github.com/rero/sonar/pull/468) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: avoid log in sentry [\#449](https://github.com/rero/sonar/pull/449) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: separate first name and last name. [\#445](https://github.com/rero/sonar/pull/445) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: allow multiple organisations [\#442](https://github.com/rero/sonar/pull/442) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: set DOI clickable [\#441](https://github.com/rero/sonar/pull/441) ([sebastiendeleze](https://github.com/sebastiendeleze))
- mappings: set shards and replicas values [\#430](https://github.com/rero/sonar/pull/430) ([sebastiendeleze](https://github.com/sebastiendeleze))
- rerodoc: default document type for thesis [\#424](https://github.com/rero/sonar/pull/424) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: improve editor [\#421](https://github.com/rero/sonar/pull/421) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: improve editor [\#420](https://github.com/rero/sonar/pull/420) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: change welcome subject [\#388](https://github.com/rero/sonar/pull/388) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: display a small header [\#386](https://github.com/rero/sonar/pull/386) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: add a back button in detail views [\#384](https://github.com/rero/sonar/pull/384) ([sebastiendeleze](https://github.com/sebastiendeleze))

**Fixed bugs:**

- Wrong controlled affiliation is sometimes set [\#465](https://github.com/rero/sonar/issues/465)
- Hide records which have no file attached, only if imported from HEG [\#464](https://github.com/rero/sonar/issues/464)
- Remove markup from abstracts [\#461](https://github.com/rero/sonar/issues/461)
- The links of the table of content in the documentation are not working. [\#450](https://github.com/rero/sonar/issues/450)
- Email check is case sensitive when try to login with a switch edu-ID account [\#397](https://github.com/rero/sonar/issues/397)
- Field "identifiedBy" for contributions is not editable in the document's form [\#396](https://github.com/rero/sonar/issues/396)
- Some controlled affiliations are not correct. [\#362](https://github.com/rero/sonar/issues/362)
- Documents from RERO DOC don't have a type in SONAR. [\#361](https://github.com/rero/sonar/issues/361)
- HEG import: remove markup from abstract [\#472](https://github.com/rero/sonar/pull/472) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: fix controlled affiliation matching [\#471](https://github.com/rero/sonar/pull/471) ([sebastiendeleze](https://github.com/sebastiendeleze))
- HEG import: fix `es` language code [\#467](https://github.com/rero/sonar/pull/467) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: add `hiddenToPublic` property [\#466](https://github.com/rero/sonar/pull/466) ([sebastiendeleze](https://github.com/sebastiendeleze))
- help: fix TOC links [\#453](https://github.com/rero/sonar/pull/453) ([sebastiendeleze](https://github.com/sebastiendeleze))
- authentication: fix Switch edu-ID authentication [\#444](https://github.com/rero/sonar/pull/444) ([sebastiendeleze](https://github.com/sebastiendeleze))

**Closed issues:**

- Update frontpage [\#476](https://github.com/rero/sonar/issues/476)
- Document endpoints for API REST. [\#458](https://github.com/rero/sonar/issues/458)
- Monitoring to get differences between DB and ES. [\#448](https://github.com/rero/sonar/issues/448)
- Install GitHub stale workflow. [\#446](https://github.com/rero/sonar/issues/446)
- PMC and CrossRef metadata import [\#407](https://github.com/rero/sonar/issues/407)
- Implements OAI PMH harvesting from swiss IRs from two sources [\#371](https://github.com/rero/sonar/issues/371)
- Sign in / Sign up distinction [\#365](https://github.com/rero/sonar/issues/365)
- Errors during importation from RERODOC [\#294](https://github.com/rero/sonar/issues/294)
- Test API request time with permissions loading and 1000 records. [\#245](https://github.com/rero/sonar/issues/245)
- Analyse collections handling [\#142](https://github.com/rero/sonar/issues/142)
- Optimize pages for referencing [\#112](https://github.com/rero/sonar/issues/112)
- Optimize pages loading speed and resources loading. [\#111](https://github.com/rero/sonar/issues/111)
- Searches [\#391](https://github.com/rero/sonar/issues/391)
- Lists [\#390](https://github.com/rero/sonar/issues/390)
- Alerts [\#389](https://github.com/rero/sonar/issues/389)
- Specific collections [\#392](https://github.com/rero/sonar/issues/392)
- Snippets [\#393](https://github.com/rero/sonar/issues/393)
- Implement an advanced search [\#394](https://github.com/rero/sonar/issues/394)
- Check the roll-over of the SAML IdP certificate of the SWITCH edu-ID IdP [\#434](https://github.com/rero/sonar/issues/434)
- Import data from HEG sets [\#429](https://github.com/rero/sonar/issues/429)
- Permalink RERO DOC? \(Besoin USI, à discuter avec @mmo\) [\#411](https://github.com/rero/sonar/issues/411)
- Finalize the IT environment for production [\#398](https://github.com/rero/sonar/issues/398)
- Push generated files to Webdav endpoint [\#378](https://github.com/rero/sonar/issues/378)
- Harvest data from BORIS \(Bern\) and Archive ouverte UNIGE [\#374](https://github.com/rero/sonar/issues/374)
- Implement the "project" section in deposit and document [\#358](https://github.com/rero/sonar/issues/358)
- Add a favicon [\#121](https://github.com/rero/sonar/issues/121)
- Add google tags for analytics tracking [\#109](https://github.com/rero/sonar/issues/109)
- Remove "Software under development!" banner [\#107](https://github.com/rero/sonar/issues/107)
- Export data for Google scholar, Google books, ... [\#99](https://github.com/rero/sonar/issues/99)
- Add schema.org metadata [\#98](https://github.com/rero/sonar/issues/98)
- DEV and TEST subdomains [\#19](https://github.com/rero/sonar/issues/19)

**Merged pull requests:**

- translations: update catalog [\#489](https://github.com/rero/sonar/pull/489) ([sebastiendeleze](https://github.com/sebastiendeleze))
- dependencies: upgrade `sonar-ui` [\#485](https://github.com/rero/sonar/pull/485) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: update copyright year [\#484](https://github.com/rero/sonar/pull/484) ([sebastiendeleze](https://github.com/sebastiendeleze))
- editor: update JSON schema properties [\#483](https://github.com/rero/sonar/pull/483) ([sebastiendeleze](https://github.com/sebastiendeleze))
- docker: force upgrade pip [\#480](https://github.com/rero/sonar/pull/480) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: optimize loading speed and SEO [\#479](https://github.com/rero/sonar/pull/479) ([sebastiendeleze](https://github.com/sebastiendeleze))
- ci: fix `xpdf` installation error [\#478](https://github.com/rero/sonar/pull/478) ([sebastiendeleze](https://github.com/sebastiendeleze))
- monitoring: data integrity and DB connections [\#475](https://github.com/rero/sonar/pull/475) ([sebastiendeleze](https://github.com/sebastiendeleze))
- frontpage: remove banner [\#469](https://github.com/rero/sonar/pull/469) ([sebastiendeleze](https://github.com/sebastiendeleze))
- dependencies: ignore vulnerability [\#463](https://github.com/rero/sonar/pull/463) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalogs [\#462](https://github.com/rero/sonar/pull/462) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: add metadata in detail view [\#460](https://github.com/rero/sonar/pull/460) ([sebastiendeleze](https://github.com/sebastiendeleze))
- gh actions: set the stale workflow [\#447](https://github.com/rero/sonar/pull/447) ([sebastiendeleze](https://github.com/sebastiendeleze))
- google analytics: add tracking code [\#440](https://github.com/rero/sonar/pull/440) ([sebastiendeleze](https://github.com/sebastiendeleze))
- es: backup and restore [\#438](https://github.com/rero/sonar/pull/438) ([sebastiendeleze](https://github.com/sebastiendeleze))
- ci: fix coveralls issue [\#437](https://github.com/rero/sonar/pull/437) ([sebastiendeleze](https://github.com/sebastiendeleze))
- ci: switch to GitHub Actions [\#436](https://github.com/rero/sonar/pull/436) ([sebastiendeleze](https://github.com/sebastiendeleze))
- db: drop tables instead of drop database [\#432](https://github.com/rero/sonar/pull/432) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: harvest records from HEG [\#431](https://github.com/rero/sonar/pull/431) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: add favicon [\#428](https://github.com/rero/sonar/pull/428) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: RERODOC permalink [\#425](https://github.com/rero/sonar/pull/425) ([sebastiendeleze](https://github.com/sebastiendeleze))
- Spelling: i.e x4, -to which x2 [\#422](https://github.com/rero/sonar/pull/422) ([comradekingu](https://github.com/comradekingu))
- dependency: fix security issue [\#418](https://github.com/rero/sonar/pull/418) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalogs [\#380](https://github.com/rero/sonar/pull/380) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: harvest from 2 sources [\#376](https://github.com/rero/sonar/pull/376) ([sebastiendeleze](https://github.com/sebastiendeleze))
- projects: add resource [\#372](https://github.com/rero/sonar/pull/372) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.7.0](https://github.com/rero/sonar/tree/v0.7.0) (2020-11-13)

[Full Changelog](https://github.com/rero/sonar/compare/v0.6.0...v0.7.0)

**Closed issues:**

- Other files are not well displayed in the document's detail view [\#357](https://github.com/rero/sonar/issues/357)
- Restore backups for organisations and users after a new setup [\#356](https://github.com/rero/sonar/issues/356)
- Field contributor should not be required in deposit form [\#352](https://github.com/rero/sonar/issues/352)
- Disallow modify isDedicated and isShared properties for non superusers. [\#351](https://github.com/rero/sonar/issues/351)
- Upgrade Invenio to version 3.3 and Elasticsearch to version 7 [\#345](https://github.com/rero/sonar/issues/345)
- ORCID must support X as last caracter. [\#342](https://github.com/rero/sonar/issues/342)
- Move from pipenv to poetry [\#341](https://github.com/rero/sonar/issues/341)
- File formats [\#339](https://github.com/rero/sonar/issues/339)
- Conferences should be displayed with number, place and date [\#338](https://github.com/rero/sonar/issues/338)
- Bookmarks are not well displayed in PDF previews [\#336](https://github.com/rero/sonar/issues/336)
- Time zone is wrong for dates in the logs of deposits. [\#333](https://github.com/rero/sonar/issues/333)
- Upgrade to celery 5 [\#331](https://github.com/rero/sonar/issues/331)
- Check files permissions [\#328](https://github.com/rero/sonar/issues/328)
- OAI-PMH Export format in Dublin Core \(DC\) [\#325](https://github.com/rero/sonar/issues/325)
- Add field licence on step "diffusion" of deposit [\#324](https://github.com/rero/sonar/issues/324)
- Accept all file formats for documents [\#322](https://github.com/rero/sonar/issues/322)
- Translate values for 'organisation' facet [\#320](https://github.com/rero/sonar/issues/320)
- Order records by date by default if no query specified [\#318](https://github.com/rero/sonar/issues/318)
- Do not create user ressource when invenio account is created [\#314](https://github.com/rero/sonar/issues/314)
- OAI-PMH Automatic creation sets for organisation [\#311](https://github.com/rero/sonar/issues/311)
- Import documents to organisation "usi" and not "unisi" when harvesting from rerodoc [\#308](https://github.com/rero/sonar/issues/308)
- For dedicated repository, avoid error when the custom styles file does not exist [\#307](https://github.com/rero/sonar/issues/307)
- Add a facet to search user not attached to an organisation [\#305](https://github.com/rero/sonar/issues/305)
- Add translation context during messages extraction [\#302](https://github.com/rero/sonar/issues/302)
- Ensure that file with lowest order is considered as the main file. [\#300](https://github.com/rero/sonar/issues/300)
- Possibility to add/edit metadata for files [\#280](https://github.com/rero/sonar/issues/280)
- Retrieve roles from invenio-access instead of storing them into User API class [\#244](https://github.com/rero/sonar/issues/244)
- \[2\] @rerowep suggested to upgrade to ES 7.6.2 [\#224](https://github.com/rero/sonar/issues/224)

**Merged pull requests:**

- documents: fix contributions in editor. [\#369](https://github.com/rero/sonar/pull/369) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalogs [\#368](https://github.com/rero/sonar/pull/368) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: restore data [\#364](https://github.com/rero/sonar/pull/364) ([sebastiendeleze](https://github.com/sebastiendeleze))
- dependencies: fix version for `importlib-metadata` [\#360](https://github.com/rero/sonar/pull/360) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalogs [\#359](https://github.com/rero/sonar/pull/359) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: meeting display [\#355](https://github.com/rero/sonar/pull/355) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: contributors are not required [\#354](https://github.com/rero/sonar/pull/354) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: validate modes update [\#353](https://github.com/rero/sonar/pull/353) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: fix ORCID format [\#348](https://github.com/rero/sonar/pull/348) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: upgrade invenio and elasticsearch [\#347](https://github.com/rero/sonar/pull/347) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: use poetry [\#344](https://github.com/rero/sonar/pull/344) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: export records in Dublic Core format [\#340](https://github.com/rero/sonar/pull/340) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: Customize PDF preview styles [\#337](https://github.com/rero/sonar/pull/337) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: fix log date format [\#335](https://github.com/rero/sonar/pull/335) ([sebastiendeleze](https://github.com/sebastiendeleze))
- dependencies: update celery to version 5 [\#332](https://github.com/rero/sonar/pull/332) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalogs [\#330](https://github.com/rero/sonar/pull/330) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: improve files permissions [\#329](https://github.com/rero/sonar/pull/329) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: add license [\#327](https://github.com/rero/sonar/pull/327) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: configure OAI sets [\#326](https://github.com/rero/sonar/pull/326) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: handle several file formats [\#323](https://github.com/rero/sonar/pull/323) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: update name in organisation facet [\#321](https://github.com/rero/sonar/pull/321) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: sort by most recent descending by default [\#319](https://github.com/rero/sonar/pull/319) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: fix thumbnail without external URL [\#317](https://github.com/rero/sonar/pull/317) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: avoid create user resource [\#315](https://github.com/rero/sonar/pull/315) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: update catalogs [\#313](https://github.com/rero/sonar/pull/313) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: rename `unisi` to `usi` [\#309](https://github.com/rero/sonar/pull/309) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: facet for users without organisation [\#306](https://github.com/rero/sonar/pull/306) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: add context when extracting messages [\#304](https://github.com/rero/sonar/pull/304) ([sebastiendeleze](https://github.com/sebastiendeleze))
- Translations update from Weblate [\#303](https://github.com/rero/sonar/pull/303) ([weblate](https://github.com/weblate))
- documents: order files [\#301](https://github.com/rero/sonar/pull/301) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: configure `\_files` in JSON schema [\#299](https://github.com/rero/sonar/pull/299) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: fix files permissions CLI [\#298](https://github.com/rero/sonar/pull/298) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: refactor file handling [\#297](https://github.com/rero/sonar/pull/297) ([sebastiendeleze](https://github.com/sebastiendeleze))
- imports: change PMID identifier [\#296](https://github.com/rero/sonar/pull/296) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: add option to force harvesting records [\#295](https://github.com/rero/sonar/pull/295) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.6.0](https://github.com/rero/sonar/tree/v0.6.0) (2020-09-08)

[Full Changelog](https://github.com/rero/sonar/compare/v0.5.0...v0.6.0)

**Closed issues:**

- Permalink in document detail point to a 404 [\#282](https://github.com/rero/sonar/issues/282)
- Problem with users with role "user" [\#273](https://github.com/rero/sonar/issues/273)
- Modifies welcome e-mail for role "user" [\#272](https://github.com/rero/sonar/issues/272)
- Fix display of provisionActivity depending on document type. [\#270](https://github.com/rero/sonar/issues/270)
- Organisation landing page [\#268](https://github.com/rero/sonar/issues/268)
- Update `dissertation` field [\#265](https://github.com/rero/sonar/issues/265)
- Extract date during import of documents [\#254](https://github.com/rero/sonar/issues/254)
- Uniformize frontend and backend brief views for the documents [\#253](https://github.com/rero/sonar/issues/253)
- Change user roles from array to string in JSON schema [\#246](https://github.com/rero/sonar/issues/246)
- Improve and correct the document editor [\#230](https://github.com/rero/sonar/issues/230)
- Uniformize frontend and admin detail views for documents [\#219](https://github.com/rero/sonar/issues/219)
- Improve the URL to access organisation view [\#215](https://github.com/rero/sonar/issues/215)
- Enhance elastic search mapping for documents [\#139](https://github.com/rero/sonar/issues/139)

**Merged pull requests:**

- translations: update catalogs [\#293](https://github.com/rero/sonar/pull/293) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: search in full-text [\#292](https://github.com/rero/sonar/pull/292) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: set default aggregation size [\#291](https://github.com/rero/sonar/pull/291) ([sebastiendeleze](https://github.com/sebastiendeleze))
- account: customize welcome e-mail [\#290](https://github.com/rero/sonar/pull/290) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: list users with no organisation [\#289](https://github.com/rero/sonar/pull/289) ([sebastiendeleze](https://github.com/sebastiendeleze))
- package: update `flask-cors` to version 3.0.9 [\#288](https://github.com/rero/sonar/pull/288) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: handle `identifiedBy` field. [\#287](https://github.com/rero/sonar/pull/287) ([sebastiendeleze](https://github.com/sebastiendeleze))
- search: enhance elasticsearch mappings [\#286](https://github.com/rero/sonar/pull/286) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: show organisation information [\#285](https://github.com/rero/sonar/pull/285) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: fix permalink [\#283](https://github.com/rero/sonar/pull/283) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: improve editor [\#281](https://github.com/rero/sonar/pull/281) ([sebastiendeleze](https://github.com/sebastiendeleze))
- editor: do not sort hierarchical options [\#279](https://github.com/rero/sonar/pull/279) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: create an associated bucket by default [\#278](https://github.com/rero/sonar/pull/278) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: improve date validation [\#277](https://github.com/rero/sonar/pull/277) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: 404 instead of raising an exception [\#276](https://github.com/rero/sonar/pull/276) ([sebastiendeleze](https://github.com/sebastiendeleze))
- styles: avoid to load styles twice. [\#275](https://github.com/rero/sonar/pull/275) ([sebastiendeleze](https://github.com/sebastiendeleze))
- navbar: add arrow for dropdown menus [\#274](https://github.com/rero/sonar/pull/274) ([sebastiendeleze](https://github.com/sebastiendeleze))
- Translations update from Weblate [\#271](https://github.com/rero/sonar/pull/271) ([weblate](https://github.com/weblate))
- help: restrict to superuser roles. [\#269](https://github.com/rero/sonar/pull/269) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: add dissertation property [\#266](https://github.com/rero/sonar/pull/266) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documentation: add a weblate badge [\#264](https://github.com/rero/sonar/pull/264) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: import start date from field `502$9`. [\#262](https://github.com/rero/sonar/pull/262) ([sebastiendeleze](https://github.com/sebastiendeleze))
- files: update the record when a file is modified [\#261](https://github.com/rero/sonar/pull/261) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: sync translations with Transifex [\#260](https://github.com/rero/sonar/pull/260) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: improve specific URL [\#259](https://github.com/rero/sonar/pull/259) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: improve detail views [\#258](https://github.com/rero/sonar/pull/258) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: limit user to one role [\#257](https://github.com/rero/sonar/pull/257) ([sebastiendeleze](https://github.com/sebastiendeleze))
- search: fix query for resources [\#256](https://github.com/rero/sonar/pull/256) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: improve scripts [\#255](https://github.com/rero/sonar/pull/255) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.5.0](https://github.com/rero/sonar/tree/v0.5.0) (2020-06-26)

[Full Changelog](https://github.com/rero/sonar/compare/v0.4.0...v0.5.0)

**Closed issues:**

- Rename publisher to submitter [\#250](https://github.com/rero/sonar/issues/250)
- Deposits improvements [\#248](https://github.com/rero/sonar/issues/248)
- Update registration email content [\#242](https://github.com/rero/sonar/issues/242)
- Allow only one role for users, as roles are hierarchical [\#241](https://github.com/rero/sonar/issues/241)
- Removes roles from user record API and use created roles in invenio-access [\#240](https://github.com/rero/sonar/issues/240)
- \[2\] Store organisation's code as additional persistent identifier for the organisation. [\#223](https://github.com/rero/sonar/issues/223)
- Create a user resource when a new account is created with registration form or oAuth [\#221](https://github.com/rero/sonar/issues/221)
- \[2\] Adds the possibility to push translation in transifex. [\#220](https://github.com/rero/sonar/issues/220)
- Page for listing deposits for the logged user [\#218](https://github.com/rero/sonar/issues/218)
- Permissions rules for accessing deposits [\#217](https://github.com/rero/sonar/issues/217)
- Possibility to access records for an organisation with a specific URL [\#216](https://github.com/rero/sonar/issues/216)
- Add a facet for searching documents by author [\#214](https://github.com/rero/sonar/issues/214)
- Add a facet for searching document by date. [\#213](https://github.com/rero/sonar/issues/213)
- Add a facet for searching documents by controlled affiliations [\#212](https://github.com/rero/sonar/issues/212)
- Improve the website design: [\#211](https://github.com/rero/sonar/issues/211)
- Custom indexer [\#209](https://github.com/rero/sonar/issues/209)
- Ability to create or link account to user record [\#204](https://github.com/rero/sonar/issues/204)
- Standardize name for organisation [\#198](https://github.com/rero/sonar/issues/198)
- Store user's organisation in document created from deposit. [\#197](https://github.com/rero/sonar/issues/197)
- Configure Flask-Wiki to store the pages on NFS volume [\#196](https://github.com/rero/sonar/issues/196)
- Configure invenio-files to store the files on NFS volume [\#195](https://github.com/rero/sonar/issues/195)
- Mount NFS volume [\#194](https://github.com/rero/sonar/issues/194)
- Re-enable sentry logs [\#193](https://github.com/rero/sonar/issues/193)
- Rules for restricting access to resources by user, role and institution [\#146](https://github.com/rero/sonar/issues/146)
- Add translations for french, german and italian [\#108](https://github.com/rero/sonar/issues/108)
- Configure ORCID for production [\#103](https://github.com/rero/sonar/issues/103)

**Merged pull requests:**

- users: rename role publisher [\#251](https://github.com/rero/sonar/pull/251) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: improve form [\#249](https://github.com/rero/sonar/pull/249) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: send welcome email [\#247](https://github.com/rero/sonar/pull/247) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: limit to only one role [\#243](https://github.com/rero/sonar/pull/243) ([sebastiendeleze](https://github.com/sebastiendeleze))
- search: add aggregations [\#239](https://github.com/rero/sonar/pull/239) ([sebastiendeleze](https://github.com/sebastiendeleze))
- design: rebrand website [\#238](https://github.com/rero/sonar/pull/238) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: add translations [\#237](https://github.com/rero/sonar/pull/237) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: Transifex integration [\#236](https://github.com/rero/sonar/pull/236) ([sebastiendeleze](https://github.com/sebastiendeleze))
- users: create user record on registration [\#235](https://github.com/rero/sonar/pull/235) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: access records with specific URL [\#234](https://github.com/rero/sonar/pull/234) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: update dependencies [\#233](https://github.com/rero/sonar/pull/233) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposits: add organisation in documents [\#231](https://github.com/rero/sonar/pull/231) ([sebastiendeleze](https://github.com/sebastiendeleze))
- user: add publisher role [\#229](https://github.com/rero/sonar/pull/229) ([sebastiendeleze](https://github.com/sebastiendeleze))
- security: add permissions for accessing resources [\#228](https://github.com/rero/sonar/pull/228) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: create default organisation [\#226](https://github.com/rero/sonar/pull/226) ([sebastiendeleze](https://github.com/sebastiendeleze))
- indexer: custom indexer [\#210](https://github.com/rero/sonar/pull/210) ([sebastiendeleze](https://github.com/sebastiendeleze))
- authentication: ORCID for production [\#208](https://github.com/rero/sonar/pull/208) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: improve form in submission process [\#207](https://github.com/rero/sonar/pull/207) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: improve editor [\#206](https://github.com/rero/sonar/pull/206) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: translate form options. [\#205](https://github.com/rero/sonar/pull/205) ([sebastiendeleze](https://github.com/sebastiendeleze))
- user: synchronize user records and security accounts [\#203](https://github.com/rero/sonar/pull/203) ([sebastiendeleze](https://github.com/sebastiendeleze))
- user: improve editor [\#202](https://github.com/rero/sonar/pull/202) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: improve serializer [\#201](https://github.com/rero/sonar/pull/201) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: improve organisation editor [\#200](https://github.com/rero/sonar/pull/200) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisation: standardize name [\#199](https://github.com/rero/sonar/pull/199) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: fix affiliations file path [\#192](https://github.com/rero/sonar/pull/192) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.4.0](https://github.com/rero/sonar/tree/v0.4.0) (2020-04-17)

[Full Changelog](https://github.com/rero/sonar/compare/v0.3.3...v0.4.0)

**Fixed bugs:**

- Error in Travis CI when update sonar-ui version [\#159](https://github.com/rero/sonar/issues/159)
- Disable access to super admin for admin users [\#125](https://github.com/rero/sonar/issues/125)

**Closed issues:**

- Initial Update [\#189](https://github.com/rero/sonar/issues/189)
- Prepare before the publication of TEST website [\#185](https://github.com/rero/sonar/issues/185)
- Create persistent storage to cluster [\#157](https://github.com/rero/sonar/issues/157)
- Import embargo information of files [\#147](https://github.com/rero/sonar/issues/147)
- Add a property to store external links for documents [\#144](https://github.com/rero/sonar/issues/144)
- Don't show files with embargo [\#143](https://github.com/rero/sonar/issues/143)
- Install flask wiki [\#138](https://github.com/rero/sonar/issues/138)
- configure smtp for sending mails in deployed instances [\#127](https://github.com/rero/sonar/issues/127)
- Change sentry key to make it work again [\#119](https://github.com/rero/sonar/issues/119)
- Remove test organizations [\#115](https://github.com/rero/sonar/issues/115)
- Modify deposit data structure to match final document structure [\#113](https://github.com/rero/sonar/issues/113)
- Create a about page [\#106](https://github.com/rero/sonar/issues/106)
- Create a contact page [\#105](https://github.com/rero/sonar/issues/105)
- Cleanup the project [\#101](https://github.com/rero/sonar/issues/101)
- Web design [\#97](https://github.com/rero/sonar/issues/97)
- Persistent identifiers [\#75](https://github.com/rero/sonar/issues/75)
- Common module between RERO ILS and SONAR [\#15](https://github.com/rero/sonar/issues/15)
- IR filter configuration [\#13](https://github.com/rero/sonar/issues/13)

**Merged pull requests:**

- security: replace pipenv check by safety. [\#191](https://github.com/rero/sonar/pull/191) ([sebastiendeleze](https://github.com/sebastiendeleze))
- accounts: add ORCID icon [\#190](https://github.com/rero/sonar/pull/190) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: prepare for publishing TEST website [\#188](https://github.com/rero/sonar/pull/188) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documentation: Flask-Wiki integration [\#187](https://github.com/rero/sonar/pull/187) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: deposit data structure finalization [\#184](https://github.com/rero/sonar/pull/184) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: check files restrictions [\#182](https://github.com/rero/sonar/pull/182) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: fix security issue in bleach library [\#181](https://github.com/rero/sonar/pull/181) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: update files permissions [\#180](https://github.com/rero/sonar/pull/180) ([sebastiendeleze](https://github.com/sebastiendeleze))
- organisations: remove test organisation [\#179](https://github.com/rero/sonar/pull/179) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.3.3](https://github.com/rero/sonar/tree/v0.3.3) (2020-03-17)

[Full Changelog](https://github.com/rero/sonar/compare/v0.3.2...v0.3.3)

**Fixed bugs:**

- Fix instability in clusters [\#158](https://github.com/rero/sonar/issues/158)

**Closed issues:**

- Import missing fields from RERODOC [\#160](https://github.com/rero/sonar/issues/160)
- Configure Switch edu-id for production [\#104](https://github.com/rero/sonar/issues/104)

**Merged pull requests:**

- documents: import missing fields from RERODOC [\#178](https://github.com/rero/sonar/pull/178) ([sebastiendeleze](https://github.com/sebastiendeleze))
- authentication: configure SWITCHaai for production [\#177](https://github.com/rero/sonar/pull/177) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: import "identifiedBy" properties [\#167](https://github.com/rero/sonar/pull/167) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.3.2](https://github.com/rero/sonar/tree/v0.3.2) (2020-03-04)

[Full Changelog](https://github.com/rero/sonar/compare/v0.3.1...v0.3.2)

**Merged pull requests:**

- deployment: install ImageMagick [\#165](https://github.com/rero/sonar/pull/165) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.3.1](https://github.com/rero/sonar/tree/v0.3.1) (2020-02-26)

[Full Changelog](https://github.com/rero/sonar/compare/v0.3.0...v0.3.1)

**Closed issues:**

- Don't display files from NL [\#161](https://github.com/rero/sonar/issues/161)

**Merged pull requests:**

- documents: external URLs [\#164](https://github.com/rero/sonar/pull/164) ([sebastiendeleze](https://github.com/sebastiendeleze))
- Preview and thumbnails [\#163](https://github.com/rero/sonar/pull/163) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.3.0](https://github.com/rero/sonar/tree/v0.3.0) (2020-02-25)

[Full Changelog](https://github.com/rero/sonar/compare/v0.2.2...v0.3.0)

**Fixed bugs:**

- Check why affiliations are not well extracted with GROBID [\#148](https://github.com/rero/sonar/issues/148)
- Show language facet [\#123](https://github.com/rero/sonar/issues/123)
- Adapt layout of password forgotten page [\#102](https://github.com/rero/sonar/issues/102)
- shibboleth: fix authentication issue [\#126](https://github.com/rero/sonar/pull/126) ([sebastiendeleze](https://github.com/sebastiendeleze))

**Closed issues:**

- Import submissions from RERODOC [\#141](https://github.com/rero/sonar/issues/141)
- Import users from RERODOC [\#140](https://github.com/rero/sonar/issues/140)
- Create the document when a deposit is validated [\#114](https://github.com/rero/sonar/issues/114)
- Re-enable marshmallow checks [\#79](https://github.com/rero/sonar/issues/79)
- Migrate data from RERO DOC [\#76](https://github.com/rero/sonar/issues/76)

**Merged pull requests:**

- project: install UI script [\#156](https://github.com/rero/sonar/pull/156) ([sebastiendeleze](https://github.com/sebastiendeleze))
- PDF extractor: Affiliation extraction [\#149](https://github.com/rero/sonar/pull/149) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: PDF metadata extraction [\#137](https://github.com/rero/sonar/pull/137) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: Create document [\#136](https://github.com/rero/sonar/pull/136) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: Import documents from RERODOC [\#135](https://github.com/rero/sonar/pull/135) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: JSON schema API endpoint [\#134](https://github.com/rero/sonar/pull/134) ([sebastiendeleze](https://github.com/sebastiendeleze))
- nginx: remove OPTIONS requests from logs. [\#133](https://github.com/rero/sonar/pull/133) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: fix languages facet display [\#132](https://github.com/rero/sonar/pull/132) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: remove unnecessary properties [\#131](https://github.com/rero/sonar/pull/131) ([sebastiendeleze](https://github.com/sebastiendeleze))
- account: password forgotten template [\#130](https://github.com/rero/sonar/pull/130) ([sebastiendeleze](https://github.com/sebastiendeleze))
- records: remove form schemas [\#129](https://github.com/rero/sonar/pull/129) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: various corrections [\#128](https://github.com/rero/sonar/pull/128) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.2.2](https://github.com/rero/sonar/tree/v0.2.2) (2020-01-16)

[Full Changelog](https://github.com/rero/sonar/compare/v0.2.1...v0.2.2)

**Merged pull requests:**

- records: integrate public search [\#122](https://github.com/rero/sonar/pull/122) ([sebastiendeleze](https://github.com/sebastiendeleze))
- documents: data model refactor [\#116](https://github.com/rero/sonar/pull/116) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.2.1](https://github.com/rero/sonar/tree/v0.2.1) (2020-01-10)

[Full Changelog](https://github.com/rero/sonar/compare/v0.2.0...v0.2.1)

**Fixed bugs:**

- Remove external calls to CSS for toastr and font-awesome [\#124](https://github.com/rero/sonar/issues/124)

**Closed issues:**

- Upgrade to invenio 3.2 [\#117](https://github.com/rero/sonar/issues/117)
- Remove invenio-theme [\#100](https://github.com/rero/sonar/issues/100)
- Change data model structure for documents [\#96](https://github.com/rero/sonar/issues/96)
- Integrate public search from sonar-ui application [\#95](https://github.com/rero/sonar/issues/95)

**Merged pull requests:**

- ui: update project name [\#120](https://github.com/rero/sonar/pull/120) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: upgrade Invenio [\#118](https://github.com/rero/sonar/pull/118) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.2.0](https://github.com/rero/sonar/tree/v0.2.0) (2019-12-30)

[Full Changelog](https://github.com/rero/sonar/compare/v0.1.0...v0.2.0)

**Closed issues:**

- API endpoint for publishing a publication [\#91](https://github.com/rero/sonar/issues/91)
- Evaluate invenio-rest for building custom endpoints [\#90](https://github.com/rero/sonar/issues/90)
- populate metadata when a file is uploaded in deposit process [\#87](https://github.com/rero/sonar/issues/87)
- Create a "Deposit" resource [\#82](https://github.com/rero/sonar/issues/82)
- Install invenio-files-rest for managing files [\#81](https://github.com/rero/sonar/issues/81)
- Document administration [\#74](https://github.com/rero/sonar/issues/74)
- Organization administration [\#73](https://github.com/rero/sonar/issues/73)
- Create default users and roles [\#70](https://github.com/rero/sonar/issues/70)
- User administration [\#68](https://github.com/rero/sonar/issues/68)
- Add link to institution [\#67](https://github.com/rero/sonar/issues/67)
- Remove user [\#66](https://github.com/rero/sonar/issues/66)
- Update user [\#65](https://github.com/rero/sonar/issues/65)
- Create user [\#64](https://github.com/rero/sonar/issues/64)
- List users [\#63](https://github.com/rero/sonar/issues/63)
- Admin layout integration [\#62](https://github.com/rero/sonar/issues/62)
- Angular testing and integration [\#61](https://github.com/rero/sonar/issues/61)
- Change license [\#60](https://github.com/rero/sonar/issues/60)
- Increase code coverage [\#57](https://github.com/rero/sonar/issues/57)
- Test yapf code formatter [\#53](https://github.com/rero/sonar/issues/53)
- Editor for bibliographic metadata [\#52](https://github.com/rero/sonar/issues/52)
- Workflow of the publication upload [\#51](https://github.com/rero/sonar/issues/51)
- Extract metadata from PDF [\#50](https://github.com/rero/sonar/issues/50)
- Italian translations [\#49](https://github.com/rero/sonar/issues/49)
- Upload a full text publication [\#43](https://github.com/rero/sonar/issues/43)
- Translations [\#28](https://github.com/rero/sonar/issues/28)
- Authentication via ORCID [\#26](https://github.com/rero/sonar/issues/26)
- Authentication via Switch Edu-ID [\#25](https://github.com/rero/sonar/issues/25)
- Project version tag [\#24](https://github.com/rero/sonar/issues/24)
- Document details [\#20](https://github.com/rero/sonar/issues/20)

**Merged pull requests:**

- deposits: various changes [\#94](https://github.com/rero/sonar/pull/94) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: review a deposit [\#93](https://github.com/rero/sonar/pull/93) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: publish a deposit [\#92](https://github.com/rero/sonar/pull/92) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deposit: extract metadata from PDF [\#89](https://github.com/rero/sonar/pull/89) ([sebastiendeleze](https://github.com/sebastiendeleze))
- resources: create deposit resource [\#88](https://github.com/rero/sonar/pull/88) ([sebastiendeleze](https://github.com/sebastiendeleze))
- files: configure Invenio files REST [\#86](https://github.com/rero/sonar/pull/86) ([sebastiendeleze](https://github.com/sebastiendeleze))
- project: add commit message template [\#80](https://github.com/rero/sonar/pull/80) ([sebastiendeleze](https://github.com/sebastiendeleze))
- webpack: custom configuration file [\#78](https://github.com/rero/sonar/pull/78) ([jma](https://github.com/jma))
- records: integrate angular UI [\#77](https://github.com/rero/sonar/pull/77) ([sebastiendeleze](https://github.com/sebastiendeleze))
- record: User resource creation [\#72](https://github.com/rero/sonar/pull/72) ([sebastiendeleze](https://github.com/sebastiendeleze))
- theming: Admin layout [\#71](https://github.com/rero/sonar/pull/71) ([sebastiendeleze](https://github.com/sebastiendeleze))
- license: Move from GPLv2 to AGPLv3 [\#69](https://github.com/rero/sonar/pull/69) ([sebastiendeleze](https://github.com/sebastiendeleze))
- document: PDF metadata extraction [\#58](https://github.com/rero/sonar/pull/58) ([sebastiendeleze](https://github.com/sebastiendeleze))

## [v0.1.0](https://github.com/rero/sonar/tree/v0.1.0) (2019-07-25)

[Full Changelog](https://github.com/rero/sonar/compare/3c557cc27626eb1a68d484f702f35023cb53a9c3...v0.1.0)

**Closed issues:**

- Authentication with the service [\#48](https://github.com/rero/sonar/issues/48)
- Test login process with Switch edu-id [\#47](https://github.com/rero/sonar/issues/47)
- Service provider configuration [\#46](https://github.com/rero/sonar/issues/46)
- Create and configure a switch edu-id account [\#45](https://github.com/rero/sonar/issues/45)
- asdf [\#44](https://github.com/rero/sonar/issues/44)
- Add command to setup script [\#42](https://github.com/rero/sonar/issues/42)
- Format all files [\#38](https://github.com/rero/sonar/issues/38)
- Language switcher [\#27](https://github.com/rero/sonar/issues/27)
- Configure coveralls.io [\#23](https://github.com/rero/sonar/issues/23)
- Remove sqlalchemy warning [\#22](https://github.com/rero/sonar/issues/22)
- Cleanup code and comments [\#18](https://github.com/rero/sonar/issues/18)
- Code coverage [\#17](https://github.com/rero/sonar/issues/17)
- Search facets [\#16](https://github.com/rero/sonar/issues/16)
- Test instance [\#14](https://github.com/rero/sonar/issues/14)
- USI data searchable [\#12](https://github.com/rero/sonar/issues/12)
- DEV instance and sub domain activation [\#3](https://github.com/rero/sonar/issues/3)

**Merged pull requests:**

- project: Release tag [\#59](https://github.com/rero/sonar/pull/59) ([sebastiendeleze](https://github.com/sebastiendeleze))
- tests: Increase code coverage [\#56](https://github.com/rero/sonar/pull/56) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: Italian translations [\#55](https://github.com/rero/sonar/pull/55) ([sebastiendeleze](https://github.com/sebastiendeleze))
- authentication: Switch edu-id authentication [\#54](https://github.com/rero/sonar/pull/54) ([sebastiendeleze](https://github.com/sebastiendeleze))
- authentication: ORCID OAuth [\#39](https://github.com/rero/sonar/pull/39) ([sebastiendeleze](https://github.com/sebastiendeleze))
-  templating: Document detail [\#37](https://github.com/rero/sonar/pull/37) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: Translations in french and german [\#33](https://github.com/rero/sonar/pull/33) ([sebastiendeleze](https://github.com/sebastiendeleze))
- translations: Language switcher [\#30](https://github.com/rero/sonar/pull/30) ([sebastiendeleze](https://github.com/sebastiendeleze))
- search: Faceted filters [\#29](https://github.com/rero/sonar/pull/29) ([sebastiendeleze](https://github.com/sebastiendeleze))
- search: USI data searchable [\#21](https://github.com/rero/sonar/pull/21) ([sebastiendeleze](https://github.com/sebastiendeleze))
- config: Sentry support [\#11](https://github.com/rero/sonar/pull/11) ([sebastiendeleze](https://github.com/sebastiendeleze))
- theming: IR specific view [\#10](https://github.com/rero/sonar/pull/10) ([sebastiendeleze](https://github.com/sebastiendeleze))
- theming: Frontpage layout [\#9](https://github.com/rero/sonar/pull/9) ([sebastiendeleze](https://github.com/sebastiendeleze))
- deployment: SONAR instance [\#8](https://github.com/rero/sonar/pull/8) ([sebastiendeleze](https://github.com/sebastiendeleze))
- tests: Travis build [\#7](https://github.com/rero/sonar/pull/7) ([sebastiendeleze](https://github.com/sebastiendeleze))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
