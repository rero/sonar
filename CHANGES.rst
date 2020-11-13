Changelog
=========

`v0.7.0 <https://github.com/rero/sonar/tree/v0.7.0>`__ (2020-11-13)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.6.0...v0.7.0>`__

**Closed issues:**

-  Other files are not well displayed in the document's detail view
   `#357 <https://github.com/rero/sonar/issues/357>`__
-  Restore backups for organisations and users after a new setup
   `#356 <https://github.com/rero/sonar/issues/356>`__
-  Field contributor should not be required in deposit form
   `#352 <https://github.com/rero/sonar/issues/352>`__
-  Disallow modify isDedicated and isShared properties for non
   superusers. `#351 <https://github.com/rero/sonar/issues/351>`__
-  Upgrade Invenio to version 3.3 and Elasticsearch to version 7
   `#345 <https://github.com/rero/sonar/issues/345>`__
-  ORCID must support X as last caracter.
   `#342 <https://github.com/rero/sonar/issues/342>`__
-  Move from pipenv to poetry
   `#341 <https://github.com/rero/sonar/issues/341>`__
-  File formats `#339 <https://github.com/rero/sonar/issues/339>`__
-  Conferences should be displayed with number, place and date
   `#338 <https://github.com/rero/sonar/issues/338>`__
-  Bookmarks are not well displayed in PDF previews
   `#336 <https://github.com/rero/sonar/issues/336>`__
-  Time zone is wrong for dates in the logs of deposits.
   `#333 <https://github.com/rero/sonar/issues/333>`__
-  Upgrade to celery 5
   `#331 <https://github.com/rero/sonar/issues/331>`__
-  Check files permissions
   `#328 <https://github.com/rero/sonar/issues/328>`__
-  OAI-PMH Export format in Dublin Core (DC)
   `#325 <https://github.com/rero/sonar/issues/325>`__
-  Add field licence on step "diffusion" of deposit
   `#324 <https://github.com/rero/sonar/issues/324>`__
-  Accept all file formats for documents
   `#322 <https://github.com/rero/sonar/issues/322>`__
-  Translate values for 'organisation' facet
   `#320 <https://github.com/rero/sonar/issues/320>`__
-  Order records by date by default if no query specified
   `#318 <https://github.com/rero/sonar/issues/318>`__
-  Do not create user ressource when invenio account is created
   `#314 <https://github.com/rero/sonar/issues/314>`__
-  OAI-PMH Automatic creation sets for organisation
   `#311 <https://github.com/rero/sonar/issues/311>`__
-  Import documents to organisation "usi" and not "unisi" when
   harvesting from rerodoc
   `#308 <https://github.com/rero/sonar/issues/308>`__
-  For dedicated repository, avoid error when the custom styles file
   does not exist `#307 <https://github.com/rero/sonar/issues/307>`__
-  Add a facet to search user not attached to an organisation
   `#305 <https://github.com/rero/sonar/issues/305>`__
-  Add translation context during messages extraction
   `#302 <https://github.com/rero/sonar/issues/302>`__
-  Ensure that file with lowest order is considered as the main file.
   `#300 <https://github.com/rero/sonar/issues/300>`__
-  Possibility to add/edit metadata for files
   `#280 <https://github.com/rero/sonar/issues/280>`__
-  Retrieve roles from invenio-access instead of storing them into User
   API class `#244 <https://github.com/rero/sonar/issues/244>`__
-  [2] @rerowep suggested to upgrade to ES 7.6.2
   `#224 <https://github.com/rero/sonar/issues/224>`__

**Merged pull requests:**

