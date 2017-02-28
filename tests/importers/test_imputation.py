import pytest
import numpy as np


def test_query_mappings(
        db_session, study_factory, status_factory, mapping_factory):
    """
    It should query the mappings for a given project
    """

    from occams_imports.importers.imputation import _query_mappings

    status = status_factory.create()
    project_foo = study_factory.create()
    project_bar = study_factory.create()
    mapping_factory.create(study=project_foo, status=status, type='imputation')
    mapping_factory.create(study=project_bar, status=status, type='imputation')
    db_session.flush()

    result = _query_mappings(db_session, project_foo.name).one()

    assert result.study == project_foo


def _test_count_mappings(
        db_session, study_factory, status_factory, mapping_factory):
    """
    It should be able to count the number of mappings in a result set
    """

    from occams_imports.importers.imputation import \
        _count_mappings, _query_mappings

    status = status_factory.create()
    project_foo = study_factory.create()
    project_bar = study_factory.create()
    mapping_factory.create_batch(
        study=project_foo, status=status, type='imputation', size=3)
    mapping_factory.create_batch(
        study=project_bar, status=status, type='imputation', size=5)
    db_session.flush()

    mappings = _query_mappings(db_session, project_foo.name).one()
    result = _count_mappings(mappings)

    assert result == 3


def test_extract_value_by_variable():
    """
    It should return the value in the current row if conversion is by variable
    """

    import pandas as pd
    from occams_imports.importers.imputation import _extract_value

    conversion = {
        'byVariable': True,
        'schema': {'name': 'some_schema'},
        'attribute': {'name': 'some_variable'}
    }
    row = pd.Series({'some_schema_some_variable': 420})
    result = _extract_value(conversion, row)

    assert result == 420


def test_extract_value_by_value():
    """
    It should return the value in the conversion if conversion is by value
    """

    import pandas as pd
    from occams_imports.importers.imputation import _extract_value

    conversion = {'byValue': True, 'value': 420}
    row = pd.Series()
    result = _extract_value(conversion, row)

    assert result == conversion['value']


def test_extract_value_by_unknown():
    """
    It should return NaN if the conversion is malformed/unsupporeted
    """

    import pandas as pd
    import numpy as np
    from occams_imports.importers.imputation import _extract_value

    row = pd.DataFrame()

    conversion = {'byValue': False, 'byVariable': False, 'value': 420}

    result = _extract_value(conversion, row)

    assert result is np.nan


def test_impute_group_require_conversions():
    """
    It should contain at least one conversion
    """

    import pandas as pd
    import numpy as np
    from occams_imports.importers.imputation import _impute_group

    row = pd.Series()
    group = {}
    result = _impute_group(group, row)

    assert result is np.nan


def test_impute_group_single_conversion():

    import pandas as pd
    from occams_imports.importers.imputation import _impute_group

    group = {
        'conversions': [
            {
                'byVariable': True,
                'schema': {'name': 'some_schema'},
                'attribute': {'name': 'some_variable'}
            }
        ]
    }
    row = pd.Series({'some_schema_some_variable': 420})
    result = _impute_group(group, row)

    assert result == 420


@pytest.mark.parametrize(('operator', 'op1', 'op2', 'expected'), [
    ('ADD', 3, 5, 3 + 5),
    ('SUB', 3, 5, 3 - 5),
    ('MUL', 3, 5, 3 * 5),
    ('DIV', 15, 5, 15 / 5),
])
def test_impute_group_operation(operator, op1, op2, expected):
    """
    It should be able to perform supported arithmetic operations
    """

    import pandas as pd
    from occams_imports.importers.imputation import _impute_group

    group = {
        'conversions': [
            {
                'byVariable': True,
                'schema': {'name': 'some_schema'},
                'attribute': {'name': 'some_variable'}
            },
            {
                'byValue': True,
                'value': op2,
                'operator': operator,
            }
        ]
    }
    row = pd.Series({'some_schema_some_variable': op1})
    result = _impute_group(group, row)

    assert result == expected


