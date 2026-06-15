# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Google scholar serializer."""

from invenio_records_rest.serializers.base import (
    PreprocessorMixin,
    SerializerMixinInterface,
)
from invenio_records_rest.serializers.marshmallow import MarshmallowMixin


class SonarGoogleScholarSerializer(SerializerMixinInterface, MarshmallowMixin, PreprocessorMixin):
    """Google scholar serializer."""

    def dump(self, obj, context=None):
        """Serialize object with schema.

        Mandatory to override this method, as invenio-records-rest does not
        use the right way to dump objects (compatible with marshmallow 3.9).
        """
        return self.schema_class(context=context).dump(obj)

    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record in metas for Google scholar."""
        data = super().transform_record(pid, record, links_factory, **kwargs)

        metas = []
        meta_template = '<meta name="citation_{key}" content="{value}">'
        for key, value in data.items():
            if isinstance(value, list):
                metas.extend(meta_template.format(key=key, value=list_value) for list_value in value)
            else:
                metas.append(meta_template.format(key=key, value=value))

        return "\n".join(metas)