-  documents: fix contributions in editor.
   `#369 <https://github.com/rero/sonar/pull/369>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: update catalogs
   `#368 <https://github.com/rero/sonar/pull/368>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: restore data
   `#364 <https://github.com/rero/sonar/pull/364>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  dependencies: fix version for ``importlib-metadata``
   `#360 <https://github.com/rero/sonar/pull/360>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: update catalogs
   `#359 <https://github.com/rero/sonar/pull/359>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: meeting display
   `#355 <https://github.com/rero/sonar/pull/355>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposits: contributors are not required
   `#354 <https://github.com/rero/sonar/pull/354>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisations: validate modes update
   `#353 <https://github.com/rero/sonar/pull/353>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposits: fix ORCID format
   `#348 <https://github.com/rero/sonar/pull/348>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: upgrade invenio and elasticsearch
   `#347 <https://github.com/rero/sonar/pull/347>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: use poetry `#344 <https://github.com/rero/sonar/pull/344>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: export records in Dublic Core format
   `#340 <https://github.com/rero/sonar/pull/340>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: Customize PDF preview styles
   `#337 <https://github.com/rero/sonar/pull/337>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: fix log date format
   `#335 <https://github.com/rero/sonar/pull/335>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  dependencies: update celery to version 5
   `#332 <https://github.com/rero/sonar/pull/332>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: update catalogs
   `#330 <https://github.com/rero/sonar/pull/330>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: improve files permissions
   `#329 <https://github.com/rero/sonar/pull/329>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposits: add license
   `#327 <https://github.com/rero/sonar/pull/327>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: configure OAI sets
   `#326 <https://github.com/rero/sonar/pull/326>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: handle several file formats
   `#323 <https://github.com/rero/sonar/pull/323>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: update name in organisation facet
   `#321 <https://github.com/rero/sonar/pull/321>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: sort by most recent descending by default
   `#319 <https://github.com/rero/sonar/pull/319>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: fix thumbnail without external URL
   `#317 <https://github.com/rero/sonar/pull/317>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  users: avoid create user resource
   `#315 <https://github.com/rero/sonar/pull/315>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: update catalogs
   `#313 <https://github.com/rero/sonar/pull/313>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisation: rename ``unisi`` to ``usi``
   `#309 <https://github.com/rero/sonar/pull/309>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  users: facet for users without organisation
   `#306 <https://github.com/rero/sonar/pull/306>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: add context when extracting messages
   `#304 <https://github.com/rero/sonar/pull/304>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  Translations update from Weblate
   `#303 <https://github.com/rero/sonar/pull/303>`__
   (`weblate <https://github.com/weblate>`__)
-  documents: order files
   `#301 <https://github.com/rero/sonar/pull/301>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: configure ``\_files`` in JSON schema
   `#299 <https://github.com/rero/sonar/pull/299>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: fix files permissions CLI
   `#298 <https://github.com/rero/sonar/pull/298>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: refactor file handling
   `#297 <https://github.com/rero/sonar/pull/297>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  imports: change PMID identifier
   `#296 <https://github.com/rero/sonar/pull/296>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: add option to force harvesting records
   `#295 <https://github.com/rero/sonar/pull/295>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.6.0 <https://github.com/rero/sonar/tree/v0.6.0>`__ (2020-09-08)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.5.0...v0.6.0>`__

**Closed issues:**

-  Permalink in document detail point to a 404
   `#282 <https://github.com/rero/sonar/issues/282>`__
-  Problem with users with role "user"
   `#273 <https://github.com/rero/sonar/issues/273>`__
-  Modifies welcome e-mail for role "user"
   `#272 <https://github.com/rero/sonar/issues/272>`__
-  Fix display of provisionActivity depending on document type.
   `#270 <https://github.com/rero/sonar/issues/270>`__
-  Organisation landing page
   `#268 <https://github.com/rero/sonar/issues/268>`__
-  Update ``dissertation`` field
   `#265 <https://github.com/rero/sonar/issues/265>`__
-  Extract date during import of documents
   `#254 <https://github.com/rero/sonar/issues/254>`__
-  Uniformize frontend and backend brief views for the documents
   `#253 <https://github.com/rero/sonar/issues/253>`__
-  Change user roles from array to string in JSON schema
   `#246 <https://github.com/rero/sonar/issues/246>`__
-  Improve and correct the document editor
   `#230 <https://github.com/rero/sonar/issues/230>`__
