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
