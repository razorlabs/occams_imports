def test_extract_value_by_variable():
    """
    It should return the value in the current row if conversion is by variable
    """

    import pandas as pd
    from occams_imports.importers.imputation import _extract_value

    frame = pd.DataFrame({'some_schema_some_attribute': [420]})

    conversion = {
        'byVariable': True,
        'schema': {'name': 'some_schema'},
        'attribute': {'name': 'some_attribute', 'type': 'string'}
    }

    result = _extract_value(conversion, frame.iloc[0])

    assert result == 420


def test_extract_value_by_value():
    """
    It should return the value in the conversion if conversion is by value
    """

    import pandas as pd
    from occams_imports.importers.imputation import _extract_value

    row = pd.DataFrame()

    conversion = {'byValue': True, 'value': 420}

    result = _extract_value(conversion, row)

    assert result == 420