-  Uniformize frontend and admin detail views for documents
   `#219 <https://github.com/rero/sonar/issues/219>`__
-  Improve the URL to access organisation view
   `#215 <https://github.com/rero/sonar/issues/215>`__
-  Enhance elastic search mapping for documents
   `#139 <https://github.com/rero/sonar/issues/139>`__

**Merged pull requests:**

-  translations: update catalogs
   `#293 <https://github.com/rero/sonar/pull/293>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: search in full-text
   `#292 <https://github.com/rero/sonar/pull/292>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: set default aggregation size
   `#291 <https://github.com/rero/sonar/pull/291>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  account: customize welcome e-mail
   `#290 <https://github.com/rero/sonar/pull/290>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  users: list users with no organisation
   `#289 <https://github.com/rero/sonar/pull/289>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  package: update ``flask-cors`` to version 3.0.9
   `#288 <https://github.com/rero/sonar/pull/288>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposits: handle ``identifiedBy`` field.
   `#287 <https://github.com/rero/sonar/pull/287>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  search: enhance elasticsearch mappings
   `#286 <https://github.com/rero/sonar/pull/286>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisations: show organisation information
   `#285 <https://github.com/rero/sonar/pull/285>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: fix permalink
   `#283 <https://github.com/rero/sonar/pull/283>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: improve editor
   `#281 <https://github.com/rero/sonar/pull/281>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  editor: do not sort hierarchical options
   `#279 <https://github.com/rero/sonar/pull/279>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: create an associated bucket by default
   `#278 <https://github.com/rero/sonar/pull/278>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: improve date validation
   `#277 <https://github.com/rero/sonar/pull/277>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisation: 404 instead of raising an exception
   `#276 <https://github.com/rero/sonar/pull/276>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  styles: avoid to load styles twice.
   `#275 <https://github.com/rero/sonar/pull/275>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  navbar: add arrow for dropdown menus
   `#274 <https://github.com/rero/sonar/pull/274>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  Translations update from Weblate
   `#271 <https://github.com/rero/sonar/pull/271>`__
   (`weblate <https://github.com/weblate>`__)
-  help: restrict to superuser roles.
   `#269 <https://github.com/rero/sonar/pull/269>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: add dissertation property
   `#266 <https://github.com/rero/sonar/pull/266>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documentation: add a weblate badge
   `#264 <https://github.com/rero/sonar/pull/264>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: import start date from field ``502$9``.
   `#262 <https://github.com/rero/sonar/pull/262>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  files: update the record when a file is modified
   `#261 <https://github.com/rero/sonar/pull/261>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: sync translations with Transifex
   `#260 <https://github.com/rero/sonar/pull/260>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisation: improve specific URL
   `#259 <https://github.com/rero/sonar/pull/259>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: improve detail views
   `#258 <https://github.com/rero/sonar/pull/258>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  users: limit user to one role
   `#257 <https://github.com/rero/sonar/pull/257>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  search: fix query for resources
   `#256 <https://github.com/rero/sonar/pull/256>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: improve scripts
   `#255 <https://github.com/rero/sonar/pull/255>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.5.0 <https://github.com/rero/sonar/tree/v0.5.0>`__ (2020-06-26)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.4.0...v0.5.0>`__

**Closed issues:**

-  Rename publisher to submitter
   `#250 <https://github.com/rero/sonar/issues/250>`__
-  Deposits improvements
   `#248 <https://github.com/rero/sonar/issues/248>`__
-  Update registration email content
   `#242 <https://github.com/rero/sonar/issues/242>`__
-  Allow only one role for users, as roles are hierarchical
   `#241 <https://github.com/rero/sonar/issues/241>`__
-  Removes roles from user record API and use created roles in
   invenio-access `#240 <https://github.com/rero/sonar/issues/240>`__
-  [2] Store organisation's code as additional persistent identifier for
   the organisation. `#223 <https://github.com/rero/sonar/issues/223>`__
-  Create a user resource when a new account is created with
   registration form or oAuth
   `#221 <https://github.com/rero/sonar/issues/221>`__
