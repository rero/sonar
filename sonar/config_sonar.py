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

"""Specific configuration SONAR."""

SONAR_APP_SERVER_NAME = 'sonar.rero.ch'

SONAR_APP_BASE_URL = 'https://localhost:5000'

SONAR_APP_API_URL = 'https://localhost:5000/api/'

SONAR_APP_ANGULAR_URL = 'https://localhost:5000/manage/'
"""Link to angular integrated app root."""

SONAR_APP_PRODUCTION_STATE = False

SONAR_APP_SITEMAP_ENTRY_SIZE = 10000

SONAR_APP_LANGUAGES_MAP = {
    'aar': 'aa',
    'abk': 'ab',
    'ace': None,
    'ach': None,
    'ada': None,
    'ady': None,
    'afa': None,
    'afh': None,
    'afr': 'af',
    'ain': None,
    'aka': 'ak',
    'akk': None,
    'alb': 'sq',
    'ale': None,
    'alg': None,
    'alt': None,
    'ang': None,
    'amh': 'am',
    'anp': None,
    'apa': None,
    'ara': 'ar',
    'arc': None,
    'arg': 'an',
    'arm': 'hy',
    'arn': None,
    'arp': None,
    'art': None,
    'arw': None,
    'asm': 'as',
    'ast': None,
    'ath': None,
    'aus': None,
    'ava': 'av',
    'ave': 'ae',
    'awa': None,
    'aym': 'ay',
    'aze': 'az',
    'bad': None,
    'bai': None,
    'bak': 'ba',
    'bal': None,
    'bam': 'bm',
    'ban': None,
    'baq': 'eu',
    'bas': None,
    'bat': None,
    'bej': None,
    'bel': 'be',
    'bem': None,
    'ben': 'bn',
    'ber': None,
    'bho': None,
    'bih': 'bh',
    'bik': None,
    'bin': None,
    'bis': 'bi',
    'bla': None,
    'bnt': None,
    'bos': 'bs',
    'bra': None,
    'bre': 'br',
    'btk': None,
    'bua': None,
    'bug': None,
    'bul': 'bg',
    'bur': 'my',
    'byn': None,
    'cad': None,
    'cai': None,
    'car': None,
    'cat': 'ca',
    'cau': None,
    'ceb': None,
    'cel': None,
    'cha': 'ch',
    'chb': None,
    'che': 'ce',
    'chg': None,
    'chi': 'zh',
    'chk': None,
    'chm': None,
    'chn': None,
    'cho': None,
    'chp': None,
    'chr': None,
    'chu': 'cu',
    'chv': 'cv',
    'chy': None,
    'cmc': None,
    'cnr': None,
    'cop': None,
    'cor': 'kw',
    'cos': 'co',
    'cpe': None,
    'cpf': None,
    'cpp': None,
    'cre': 'cr',
    'crh': None,
    'crp': None,
    'csb': None,
    'cus': None,
    'cze': 'cs',
    'dak': None,
    'dan': 'da',
    'dar': None,
    'day': None,
    'del': None,
    'den': None,
    'dgr': None,
    'din': None,
    'div': 'dv',
    'doi': None,
    'dra': None,
    'dsb': None,
    'dua': None,
    'dum': None,
    'dut': 'nl',
    'dyu': None,
    'dzo': 'dz',
    'efi': None,
    'egy': None,
    'eka': None,
    'elx': None,
    'eng': 'en',
    'enm': None,
    'epo': 'eo',
    'est': 'et',
    'ewe': 'ee',
    'ewo': None,
    'fan': None,
    'fao': 'fo',
    'fat': None,
    'fij': 'fj',
    'fil': None,
    'fin': 'fi',
    'fiu': None,
    'fon': None,
    'fre': 'fr',
    'frm': None,
    'fro': None,
    'frr': None,
    'frs': None,
    'fry': 'fy',
    'ful': 'ff',
    'fur': None,
    'gaa': None,
    'gay': None,
    'gba': None,
    'gem': None,
    'geo': 'ka',
    'ger': 'de',
    'gez': None,
    'gil': None,
    'gla': 'gd',
    'gle': 'ga',
    'glg': 'gl',
    'glv': 'gv',
    'gmh': None,
    'goh': None,
    'gon': None,
    'gor': None,
    'got': None,
    'grb': None,
    'grc': None,
    'gre': 'el',
    'grn': 'gn',
    'gsw': None,
    'guj': 'gu',
    'gwi': None,
    'hai': None,
    'hat': 'ht',
    'hau': 'ha',
    'haw': None,
    'heb': 'he',
    'her': 'hz',
    'hil': None,
    'him': None,
    'hin': 'hi',
    'hit': None,
    'hmn': None,
    'hmo': 'ho',
    'hrv': 'hr',
    'hsb': None,
    'hun': 'hu',
    'hup': None,
    'iba': None,
    'ibo': 'ig',
    'ice': 'is',
    'ido': 'io',
    'iii': 'ii',
    'ijo': None,
    'iku': 'iu',
    'ile': 'ie',
    'ilo': None,
    'ina': 'ia',
    'inc': None,
    'ind': 'id',
    'ine': None,
    'inh': None,
    'ipk': 'ik',
    'ira': None,
    'iro': None,
    'ita': 'it',
    'jav': 'jv',
    'jbo': None,
    'jpn': 'ja',
    'jpr': None,
    'jrb': None,
    'kaa': None,
    'kab': None,
    'kac': None,
    'kal': 'kl',
    'kam': None,
    'kan': 'kn',
    'kar': None,
    'kas': 'ks',
    'kau': 'kr',
    'kaw': None,
    'kaz': 'kk',
    'kbd': None,
    'kha': None,
    'khi': None,
    'khm': 'km',
    'kho': None,
    'kik': 'ki',
    'kin': 'rw',
    'kir': 'ky',
    'kmb': None,
    'kok': None,
    'kom': 'kv',
    'kon': 'kg',
    'kor': 'ko',
    'kos': None,
    'kpe': None,
    'krc': None,
    'krl': None,
    'kro': None,
    'kru': None,
    'kua': 'kj',
    'kum': None,
    'kur': 'ku',
    'kut': None,
    'lad': None,
    'lah': None,
    'lam': None,
    'lao': 'lo',
    'lat': 'la',
    'lav': 'lv',
    'lez': None,
    'lim': 'li',
    'lin': 'ln',
    'lit': 'lt',
    'lol': None,
    'loz': None,
    'ltz': 'lb',
    'lua': None,
    'lub': 'lu',
    'lug': 'lg',
    'lui': None,
    'lun': None,
    'luo': None,
    'lus': None,
    'mac': 'mk',
    'mad': None,
    'mag': None,
    'mah': 'mh',
    'mai': None,
    'mak': None,
    'mal': 'ml',
    'man': None,
    'mao': 'mi',
    'map': None,
    'mar': 'mr',
    'mas': None,
    'may': 'ms',
    'mdf': None,
    'mdr': None,
    'men': None,
    'mga': None,
    'mic': None,
    'min': None,
    'mis': None,
    'mkh': None,
    'mlg': 'mg',
    'mlt': 'mt',
    'mnc': None,
    'mni': None,
    'mno': None,
    'moh': None,
    'mon': 'mn',
    'mos': None,
    'mul': None,
    'mun': None,
    'mus': None,
    'mwl': None,
    'mwr': None,
    'myn': None,
    'myv': None,
    'nah': None,
    'nai': None,
    'nap': None,
    'nau': 'na',
    'nav': 'nv',
    'nbl': 'nr',
    'nde': 'nd',
    'ndo': 'ng',
    'nds': None,
    'nep': 'ne',
    'new': None,
    'nia': None,
    'nic': None,
    'niu': None,
    'nno': 'nn',
    'nob': 'nb',
    'nog': None,
    'non': None,
    'nor': 'no',
    'nqo': None,
    'nso': None,
    'nub': None,
    'nwc': None,
    'nya': 'ny',
    'nym': None,
    'nyn': None,
    'nyo': None,
    'nzi': None,
    'oci': 'oc',
    'oji': 'oj',
    'ori': 'or',
    'orm': 'om',
    'osa': None,
    'oss': 'os',
    'ota': None,
    'oto': None,
    'paa': None,
    'pag': None,
    'pal': None,
    'pam': None,
    'pan': 'pa',
    'pap': None,
    'pau': None,
    'peo': None,
    'per': 'fa',
    'phi': None,
    'phn': None,
    'pli': 'pi',
    'pol': 'pl',
    'pon': None,
    'por': 'pt',
    'pra': None,
    'pro': None,
    'pus': 'ps',
    'que': 'qu',
    'raj': None,
    'rap': None,
    'rar': None,
    'roa': None,
    'roh': 'rm',
    'rom': None,
    'rum': 'ro',
    'run': 'rn',
    'rup': None,
    'rus': 'ru',
    'sad': None,
    'sag': 'sg',
    'sah': None,
    'sai': None,
    'sal': None,
    'sam': None,
    'san': 'sa',
    'sas': None,
    'sat': None,
    'scn': None,
    'sco': None,
    'sel': None,
    'sem': None,
    'sga': None,
    'sgn': None,
    'shn': None,
    'sid': None,
    'sin': 'si',
    'sio': None,
    'sit': None,
    'sla': None,
    'slo': 'sk',
    'slv': 'sl',
    'sma': None,
    'sme': 'se',
    'smi': None,
    'smj': None,
    'smn': None,
    'smo': 'sm',
    'sms': None,
    'sna': 'sn',
    'snd': 'sd',
    'snk': None,
    'sog': None,
    'som': 'so',
    'son': None,
    'sot': 'st',
    'spa': 'es',
    'srd': 'sc',
    'srn': None,
    'srp': 'sr',
    'srr': None,
    'ssa': None,
    'ssw': 'ss',
    'suk': None,
    'sun': 'su',
    'sus': None,
    'sux': None,
    'swa': 'sw',
    'swe': 'sv',
    'syc': None,
    'syr': None,
    'tah': 'ty',
    'tai': None,
    'tam': 'ta',
    'tat': 'tt',
    'tel': 'te',
    'tem': None,
    'ter': None,
    'tet': None,
    'tgk': 'tg',
    'tgl': 'tl',
    'tha': 'th',
    'tib': 'bo',
    'tig': None,
    'tir': 'ti',
    'tiv': None,
    'tkl': None,
    'tlh': None,
    'tli': None,
    'tmh': None,
    'tog': None,
    'ton': 'to',
    'tpi': None,
    'tsi': None,
    'tsn': 'tn',
    'tso': 'ts',
    'tuk': 'tk',
    'tum': None,
    'tup': None,
    'tur': 'tr',
    'tut': None,
    'tvl': None,
    'twi': 'tw',
    'tyv': None,
    'udm': None,
    'uga': None,
    'uig': 'ug',
    'ukr': 'uk',
    'umb': None,
    'und': None,
    'urd': 'ur',
    'uzb': 'uz',
    'vai': None,
    'ven': 've',
    'vie': 'vi',
    'vol': 'vo',
    'vot': None,
    'wak': None,
    'wal': None,
    'war': None,
    'was': None,
    'wel': 'cy',
    'wen': None,
    'wln': 'wa',
    'wol': 'wo',
    'xal': None,
    'xho': 'xh',
    'yao': None,
    'yap': None,
    'yid': 'yi',
    'yor': 'yo',
    'ypk': None,
    'zap': None,
    'zbl': None,
    'zen': None,
    'zgh': None,
    'zha': 'za',
    'znd': None,
    'zul': 'zu',
    'zun': None,
    'zxx': None,
    'zza': None
}


