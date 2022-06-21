# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Urn API."""

from datetime import datetime, timedelta, timezone

from flask import current_app
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from sonar.modules.documents.models import UrnIdentifier


class Urn:
    """Urn class."""

    urn_pid_type = 'urn'

    @classmethod
    def _calculateCheckDigit(cls, urn):
        """Return the check-digit calculated on a URN.

        :param urn: the urn identifier.
        """
        # For details on the algorithm, see:
        # https://d-nb.info/1045320641/34
        # set up conversion table
        conversion_table = {
            '0':'1', '1':'2', '2':'3', '3':'4', '4':'5', '5':'6', '6':'7',
            '7':'8', '8':'9', '9':'41', 'A':'18', 'B':'14', 'C':'19', 'D':'15',
            'E':'16', 'F':'21', 'G':'22', 'H':'23', 'I':'24', 'J':'25',
            'K':'42', 'L':'26', 'M':'27', 'N':'13', 'O':'28', 'P':'29',
            'Q':'31', 'R':'12', 'S':'32', 'T':'33', 'U':'11', 'V':'34',
            'W':'35', 'X':'36', 'Y':'37', 'Z':'38', '-':'39', ':':'17',
            '_':'43', '.':'47', '/':'45','+':'49'
            }
        # obtain digit sequence using the conversion table by concatenating
        # chars
        digit_sequence = ''
        for idx, element in enumerate(urn, 0):
            digits = conversion_table[urn[idx].upper()]
            digit_sequence = digit_sequence + digits
        # calculate product sum
        product_sum = 0
        for idx, element in enumerate(digit_sequence, 0):
            product_sum = product_sum + ((idx+1) * int(digit_sequence[idx]))
        # read the last number of the digit sequence and calculate the quotient
        last_number = int(digit_sequence[-1])
        quotient = int(product_sum/last_number)
        quotient_string = str(quotient)
        # read the check-digit from the quotient value string
        return quotient_string[-1]

    @classmethod
    def _generate_urn(cls, pid, config):
        """Generate a URN code for namespace.

        :param pid: the pid of the urn identifier.
        :param config: organisation related configuration.
        """
        base_urn = current_app.config.get("SONAR_APP_URN_DNB_BASE_URN")
        new_urn = f'{base_urn}{config.get("code"):03}-{pid}'
        return f'{new_urn}{cls._calculateCheckDigit(new_urn)}'

    @classmethod
    def create_urn(cls, record):
        """Create the URN identifier.

        :param record: the invenio record instance to be processed.
        """
        urn_config = current_app.config.get("SONAR_APP_DOCUMENT_URN")
        org_pid = record.replace_refs().get("organisation", [{}])[0].get("pid")
        if config := urn_config.get("organisations", {}).get(org_pid):
            if record.get("documentType") in config.get("types"):
                urn_next_pid = str(UrnIdentifier.next())
                try:
                    urn_code = cls._generate_urn(int(urn_next_pid), config)
                    pid = PersistentIdentifier.create(
                        cls.urn_pid_type,
                        urn_code,
                        object_type="rec",
                        object_uuid=record.id,
                        status=PIDStatus.NEW,
                    )
                    record["identifiedBy"].append(
                        {"type": "bf:Urn", "value": urn_code}
                    )
                except PIDAlreadyExists:
                    current_app.logger.error(
                        'generated urn already exist for document: '
                            + record.get('pid'))

    @classmethod
    def urn_query(cls, status=None):
        """Build URN query.

        :param status: PID status by default N.
        :returns: Base query.
        """
        return PersistentIdentifier.query\
                .filter_by(pid_type=cls.urn_pid_type)\
                .filter_by(status=status)


    @classmethod
    def get_urn_pids(cls, status=PIDStatus.NEW, days=None):
        """Get count of URN pids by status and creation date.

        :param status: PID status by default N.
        :param days: Number of days passed since the creation of the document.
        :returns: Documents count.
        """
        count = 0
        query = cls.urn_query(status=status)
        if uuuids := [str(uuid.object_uuid) for uuid in query.all()]:
            from sonar.modules.documents.api import DocumentSearch
            query = DocumentSearch()\
                .filter('terms', _id=uuuids)
            if days:
                date = datetime.now(timezone.utc) - timedelta(days=days)
                query = query.filter('range', _created={'lte': date})
            count = query.count()
        return count


    @classmethod
    def get_unregistered_urns(cls):
        """Get list of unregistered URNs.

        :returns: List of unregistered URNs .
        """
        query = cls.urn_query(status=PIDStatus.NEW)
        return [str(uuid.pid_value) for uuid in query.all()]

    @classmethod
    def register_urn_code_from_document(cls, record):
        """Register the urn pid for a given document.

        :param record: The document.
        """
        from sonar.modules.documents.api import DocumentRecord
        from sonar.modules.documents.dnb import DnbUrnService

        # TODO: verify the urn, it could be already registered
        if DnbUrnService.register_document(record):
            urn_code = DocumentRecord.get_rero_urn_code(record)
            pid = PersistentIdentifier.query\
                    .filter_by(pid_type=cls.urn_pid_type)\
                    .filter_by(pid_value=urn_code).first()
            if pid and pid.status == PIDStatus.NEW:
                pid.status = PIDStatus.REGISTERED
                db.session.commit()

    @classmethod
    def register_urn_pid(cls, urn=None):
        """Register the urn pid.

        :param pid: The corresponding URN code to register.
        """
        if pid := PersistentIdentifier.get(cls.urn_pid_type, urn):
            pid.status = PIDStatus.REGISTERED
            db.session.commit()


    @classmethod
    def get_documents_to_generate_urns(cls):
        """Get documents that need a URN code..

        :returns: generator of document records.
        """
        from sonar.modules.documents.api import DocumentRecord, DocumentSearch
        urn_config = current_app.config.get("SONAR_APP_DOCUMENT_URN")
        configs = urn_config.get('organisations', {})
        pids = []
        for org_pid in configs.items():
            config = configs.get(org_pid)
            doc_types = config.get('types')
            query = DocumentSearch()\
                .filter('terms', documentType=doc_types)\
                .filter('exists', field='identifiedBy')\
                .filter('bool', must_not=[
                    Q('term', identifiedBy__type='bf:Urn')])\
                .source(['pid'])
            pids.extend(hit.pid for hit in query.scan())

        for pid in pids:
            yield DocumentRecord.get_record_by_pid(pid)