-  [2] Adds the possibility to push translation in transifex.
   `#220 <https://github.com/rero/sonar/issues/220>`__
-  Page for listing deposits for the logged user
   `#218 <https://github.com/rero/sonar/issues/218>`__
-  Permissions rules for accessing deposits
   `#217 <https://github.com/rero/sonar/issues/217>`__
-  Possibility to access records for an organisation with a specific URL
   `#216 <https://github.com/rero/sonar/issues/216>`__
-  Add a facet for searching documents by author
   `#214 <https://github.com/rero/sonar/issues/214>`__
-  Add a facet for searching document by date.
   `#213 <https://github.com/rero/sonar/issues/213>`__
-  Add a facet for searching documents by controlled affiliations
   `#212 <https://github.com/rero/sonar/issues/212>`__
-  Improve the website design:
   `#211 <https://github.com/rero/sonar/issues/211>`__
-  Custom indexer `#209 <https://github.com/rero/sonar/issues/209>`__
-  Ability to create or link account to user record
   `#204 <https://github.com/rero/sonar/issues/204>`__
-  Standardize name for organisation
   `#198 <https://github.com/rero/sonar/issues/198>`__
-  Store user's organisation in document created from deposit.
   `#197 <https://github.com/rero/sonar/issues/197>`__
-  Configure Flask-Wiki to store the pages on NFS volume
   `#196 <https://github.com/rero/sonar/issues/196>`__
-  Configure invenio-files to store the files on NFS volume
   `#195 <https://github.com/rero/sonar/issues/195>`__
-  Mount NFS volume `#194 <https://github.com/rero/sonar/issues/194>`__
-  Re-enable sentry logs
   `#193 <https://github.com/rero/sonar/issues/193>`__
-  Rules for restricting access to resources by user, role and
   institution `#146 <https://github.com/rero/sonar/issues/146>`__
-  Add translations for french, german and italian
   `#108 <https://github.com/rero/sonar/issues/108>`__
-  Configure ORCID for production
   `#103 <https://github.com/rero/sonar/issues/103>`__

**Merged pull requests:**

-  users: rename role publisher
   `#251 <https://github.com/rero/sonar/pull/251>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposits: improve form
   `#249 <https://github.com/rero/sonar/pull/249>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  users: send welcome email
   `#247 <https://github.com/rero/sonar/pull/247>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  users: limit to only one role
   `#243 <https://github.com/rero/sonar/pull/243>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  search: add aggregations
   `#239 <https://github.com/rero/sonar/pull/239>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  design: rebrand website
   `#238 <https://github.com/rero/sonar/pull/238>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: add translations
   `#237 <https://github.com/rero/sonar/pull/237>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: Transifex integration
   `#236 <https://github.com/rero/sonar/pull/236>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  users: create user record on registration
   `#235 <https://github.com/rero/sonar/pull/235>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisations: access records with specific URL
   `#234 <https://github.com/rero/sonar/pull/234>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: update dependencies
   `#233 <https://github.com/rero/sonar/pull/233>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposits: add organisation in documents
   `#231 <https://github.com/rero/sonar/pull/231>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  user: add publisher role
   `#229 <https://github.com/rero/sonar/pull/229>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  security: add permissions for accessing resources
   `#228 <https://github.com/rero/sonar/pull/228>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisation: create default organisation
   `#226 <https://github.com/rero/sonar/pull/226>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  indexer: custom indexer
   `#210 <https://github.com/rero/sonar/pull/210>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  authentication: ORCID for production
   `#208 <https://github.com/rero/sonar/pull/208>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: improve form in submission process
   `#207 <https://github.com/rero/sonar/pull/207>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: improve editor
   `#206 <https://github.com/rero/sonar/pull/206>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: translate form options.
   `#205 <https://github.com/rero/sonar/pull/205>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  user: synchronize user records and security accounts
   `#203 <https://github.com/rero/sonar/pull/203>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  user: improve editor
   `#202 <https://github.com/rero/sonar/pull/202>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: improve serializer
   `#201 <https://github.com/rero/sonar/pull/201>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisation: improve organisation editor
   `#200 <https://github.com/rero/sonar/pull/200>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisation: standardize name
   `#199 <https://github.com/rero/sonar/pull/199>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: fix affiliations file path
   `#192 <https://github.com/rero/sonar/pull/192>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.4.0 <https://github.com/rero/sonar/tree/v0.4.0>`__ (2020-04-17)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.3.3...v0.4.0>`__