@pytest.mark.parametrize(('operator', 'op1', 'op2', 'expected'), [
    ('NE', 3, 5, 3 != 5),
    ('NE', 3, 3, 3 != 3),
    ('EQ', 3, 5, 3 == 5),
    ('EQ', 3, 3, 3 == 3),
    ('LT', 3, 5, 3 < 5),
    ('LT', 5, 5, 5 < 5),
    ('LT', 6, 5, 6 < 5),
    ('LTE', 3, 5, 3 <= 5),
    ('LTE', 5, 5, 5 <= 5),
    ('LTE', 6, 5, 6 <= 5),
    ('GTE', 3, 5, 3 >= 5),
    ('GTE', 5, 5, 5 >= 5),
    ('GTE', 6, 5, 6 >= 5),
    ('GT', 6, 5, 6 > 5),
    ('GT', 6, 6, 6 > 6),
])
def test_impute_group_imputation(operator, op1, op2, expected):
    """
    It should be able to check supported logical operators
    """

    import pandas as pd
    from occams_imports.importers.imputation import _impute_group

    group = {
        'conversions': [
            {
                'byVariable': True,
                'schema': {'name': 'some_schema'},
                'attribute': {'name': 'some_variable'}
            },
        ],
        'logic': {
            'operator': 'ALL',
            'imputations': [
                {
                    'operator': operator,
                    'value': op2
                }
            ]
        }
    }
    row = pd.Series({'some_schema_some_variable': op1})
    result = _impute_group(group, row)

    assert result is expected


@pytest.mark.parametrize(
    ('operator', 'operator_result', 'target_value', 'expected'), [
        ('ALL', True, None, None),
        ('ALL', True, 420, 420),
        ('ALL', False, None, np.nan),
        ('ALL', False, 420, np.nan),
        ('ANY', True, None, None),
        ('ANY', True, 420, 420),
        ('ANY', False, None, np.nan),
        ('ANY', False, 420, np.nan),
    ]
)
def test_compile_imputation_choice(
        operator, operator_result, target_value, expected):
    """
    It should return a callback function that can parse a row at a time
    """

    import pandas as pd
    import mock
    from occams_imports.importers import imputation as module
    from occams_imports.importers.imputation import _compile_imputation

    module._impute_group = mock.Mock(return_value=operator_result)

    dummy_groups = [{}]
    row = pd.Series()
    result = _compile_imputation(operator, target_value, dummy_groups)(row)

    assert result is expected


@pytest.mark.parametrize(
    ('operator', 'operator_result', 'target_value', 'expected'), [
        ('ID', 420, None, 420)
    ]
)
def test_compile_imputation_computed(
        operator, operator_result, target_value, expected):
    """
    It should return a callback function that can parse a row at a time
    """

    import pandas as pd
    import mock
    from occams_imports.importers import imputation as module
    from occams_imports.importers.imputation import _compile_imputation

    module._impute_group = mock.Mock(return_value=operator_result)

    dummy_groups = [{}]
    row = pd.Series()
    result = _compile_imputation(operator, target_value, dummy_groups)(row)

    assert result == expected


@pytest.mark.parametrize(('operator'), [('ANY', 'ALL')])
def test_apply_mapping_with_target_choice(
        db_session,
        mapping_factory, schema_factory, attribute_factory,
        operator
        ):
    """
    It should enforce ANY/ALL for choice targets
    """
    import mock
    import pandas as pd
    from occams_imports.importers import imputation as module

    target_value = '003'
    groups = []

    target_schema = schema_factory.create()
    target_attribute = attribute_factory.create(
        schema=target_schema, type='choice')
    mapping = mapping_factory.create(logic={
        'target_schema': target_schema.name,
        'target_variable': target_attribute.name,
        'target_choice': {'name': target_value, 'title': 'Blah'},
        'groups': groups,
        'condition': operator
    })

    module._get_attribute = mock.Mock(return_value=target_attribute)
    module._compile_imputation = mock.Mock(return_value=lambda r: r['source'])

    frame = pd.DataFrame({'source': [1]})
    redis = None
    jobid = '123'
    module._apply_mapping(db_session, redis, jobid, frame, mapping)

    module._compile_imputation.assert_called_with(
        operator, target_value, groups)


def test_apply_mapping_with_computed_scalar(
        db_session,
        mapping_factory, schema_factory, attribute_factory
        ):
    """
    It should enforce ANY/ALL for choice targets
    """

    import mock
    import pandas as pd
    from occams_imports.importers import imputation as module

    group_1 = {'conversions': []}
    group_2 = {'conversions': [], 'logic': {}}

    # The second group will be ignored in a computation
    groups = [group_1, group_2]

    target_schema = schema_factory.create()
    target_attribute = attribute_factory.create(
        schema=target_schema, type='number')
    mapping = mapping_factory.create(logic={
        'target_schema': target_schema.name,
        'target_variable': target_attribute.name,
        'target_choice': None,
        'groups': groups,
        'condition': None,
    })

    module._get_attribute = mock.Mock(return_value=target_attribute)
    module._compile_imputation = mock.Mock(return_value=lambda r: r['source'])

    frame = pd.DataFrame({'source': [1]})
    redis = None
    jobid = '123'
    module._apply_mapping(db_session, redis, jobid, frame, mapping)

    module._compile_imputation.assert_called_with('ID', None, group_1)