SONAR_APP_PREFERRED_LANGUAGES = ['eng', 'fre', 'ger', 'ita']
"""Order of preferred languages for displaying value in views."""

SONAR_APP_ENABLE_CORS = True

SONAR_APP_DISABLE_PERMISSION_CHECKS = False
"""Disable permission checks during API calls. Useful when API is test from
command line or progams like postman."""

SONAR_APP_UI_VERSION = '1.6.0'

SONAR_APP_DEFAULT_ORGANISATION = 'global'
"""Default organisation key."""

SONAR_APP_STORAGE_PATH = None
"""File storage location."""

SONAR_APP_EXPORT_SERIALIZERS = {
    'org': ('sonar.modules.organisations.serializers.schemas.export:'
            'ExportSchemaV1'),
    'user': ('sonar.modules.users.serializers.schemas.export:'
             'ExportSchemaV1'),
}

SONAR_APP_FILE_PREVIEW_EXTENSIONS = [
    'jpeg', 'jpg', 'gif', 'png', 'pdf', 'json', 'xml', 'csv', 'zip', 'md'
]
"""List of extensions for which files can be previewed."""

SONAR_APP_WEBDAV_HEG_HOST = 'https://share.rero.ch/HEG'
SONAR_APP_WEBDAV_HEG_USER = None
SONAR_APP_WEBDAV_HEG_PASSWORD = None
"""Connection data to webdav for HEG."""