**Fixed bugs:**

-  Error in Travis CI when update sonar-ui version
   `#159 <https://github.com/rero/sonar/issues/159>`__
-  Disable access to super admin for admin users
   `#125 <https://github.com/rero/sonar/issues/125>`__

**Closed issues:**

-  Initial Update `#189 <https://github.com/rero/sonar/issues/189>`__
-  Prepare before the publication of TEST website
   `#185 <https://github.com/rero/sonar/issues/185>`__
-  Create persistent storage to cluster
   `#157 <https://github.com/rero/sonar/issues/157>`__
-  Import embargo information of files
   `#147 <https://github.com/rero/sonar/issues/147>`__
-  Add a property to store external links for documents
   `#144 <https://github.com/rero/sonar/issues/144>`__
-  Don't show files with embargo
   `#143 <https://github.com/rero/sonar/issues/143>`__
-  Install flask wiki
   `#138 <https://github.com/rero/sonar/issues/138>`__
-  configure smtp for sending mails in deployed instances
   `#127 <https://github.com/rero/sonar/issues/127>`__
-  Change sentry key to make it work again
   `#119 <https://github.com/rero/sonar/issues/119>`__
-  Remove test organizations
   `#115 <https://github.com/rero/sonar/issues/115>`__
-  Modify deposit data structure to match final document structure
   `#113 <https://github.com/rero/sonar/issues/113>`__
-  Create a about page
   `#106 <https://github.com/rero/sonar/issues/106>`__
-  Create a contact page
   `#105 <https://github.com/rero/sonar/issues/105>`__
-  Cleanup the project
   `#101 <https://github.com/rero/sonar/issues/101>`__
-  Web design `#97 <https://github.com/rero/sonar/issues/97>`__
-  Persistent identifiers
   `#75 <https://github.com/rero/sonar/issues/75>`__
-  Common module between RERO ILS and SONAR
   `#15 <https://github.com/rero/sonar/issues/15>`__
-  IR filter configuration
   `#13 <https://github.com/rero/sonar/issues/13>`__

**Merged pull requests:**

-  security: replace pipenv check by safety.
   `#191 <https://github.com/rero/sonar/pull/191>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  accounts: add ORCID icon
   `#190 <https://github.com/rero/sonar/pull/190>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: prepare for publishing TEST website
   `#188 <https://github.com/rero/sonar/pull/188>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documentation: Flask-Wiki integration
   `#187 <https://github.com/rero/sonar/pull/187>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: deposit data structure finalization
   `#184 <https://github.com/rero/sonar/pull/184>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: check files restrictions
   `#182 <https://github.com/rero/sonar/pull/182>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: fix security issue in bleach library
   `#181 <https://github.com/rero/sonar/pull/181>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: update files permissions
   `#180 <https://github.com/rero/sonar/pull/180>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  organisations: remove test organisation
   `#179 <https://github.com/rero/sonar/pull/179>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.3.3 <https://github.com/rero/sonar/tree/v0.3.3>`__ (2020-03-17)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.3.2...v0.3.3>`__

**Fixed bugs:**

-  Fix instability in clusters
   `#158 <https://github.com/rero/sonar/issues/158>`__

**Closed issues:**

-  Import missing fields from RERODOC
   `#160 <https://github.com/rero/sonar/issues/160>`__
-  Configure Switch edu-id for production
   `#104 <https://github.com/rero/sonar/issues/104>`__

**Merged pull requests:**

