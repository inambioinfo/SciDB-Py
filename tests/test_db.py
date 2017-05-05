import numpy
import pytest

from scidbpy.db import connect, iquery
from scidbpy.schema import Schema

variety_atts_types = """b  :bool       null,
                        c  :char       null,
                        d  :double     null,
                        f  :float      null,
                        i8 :int8       null,
                        i16:int16      null,
                        i32:int32      null,
                        i64:int64      null,
                        s  :string     null,
                        u8 :uint8      null,
                        u16:uint16     null,
                        u32:uint32     null,
                        u64:uint64     null"""

variety_queries = {
    'create': [
        'create array variety_i<{}>[i=0:2]'.format(variety_atts_types),

        'create array variety<{}>[i=0:2; j=-2:0; k=0:*]'.format(
            variety_atts_types),

        """store(
             build(
               variety_i,
               '[(true,
                  "a",
                  1.7976931348623157e+308,
                  -3.4028234663852886e+38,
                  -128,
                  -32768,
                  -2147483648,
                  -9223372036854775808,
                  "abcDEF123",
                  255,
                  65535,
                  4294967295,
                  18446744073709551615),
                 (null,
                  null,
                  null,
                  ?34,
                  ?7,
                  ?15,
                  ?31,
                  ?63,
                  null,
                  null,
                  null,
                  null,
                  null),
                 (?99,
                  ?65,
                  -inf,
                  inf,
                  null,
                  null,
                  null,
                  null,
                  ?99,
                  ?8,
                  ?16,
                  ?32,
                  ?64)]',
               true),
             variety_i)""",

        """store(
             filter(
               redimension(
                 cross_join(
                   cross_join(
                     variety_i,
                     build(<x:int8 null>[j=-2:0], null)),
                   build(<y:int8 null>[k=0:2], null)),
                 variety),
               j != 0 and k != 1),
             variety)"""],
    'clean': [
        'remove(variety_i)',
        'remove(variety)']}

variety_atts = [at.split(':')[0].strip()
                for at in variety_atts_types.split(',')]

variety_schema = variety_queries['create'][1][len('create array '):]

variety_array = numpy.array(
    [((255, True),
      (255, b'a'),
      (255, 1.7976931348623157e+308),
      (255, -3.4028234663852886e+38),
      (255, -128),
      (255, -32768),
      (255, -2147483648),
      (255, -9223372036854775808),
      (255, 'abcDEF123'),
      (255, 255),
      (255, 65535),
      (255, 4294967295),
      (255, 18446744073709551615),
      0, -2, 0),
     ((0, False),
      (0, b''),
      (0, 0.0),
      (34, 0.0),
      (7, 0),
      (15, 0),
      (31, 0),
      (63, 0),
      (0, ''),
      (0, 0),
      (0, 0),
      (0, 0),
      (0, 0),
      1, -2, 0),
     ((99, False),
      (65, b''),
      (255, -numpy.inf),
      (255, numpy.inf),
      (0, 0),
      (0, 0),
      (0, 0),
      (0, 0),
      (99, ''),
      (8, 0),
      (16, 0),
      (32, 0),
      (64, 0),
      2, -2, 0)],
    dtype=[('b', [('null', 'u1'), ('val', '?')]),
           ('c', [('null', 'u1'), ('val', 'S1')]),
           ('d', [('null', 'u1'), ('val', '<f8')]),
           ('f', [('null', 'u1'), ('val', '<f4')]),
           ('i8', [('null', 'u1'), ('val', 'i1')]),
           ('i16', [('null', 'u1'), ('val', '<i2')]),
           ('i32', [('null', 'u1'), ('val', '<i4')]),
           ('i64', [('null', 'u1'), ('val', '<i8')]),
           ('s', [('null', 'u1'), ('val', 'O')]),
           ('u8', [('null', 'u1'), ('val', 'u1')]),
           ('u16', [('null', 'u1'), ('val', '<u2')]),
           ('u32', [('null', 'u1'), ('val', '<u4')]),
           ('u64', [('null', 'u1'), ('val', '<u8')]),
           ('i', '<i8'), ('j', '<i8'), ('k', '<i8')])

