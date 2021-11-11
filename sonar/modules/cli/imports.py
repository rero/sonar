# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""SONAR CLI commands."""

import csv
import os
from datetime import datetime

import click
from flask.cli import with_appcontext

from sonar.modules.documents.tasks import import_records
from sonar.modules.utils import chunks

DOCUMENT_TYPE_MAPPING = {
    'master thesis': 'coar:c_bdcc',
    'bachelor thesis': 'coar:c_7a1f',
    'thesis': 'coar:c_46ec',
    'book': 'coar:c_2f33',
    'bookSection': 'coar:c_3248',
    'conferencePaper': 'coar:c_5794',
    'journalArticle': 'coar:c_6501',
    'report': 'coar:c_18ws'
}

DOCUMENT_TYPE_MAPPING_HEPVS = {
    'book': 'coar:c_2f33', # book
    'bookSection': 'coar:c_3248', # book part
    'conferencePaper': 'coar:c_5794', # conference paper
    'conferencePoster': 'coar:c_6670', # conference poster
    'conferencePresentation': 'coar:R60J-J5BD', # conference presentation
    'doctoralThesis': 'coar:c_db06', # doctoral thesis
    'film': 'coar:c_8a7e', # moving image
    'internalReport': 'coar:c_18ww', # internal report
    'journalArticle': 'coar:c_6501', # journal article
    'lecture': 'coar:c_8544', # lecture
    'livrable de projet': 'coar:c_18op', # project deliverable
    'newspaperArticle': 'coar:c_998f', # newspaper article
    'other': 'coar:c_1843', # other
    'report': 'coar:c_93fc', # report
    'reportFinancial': 'coar:c_18hj', # report to funding agency
    'researchReport': 'coar:c_18ws', # research report
    'sound': 'coar:c_18cc' # sound
}



@click.group()
def imports():
    """Import commands."""


@imports.command()
@with_appcontext
@click.argument('data_file', type=click.File('r'), required=True)
@click.argument('pdf_directory', required=True)
def hepbejune(data_file, pdf_directory):
    """Import record from HEP BEJUNE.

    :param data_file: CSV File.
    :param pdf_directory: Directory containing the PDF files.
    """
    click.secho('Import records from HEPBEJUNE')

    records = []

    with open(data_file.name, 'r') as file:
        reader = csv.reader(file, delimiter=',')

        for row in reader:
            date = datetime.strptime(row[9], '%d/%m/%Y')
            if row[1] == 'SKIP':
                continue

            degree = row[14]
            if degree == 'bachelor thesis':
                degree = 'Mémoire de bachelor'
            elif degree == 'master thesis':
                degree = 'Mémoire de master'
            else:
                degree = 'Mémoire'

            data = {
                'title': [{
                    'type': 'bf:Title',
                    'mainTitle': [{
                        'value': row[3],
                        'language': 'fre'
                    }]
                }],
                'identifiedBy': [{
                    'type': 'bf:Local',
                    'source': 'hepbejune',
                    'value': row[0]
                }],
                'language': [{
                    'type': 'bf:Language',
                    'value': 'fre'
                }],
                'contribution': [{
                    'agent': {
                        'type': 'bf:Person',
                        'preferred_name': row[8]
                    },
                    'role': ['cre']
                }],
                'dissertation': {
                    'degree': degree,
                    'grantingInstitution': 'Haute école pédagogique BEJUNE',
                    'date': date.strftime('%Y-%m-%d')
                },
                'provisionActivity': [{
                    'type': 'bf:Publication',
                    'startDate': date.strftime('%Y')
                }],
                'customField1': [
                    row[12]
                ],
                'customField2': [
                    row[13]
                ],
                'documentType':
                DOCUMENT_TYPE_MAPPING.get(row[14], 'coar:c_1843'),
                'usageAndAccessPolicy': {
                    'license': 'CC BY-NC-ND'
                },
                'organisation': [{
                    '$ref':
                    'https://sonar.ch/api/organisations/hepbejune'
                }],
                'harvested':
                True,
                'masked':
                'masked_for_external_ips'
            }

            file_path = os.path.join(pdf_directory, row[16])
            if os.path.isfile(file_path):
                data['files'] = [{
                    'key': 'fulltext.pdf',
                    'url': file_path,
                    'label': 'Full-text',
                    'type': 'file',
                    'order': 0
                }]

            records.append(data)

    # Chunk record list and send celery task
    for chunk in list(chunks(records, 10)):
        import_records.delay(chunk)

    click.secho('Finished, records are imported in background', fg='green')