-  documents: import missing fields from RERODOC
   `#178 <https://github.com/rero/sonar/pull/178>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  authentication: configure SWITCHaai for production
   `#177 <https://github.com/rero/sonar/pull/177>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: import "identifiedBy" properties
   `#167 <https://github.com/rero/sonar/pull/167>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.3.2 <https://github.com/rero/sonar/tree/v0.3.2>`__ (2020-03-04)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.3.1...v0.3.2>`__

**Merged pull requests:**

-  deployment: install ImageMagick
   `#165 <https://github.com/rero/sonar/pull/165>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.3.1 <https://github.com/rero/sonar/tree/v0.3.1>`__ (2020-02-26)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.3.0...v0.3.1>`__

**Closed issues:**

-  Don't display files from NL
   `#161 <https://github.com/rero/sonar/issues/161>`__

**Merged pull requests:**

-  documents: external URLs
   `#164 <https://github.com/rero/sonar/pull/164>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  Preview and thumbnails
   `#163 <https://github.com/rero/sonar/pull/163>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.3.0 <https://github.com/rero/sonar/tree/v0.3.0>`__ (2020-02-25)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.2.2...v0.3.0>`__

**Fixed bugs:**

-  Check why affiliations are not well extracted with GROBID
   `#148 <https://github.com/rero/sonar/issues/148>`__
-  Show language facet
   `#123 <https://github.com/rero/sonar/issues/123>`__
-  Adapt layout of password forgotten page
   `#102 <https://github.com/rero/sonar/issues/102>`__
-  shibboleth: fix authentication issue
   `#126 <https://github.com/rero/sonar/pull/126>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

**Closed issues:**

-  Import submissions from RERODOC
   `#141 <https://github.com/rero/sonar/issues/141>`__
-  Import users from RERODOC
   `#140 <https://github.com/rero/sonar/issues/140>`__
-  Create the document when a deposit is validated
   `#114 <https://github.com/rero/sonar/issues/114>`__
-  Re-enable marshmallow checks
   `#79 <https://github.com/rero/sonar/issues/79>`__
-  Migrate data from RERO DOC
   `#76 <https://github.com/rero/sonar/issues/76>`__

**Merged pull requests:**

-  project: install UI script
   `#156 <https://github.com/rero/sonar/pull/156>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  PDF extractor: Affiliation extraction
   `#149 <https://github.com/rero/sonar/pull/149>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: PDF metadata extraction
   `#137 <https://github.com/rero/sonar/pull/137>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: Create document
   `#136 <https://github.com/rero/sonar/pull/136>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: Import documents from RERODOC
   `#135 <https://github.com/rero/sonar/pull/135>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: JSON schema API endpoint
   `#134 <https://github.com/rero/sonar/pull/134>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  nginx: remove OPTIONS requests from logs.
   `#133 <https://github.com/rero/sonar/pull/133>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: fix languages facet display
   `#132 <https://github.com/rero/sonar/pull/132>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: remove unnecessary properties
   `#131 <https://github.com/rero/sonar/pull/131>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  account: password forgotten template
   `#130 <https://github.com/rero/sonar/pull/130>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  records: remove form schemas
   `#129 <https://github.com/rero/sonar/pull/129>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: various corrections
   `#128 <https://github.com/rero/sonar/pull/128>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.2.2 <https://github.com/rero/sonar/tree/v0.2.2>`__ (2020-01-16)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.2.1...v0.2.2>`__

**Merged pull requests:**

-  records: integrate public search
   `#122 <https://github.com/rero/sonar/pull/122>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  documents: data model refactor
   `#116 <https://github.com/rero/sonar/pull/116>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.2.1 <https://github.com/rero/sonar/tree/v0.2.1>`__ (2020-01-10)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.2.0...v0.2.1>`__

**Fixed bugs:**

-  Remove external calls to CSS for toastr and font-awesome
   `#124 <https://github.com/rero/sonar/issues/124>`__

**Closed issues:**

-  Upgrade to invenio 3.2
   `#117 <https://github.com/rero/sonar/issues/117>`__