SONAR_APP_HEG_DATA_DIRECTORY = './data/heg'

SONAR_APP_ORGANISATION_CONFIG = {
    'hepvs': {
        'home_template': 'dedicated/hepvs/home.html',
        'projects': True
    }
}
# Custom resources for organisations

# ARK
# ===

# SONAR_APP_ARK_USER = 'test'
"""Username for the NMA server."""
# SONAR_APP_ARK_PASSWORD = 'test'
"""Password for the NMA server."""
# SONAR_APP_ARK_RESOLVER = 'https://n2t.net'
"""ARK resolver URL."""
# SONAR_APP_ARK_NMA = 'https://www.arketype.ch'
"""ARK Name Mapping Authority: a service provider server."""
# SONAR_APP_ARK_NAAN = '99999'
"""ARK prefix corresponding to an organisation."""
# SONAR_APP_ARK_SCHEME = 'ark:'
"""ARK scheme."""
# SONAR_APP_ARK_SHOULDER = 'ffk3'
"""ARK Shoulder, can be multiple for a given organisation."""

SONAR_APP_SWISSCOVERY_SEARCH_URL = 'https://swisscovery.slsp.ch/view/sru/41SLSP_NETWORK'
SONAR_APP_SWISSCOVERY_SEARCH_VERSION = '1.1'