#  0 	identifiedBy[type=bf:Local; source=hepvs]
#  1 	SKIP ?
#  2 	COMMENTAIRE RERO+
#  3 	documentType
#  4 	provisionActivity.startDate
#  5 	contribution.agent.preferred_name [role=cre]
#  6 	title
#  7 	partOf.document.title
#  8 	partOf.document.identifiedBy.value [type=ISBN]
#  9 	partOf.document.identifiedBy.value [type=ISSN]
#  10	identifiedBy.value [type=ISBN]
#  11	identifiedBy.value [type=DOI]
#  12	otherEdition.document.electronicLocator
#  13	abstracts [pour le sous-champ language, reprendre la langue du document]
# 14	?
#  15	partOf.numberingPages
#  16	extent
#  17	partOf.numberingIssue
#  18	partOf.numberingVolume
#  19	series.name
#  20	series.number
# 21	series.name [TO BE IGNORED - EMPTY DATA]
#  22	provisionActivity.statements.label [type=agent]
#  23	provisionActivity.statements.label [type=place]
#  24	language
#  25	usageAndAccessPolicy.license
#  26	usageAndAccessPolicy.label
#  27	notes
#  28	FILE
#  29	otherEdition.document.electronicLocator
#  30	subjects.label.value [language=fr]
#  31	partOf.document.contribution
#  32	masked
# 33	contribution.agent.preferred_name [role=ctb]  [TO BE IGNORED - REDUNDANT DATA (5/7)]
#  34	notes
#  35	contribution.agent[type=bf:Meeting].preferred_name [role=ctb]