-  Remove invenio-theme
   `#100 <https://github.com/rero/sonar/issues/100>`__
-  Change data model structure for documents
   `#96 <https://github.com/rero/sonar/issues/96>`__
-  Integrate public search from sonar-ui application
   `#95 <https://github.com/rero/sonar/issues/95>`__

**Merged pull requests:**

-  ui: update project name
   `#120 <https://github.com/rero/sonar/pull/120>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: upgrade Invenio
   `#118 <https://github.com/rero/sonar/pull/118>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.2.0 <https://github.com/rero/sonar/tree/v0.2.0>`__ (2019-12-30)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/v0.1.0...v0.2.0>`__

**Closed issues:**

-  API endpoint for publishing a publication
   `#91 <https://github.com/rero/sonar/issues/91>`__
-  Evaluate invenio-rest for building custom endpoints
   `#90 <https://github.com/rero/sonar/issues/90>`__
-  populate metadata when a file is uploaded in deposit process
   `#87 <https://github.com/rero/sonar/issues/87>`__
-  Create a "Deposit" resource
   `#82 <https://github.com/rero/sonar/issues/82>`__
-  Install invenio-files-rest for managing files
   `#81 <https://github.com/rero/sonar/issues/81>`__
-  Document administration
   `#74 <https://github.com/rero/sonar/issues/74>`__
-  Organization administration
   `#73 <https://github.com/rero/sonar/issues/73>`__
-  Create default users and roles
   `#70 <https://github.com/rero/sonar/issues/70>`__
-  User administration `#68 <https://github.com/rero/sonar/issues/68>`__
-  Add link to institution
   `#67 <https://github.com/rero/sonar/issues/67>`__
-  Remove user `#66 <https://github.com/rero/sonar/issues/66>`__
-  Update user `#65 <https://github.com/rero/sonar/issues/65>`__
-  Create user `#64 <https://github.com/rero/sonar/issues/64>`__
-  List users `#63 <https://github.com/rero/sonar/issues/63>`__
-  Admin layout integration
   `#62 <https://github.com/rero/sonar/issues/62>`__
-  Angular testing and integration
   `#61 <https://github.com/rero/sonar/issues/61>`__
-  Change license `#60 <https://github.com/rero/sonar/issues/60>`__
-  Increase code coverage
   `#57 <https://github.com/rero/sonar/issues/57>`__
-  Test yapf code formatter
   `#53 <https://github.com/rero/sonar/issues/53>`__
-  Editor for bibliographic metadata
   `#52 <https://github.com/rero/sonar/issues/52>`__
-  Workflow of the publication upload
   `#51 <https://github.com/rero/sonar/issues/51>`__
-  Extract metadata from PDF
   `#50 <https://github.com/rero/sonar/issues/50>`__
-  Italian translations
   `#49 <https://github.com/rero/sonar/issues/49>`__
-  Upload a full text publication
   `#43 <https://github.com/rero/sonar/issues/43>`__
-  Translations `#28 <https://github.com/rero/sonar/issues/28>`__
-  Authentication via ORCID
   `#26 <https://github.com/rero/sonar/issues/26>`__
-  Authentication via Switch Edu-ID
   `#25 <https://github.com/rero/sonar/issues/25>`__
-  Project version tag `#24 <https://github.com/rero/sonar/issues/24>`__
-  Document details `#20 <https://github.com/rero/sonar/issues/20>`__

**Merged pull requests:**

-  deposits: various changes
   `#94 <https://github.com/rero/sonar/pull/94>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: review a deposit
   `#93 <https://github.com/rero/sonar/pull/93>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: publish a deposit
   `#92 <https://github.com/rero/sonar/pull/92>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deposit: extract metadata from PDF
   `#89 <https://github.com/rero/sonar/pull/89>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  resources: create deposit resource
   `#88 <https://github.com/rero/sonar/pull/88>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  files: configure Invenio files REST
   `#86 <https://github.com/rero/sonar/pull/86>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  project: add commit message template
   `#80 <https://github.com/rero/sonar/pull/80>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  webpack: custom configuration file
   `#78 <https://github.com/rero/sonar/pull/78>`__
   (`jma <https://github.com/jma>`__)
