# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""schema.org serializer."""

from invenio_records_rest.serializers.base import (
    PreprocessorMixin,
    SerializerMixinInterface,
)
from invenio_records_rest.serializers.marshmallow import MarshmallowMixin


class SonarSchemaOrgSerializer(SerializerMixinInterface, MarshmallowMixin, PreprocessorMixin):
    """Marshmallow based schema.org serializer for records."""

    def dump(self, obj, context=None):
        """Serialize object with schema.

        Mandatory to override this method, as invenio-records-rest does not
        use the right way to dump objects (compatible with marshmallow 3.9).
        """
        return self.schema_class(context=context).dump(obj)