@imports.command()
@with_appcontext
@click.argument('data_file', type=click.File('r'), required=True)
@click.argument('pdf_directory', required=True)
def hepvs(data_file, pdf_directory):
    """Import record from HEP VS.

    :param data_file: CSV File.
    :param pdf_directory: Directory containing the PDF files.
    """
    click.secho('Import records from HEP VS')

    records = []

    with open(data_file.name, 'r') as file:
        reader = csv.reader(file, delimiter=',')

        rec = 0
        for row in reader:
            rec += 1
            if rec <= 3 or row[1].lower() == 'x':
                # skip 3 top rows (headers) and rows tagged as 'SKIP'
                continue
            date = datetime.strptime(row[4], '%Y')

            click.secho('Rec %d with id %s' % (rec, row[0]))

            data = {
                'title': [{
                    'type': 'bf:Title',
                    'mainTitle': [{
                        'value': row[6],
                        'language': row[24]
                    }]
                }],
                'identifiedBy': [{
                    'type': 'bf:Local',
                    'source': 'hepvs',
                    'value': row[0]
                }],
                'language': [{
                    'type': 'bf:Language',
                    'value': row[24]
                }],
                'provisionActivity': [{
                    'type': 'bf:Publication',
                    'startDate': date.strftime('%Y')
                }],
                'documentType':
                DOCUMENT_TYPE_MAPPING_HEPVS.get(row[3], 'coar:c_1843'),
                'organisation': [{
                    '$ref':
                    'https://sonar.ch/api/organisations/hepvs'
                }],
                'harvested':
                True,
            }

            authors = row[5].split(';') if row[5] else None
            if authors:
                contribution = []
                for a in authors:
                    a.strip()
                    c = {
                        'agent': {
                            'type': 'bf:Person',
                            'preferred_name': a.strip()
                        },
                        'role': ['cre']
                    }
                    contribution.append(c)
                data['contribution'] = contribution

            part_of = {}
            part_of_document = {}
            if row[7]:
                part_of_document['title'] = row[7]
            if row[8]:
                isbn = {'type': 'bf:Isbn', 'value': row[8]}
                if 'identifiedBy' not in part_of_document:
                     part_of_document['identifiedBy'] = []
                part_of_document['identifiedBy'].append(isbn)
            if row[9]:
                issn = {'type': 'bf:Issn', 'value': row[9]}
                if 'identifiedBy' not in part_of_document:
                     part_of_document['identifiedBy'] = []
                part_of_document['identifiedBy'].append(issn)
            if row[31]:
                part_of_document['contribution'] = [row[31]]

            if part_of_document:
                part_of['document'] = part_of_document
                part_of['numberingYear'] = date.strftime('%Y')
            if row[15]:
                part_of['numberingPages'] = row[15]
            if row[17]:
                part_of['numberingIssue'] = row[17]
            if row[18]:
                part_of['numberingVolume'] = row[18]
            if part_of:
                data['partOf'] = [part_of]

            if row[10]:
                isbn = {'type': 'bf:Isbn', 'value': row[10]}
                if 'identifiedBy' not in data:
                     data['identifiedBy'] = []
                data['identifiedBy'].append(isbn)
            if row[11]:
                doi = {'type': 'bf:Doi', 'value': row[11]}
                if 'identifiedBy' not in data:
                     data['identifiedBy'] = []
                data['identifiedBy'].append(doi)

            # otherEdition.document.electronicLocator is based on
            # "Link Attachments" [29] _or_ "Url" [12] (prority to the former)
            if row[29] or row[12]:
                url = row[29] or row[12]
                data['otherEdition'] = [{
                    'document': {
                        'electronicLocator': url
                    },
                    'publicNote': 'Autre URL'
                }]
            
            if row[19]:
                series = {}
                series['name'] = row[19]
                if row[20]:
                    series['number'] = row[20]
                data['series'] = [series]

            if row[22] or row[23]:
                provision_activity = data.get('provisionActivity', [])
                statement = []
                if row[22]:
                    statement.append(
                        {'label': [{'value': row[22]}], 'type': 'bf:Agent'}
                    )
                if row[23]:
                    statement.append(
                        {'label': [{'value': row[23]}], 'type': 'bf:Place'}
                    )
                provision_activity.append({
                    'type': 'bf:Publication',
                    'statement': statement
                })
                data['provisionActivity'] = provision_activity

            if row[27] or row[34]:
                notes = data.get('notes', [])
                if row[27]:
                    notes.append(row[27])
                if row[34]:
                    notes.append(row[34])
                data['notes'] = notes

            if row[13]:
                abstract = {
                    'value': row[13],
                    'language': row[24]
                }
                data['abstracts'] = [abstract]
            
            if row[30]:
                data['subjects'] = [{
                    'label': {
                        'language': 'fre',
                        'value': [s.strip() for s in row[30].split(';')]
                    }}]

            if row[16]:
                data['extent'] = row[16] + ' p.'

            (license, label) = (row[25], row[26])
            if license or label:
                data['usageAndAccessPolicy'] = {}
            if license:
                data['usageAndAccessPolicy']['license'] = license
            if label:
                data['usageAndAccessPolicy']['label'] = label

            if row[32]:
                data['masked'] = 'masked_for_external_ips'

            if row[35]:
                contribution = data.get('contribution', [])
                c = {
                    'agent': {
                        'type': 'bf:Meeting',
                        'preferred_name': row[35]
                    },
                    'role': ['ctb']
                }
                contribution.append(c)
                data['contribution'] = contribution

            if (row[28]):
                file_path = os.path.join(pdf_directory, row[28])
                file_name = file_path.split('/')[-1]
                click.secho('\tFile path: ' + file_path)
                click.secho('\tFile name: ' + file_name)
                if os.path.isfile(file_path):
                    data['files'] = [{
                        'key': file_name,
                        'url': file_path,
                        'label': 'Full-text',
                        'type': 'file',
                        'order': 0
                    }]
                else: 
                    click.secho('ERROR: file for %s does not exist!' % row[0], fg='red')

            records.append(data)

    # Chunk record list and send celery task
    for chunk in list(chunks(records, 10)):
        import_records.delay(chunk)

    click.secho('Finished, records are imported in the background', fg='green')