-  records: integrate angular UI
   `#77 <https://github.com/rero/sonar/pull/77>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  record: User resource creation
   `#72 <https://github.com/rero/sonar/pull/72>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  theming: Admin layout `#71 <https://github.com/rero/sonar/pull/71>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  license: Move from GPLv2 to AGPLv3
   `#69 <https://github.com/rero/sonar/pull/69>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  document: PDF metadata extraction
   `#58 <https://github.com/rero/sonar/pull/58>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

`v0.1.0 <https://github.com/rero/sonar/tree/v0.1.0>`__ (2019-07-25)
-------------------------------------------------------------------

`Full
Changelog <https://github.com/rero/sonar/compare/3c557cc27626eb1a68d484f702f35023cb53a9c3...v0.1.0>`__

**Closed issues:**

-  Authentication with the service
   `#48 <https://github.com/rero/sonar/issues/48>`__
-  Test login process with Switch edu-id
   `#47 <https://github.com/rero/sonar/issues/47>`__
-  Service provider configuration
   `#46 <https://github.com/rero/sonar/issues/46>`__
-  Create and configure a switch edu-id account
   `#45 <https://github.com/rero/sonar/issues/45>`__
-  asdf `#44 <https://github.com/rero/sonar/issues/44>`__
-  Add command to setup script
   `#42 <https://github.com/rero/sonar/issues/42>`__
-  Format all files `#38 <https://github.com/rero/sonar/issues/38>`__
-  Language switcher `#27 <https://github.com/rero/sonar/issues/27>`__
-  Configure coveralls.io
   `#23 <https://github.com/rero/sonar/issues/23>`__
-  Remove sqlalchemy warning
   `#22 <https://github.com/rero/sonar/issues/22>`__
-  Cleanup code and comments
   `#18 <https://github.com/rero/sonar/issues/18>`__
-  Code coverage `#17 <https://github.com/rero/sonar/issues/17>`__
-  Search facets `#16 <https://github.com/rero/sonar/issues/16>`__
-  Test instance `#14 <https://github.com/rero/sonar/issues/14>`__
-  USI data searchable `#12 <https://github.com/rero/sonar/issues/12>`__
-  DEV instance and sub domain activation
   `#3 <https://github.com/rero/sonar/issues/3>`__

**Merged pull requests:**

-  project: Release tag `#59 <https://github.com/rero/sonar/pull/59>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  tests: Increase code coverage
   `#56 <https://github.com/rero/sonar/pull/56>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: Italian translations
   `#55 <https://github.com/rero/sonar/pull/55>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  authentication: Switch edu-id authentication
   `#54 <https://github.com/rero/sonar/pull/54>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  authentication: ORCID OAuth
   `#39 <https://github.com/rero/sonar/pull/39>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  templating: Document detail
   `#37 <https://github.com/rero/sonar/pull/37>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: Translations in french and german
   `#33 <https://github.com/rero/sonar/pull/33>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  translations: Language switcher
   `#30 <https://github.com/rero/sonar/pull/30>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  search: Faceted filters
   `#29 <https://github.com/rero/sonar/pull/29>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  search: USI data searchable
   `#21 <https://github.com/rero/sonar/pull/21>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  config: Sentry support
   `#11 <https://github.com/rero/sonar/pull/11>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  theming: IR specific view
   `#10 <https://github.com/rero/sonar/pull/10>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  theming: Frontpage layout
   `#9 <https://github.com/rero/sonar/pull/9>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  deployment: SONAR instance
   `#8 <https://github.com/rero/sonar/pull/8>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)
-  tests: Travis build `#7 <https://github.com/rero/sonar/pull/7>`__
   (`sebastiendeleze <https://github.com/sebastiendeleze>`__)

\* *This Changelog was automatically generated by
`github\_changelog\_generator <https://github.com/github-changelog-generator/github-changelog-generator>`__*