# Link on document identifier
# Add the source identifier in lowercase (Ex: orcid)
SONAR_APP_DOCUMENT_IDENTIFIER_LINK = {
    'bf:Doi': {
        'default': 'https://doi.org/_identifier_'
    },
    'bf:Local': {
        'orcid': 'https://orcid.org/_identifier_',
        'swisscovery': 'https://swisscovery.slsp.ch/permalink/41SLSP_NETWORK/1ufb5t2/alma_identifier_'
    },
    'bf:Urn': {
        'default': 'https://nbn-resolving.org/_identifier_'
    }
}

# URN
# ===
# Config to generate URN identifiers for organisations. The real configuration
# should be set during the deployment.
SONAR_APP_DOCUMENT_URN = {
    'organisations': {
        'unifr': {
            'types': ['coar:c_db06'],
            'code': 6
        },
        'usi': {
            'types': ['coar:c_db06'],
            'code': 1
        }
    }
}

# DNB REST API config
# The real configuration should be set during the deployment.
SONAR_APP_URN_DNB_BASE_URL = ''
SONAR_APP_URN_DNB_USERNAME = ''
SONAR_APP_URN_DNB_PASSWORD = ''
SONAR_APP_URN_DNB_BASE_URN = 'urn:nbn:ch:rero-'