variety_values = numpy.array(
    [[True,
      b'a',
      1.7976931348623157e+308,
      -3.4028234663852886e+38,
      -128.0,
      -32768.0,
      -2147483648.0,
      -9.223372036854776e+18,
      'abcDEF123',
      255.0,
      65535.0,
      4294967295.0,
      1.8446744073709552e+19],
     [None,
      None,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      None,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      numpy.nan],
     [None,
      None,
      -numpy.inf,
      numpy.inf,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      None,
      numpy.nan,
      numpy.nan,
      numpy.nan,
      numpy.nan]], dtype=object)


@pytest.fixture(scope='module')
def db():
    return connect()


@pytest.fixture(scope='module')
def variety(db):
    for q in variety_queries['create']:
        iquery(db, q)
    variety = variety_schema.split('<')[0].strip()

    yield variety
    for q in variety_queries['clean']:
        iquery(db, q)


class TestDB:

    @pytest.mark.parametrize('args', [
        {'scidb_auth': ('foo', 'bar')},
        {'scidb_url': 'http://localhost:8080', 'scidb_auth': ('foo', 'bar')},
    ])
    def test_connect_exception(self, args):
        with pytest.raises(Exception):
            connect(**args)

    @pytest.mark.parametrize('query', [
        'list()',
        "list('operators')",
    ])
    def test_iquery(self, db, query):
        assert db.iquery(query) == None
        assert type(db.iquery(query, fetch=True)) == numpy.ndarray

    @pytest.mark.parametrize(('type_name', 'schema'), [
        (type_name, schema)
        for type_name in [
                '{}int{}'.format(pre, sz)
                for pre in ('', 'u')
                for sz in (8, 16, 32, 64)
        ] + [
            'bool',
            'double',
            'float',
            'int8',
            'uint64',
        ]
        for schema in [
                None,
                'build<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10]'.format(type_name),
                '<val:{}>[i]'.format(type_name),
        ]
    ])
    @pytest.mark.parametrize('atts_only', [
        True,
        False,
    ])
    def test_fetch_numpy(self, db, type_name, atts_only, schema):
        # NumPy array
        ar = iquery(
            db,
            'build(<val:{}>[i=1:10,10,0], random())'.format(type_name),
            fetch=True,
            atts_only=atts_only,
            schema=schema)
        assert ar.shape == (10,)
        assert ar.ndim == 1

    @pytest.mark.parametrize(('type_name', 'schema'), [
        (type_name, schema)
        for type_name in [
                '{}int{}'.format(pre, sz)
                for pre in ('', 'u')
                for sz in (8, 16, 32, 64)
        ] + [
            'bool',
            'double',
            'float',
            'int8',
            'uint64',
        ]
        for schema in [
                None,
                'build<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10]'.format(type_name),
                '<val:{}>[i]'.format(type_name),
        ]
    ])
    @pytest.mark.parametrize('index', [
        False,
        None,
        [],
    ])
    def test_fetch_dataframe(self, db, type_name, index, schema):
        # Pandas DataFrame
        ar = iquery(
            db,
            'build(<val:{}>[i=1:10,10,0], random())'.format(type_name),
            fetch=True,
            as_dataframe=True,
            index=index,
            schema=schema)
        assert ar.shape == (10, 2)
        assert ar.ndim == 2

    @pytest.mark.parametrize(('type_name', 'schema'), [
        (type_name, schema)
        for type_name in [
                '{}int{}'.format(pre, sz)
                for pre in ('', 'u')
                for sz in (8, 16, 32, 64)
        ] + [
            'bool',
            'double',
            'float',
            'int8',
            'uint64',
        ]
        for schema in [
                None,
                'build<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10]'.format(type_name),
                '<val:{}>[i]'.format(type_name),
        ]
    ])
    @pytest.mark.parametrize('index', [
        False,
        None,
        [],
    ])
    def test_fetch_dataframe_atts(self, db, type_name, index, schema):
        # Pandas DataFrame
        ar = iquery(
            db,
            'build(<val:{}>[i=1:10,10,0], random())'.format(type_name),
            fetch=True,
            atts_only=True,
            as_dataframe=True,
            index=index,
            schema=schema)
        assert ar.shape == (10, 1)
        assert ar.ndim == 2

    @pytest.mark.parametrize(('type_name', 'schema'), [
        (type_name, schema)
        for type_name in [
                '{}int{}'.format(pre, sz)
                for pre in ('', 'u')
                for sz in (8, 16, 32, 64)
        ] + [
            'bool',
            'double',
            'float',
            'int8',
            'uint64',
        ]
        for schema in [
                None,
                'build<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10,10,0]'.format(type_name),
                '<val:{}>[i=1:10]'.format(type_name),
                '<val:{}>[i]'.format(type_name),
        ]
    ])
    @pytest.mark.parametrize('index', [
        True,
        ['val'],
    ])
    def test_fetch_dataframe_index(self, db, type_name, index, schema):
        # Pandas DataFrame, index
        ar = iquery(
            db,
            'build(<val:{}>[i=1:10,10,0], random())'.format(type_name),
            fetch=True,
            as_dataframe=True,
            index=index,
            schema=schema)
        assert ar.shape == (10, 1)
        assert ar.ndim == 2

    @pytest.mark.parametrize('schema', [
        None,
        variety_schema,
        Schema.fromstring(variety_schema),
    ])
    def test_variety_numpy(self, db, variety, schema):
        # NumPy array
        ar = iquery(db, 'scan({})'.format(variety),
                    fetch=True, schema=schema)
        assert ar.shape == (12,)
        assert ar.ndim == 1
        assert ar[0] == variety_array[0]
        assert ar[4] == variety_array[1]
        assert ar[8] == variety_array[2]

    @pytest.mark.parametrize('schema', [
        None,
        variety_schema,
        Schema.fromstring(variety_schema),
    ])
    def test_variety_numpy_atts(self, db, variety, schema):
        # NumPy array, atts_only
        ar = iquery(db, 'scan({})'.format(variety),
                    fetch=True, atts_only=True, schema=schema)
        assert ar.shape == (12,)
        assert ar.ndim == 1
        assert ar[0] == variety_array[variety_atts][0]
        assert ar[4] == variety_array[variety_atts][1]
        assert ar[8] == variety_array[variety_atts][2]

    @pytest.mark.parametrize('schema', [
        None,
        variety_schema,
        Schema.fromstring(variety_schema),
    ])
    def test_variety_dataframe(self, db, variety, schema):
        # Pandas DataFrame, atts_only
        ar = iquery(db, 'scan({})'.format(variety),
                    fetch=True, as_dataframe=True)
        assert ar.shape == (12, 1)
        assert ar.ndim == 1
        assert numpy.all(ar[0:1].values[0, :13] == variety_values[0])

        # Values which differ have to be NAN
        ln = ar[4:5]
        assert numpy.all(
            numpy.isnan(
                ln[ar.columns[ln.values[0, :13] != variety_values[1]]]))

        ln = ar[8:9]
        assert numpy.all(
            numpy.isnan(
                ln[ar.columns[ln.values[0, :13] != variety_values[2]]]))

    @pytest.mark.parametrize('schema', [
        None,
        variety_schema,
        Schema.fromstring(variety_schema),
    ])
    def test_variety_dataframe_atts(self, db, variety, schema):
        # Pandas DataFrame, atts_only
        ar = iquery(db, 'scan({})'.format(variety),
                    fetch=True, as_dataframe=True, atts_only=True)
        assert ar.shape == (12, 1)
        assert ar.ndim == 1
        assert numpy.all(ar[0:1].values == variety_values[0])

        # Values which differ have to be NAN
        ln = ar[4:5]
        assert numpy.all(
            numpy.isnan(
                ln[ar.columns[(ln.values != variety_values[1])[0]]]))

        ln = ar[8:9]
        assert numpy.all(
            numpy.isnan(
                ln[ar.columns[(ln.values != variety_values[2])[0]]]))

    @pytest.mark.parametrize('schema', [
        None,
        variety_schema,
        Schema.fromstring(variety_schema),
    ])
    @pytest.mark.parametrize('index', [
        True,
        ('i', 'j', 'k'),
    ])
    def test_variety_dataframe_index(self, db, variety, schema, index):
        # Pandas DataFrame
        ar = iquery(db, 'scan({})'.format(variety),
                    fetch=True, as_dataframe=True, index=index)
        assert ar.shape == (12, 13)
        assert ar.ndim == 1
        assert numpy.all(
            ar.ix[[(0, -2, 0)]].values == variety_values[0])

        # Values which differ have to be NAN
        ln = ar.ix[[(1, -2, 0)]]
        assert numpy.all(
            numpy.isnan(
                ln[ar.columns[(ln.values != variety_values[1])[0]]]))

        ln = ar.ix[[(2, -2, 0)]]
        assert numpy.all(
            numpy.isnan(
                ln[ar.columns[(ln.values != variety_values[2])[0]]]))
