"""Test occams merge publish date script."""

import io
import csv
import pytest
import datetime


def test_merge_choices():
    """Test that choices string merges correctly."""
    from occams_merge_publish_dates import merge_choices

    variables = [
        {
            '': '',
            'choices': '0=No;1=Yes;4=NoWay',
            'decimal_places': '',
            'description': '',
            'field': 'schedvis',
            'form': 'Clinical Assessment - Screening - 593',
            'is_collection': 'FALSE',
            'is_private': 'FALSE',
            'is_required': 'TRUE',
            'is_system': 'FALSE',
            'order': '100002001',
            'publish_date': datetime.date(2013, 7, 26),
            'table': 'ClinicalAssessmentScreening593',
            'title': 'Was a clinic visit scheduled with the subject?',
            'type': 'choice'
        },
        {
            '': '',
            'choices': '0=No;1=Yes;2=Sure',
            'decimal_places': '',
            'description': '',
            'field': 'schedvis',
            'form': 'Clinical Assessment - Screening - 593',
            'is_collection': 'FALSE',
            'is_private': 'FALSE',
            'is_required': 'TRUE',
            'is_system': 'FALSE',
            'order': '100002001',
            'publish_date': datetime.date(2013, 7, 26),
            'table': 'ClinicalAssessmentScreening593',
            'title': 'Was a clinic visit scheduled with the subject?',
            'type': 'choice'
        },
        {
            '': '',
            'choices': '0=No;1=Okay',
            'decimal_places': '',
            'description': '',
            'field': 'schedvis',
            'form': 'Clinical Assessment - Screening - 593',
            'is_collection': 'FALSE',
            'is_private': 'FALSE',
            'is_required': 'TRUE',
            'is_system': 'FALSE',
            'order': '100001001',
            'publish_date': datetime.date(2015, 1, 11),
            'table': 'ClinicalAssessmentScreening593',
            'title': 'Was a clinic visit scheduled with the subject?',
            'type': 'choice'
        }
    ]

    actual = merge_choices(variables)
    expected = '0=No;1=Okay;2=Sure;4=NoWay'

    assert actual == expected


def test_get_file_output():
    """Test the correct output is filtered."""
    from occams_merge_publish_dates import get_file_output

    forms = {
        'Antibiotic, Diet, and Supplement Intake Survey':
            {'antibiotic': [
                {'': '',
                 'choices': '0=No;1=Yes;3=Not sure;4=Refuse to answer',
                 'decimal_places': '',
                 'description': '(ex. amoxicillin, azithromycin, doxycycline, '
                                'ciprofloxacin, etc.)\n',
                 'field': 'antibiotic',
                 'form': 'Antibiotic, Diet, and Supplement Intake Survey',
                 'is_collection': 'FALSE',
                 'is_private': 'FALSE',
                 'is_required': 'TRUE',
                 'is_system': 'FALSE',
                 'order': '100000000',
                 'publish_date': datetime.date(2013, 3, 1),
                 'table': 'AntibioticDietAndSupplementIntakeSurvey',
                 'title': 'In the past 3 months has the subject consumed an '
                          'antibiotic?',
                 'type': 'choice'}]}
    }

    output = io.StringIO()
    output.write('table,form,publish_date,field,title,description,'
                 'is_required,is_system,is_collection,is_private,type,'
                 'decimal_places,choices,order\n')
    output.write('AdverseEventsLog,,,modify_user,,,TRUE,TRUE,FALSE,FALSE,'
                 'string,,,\n')
    output.write('AntibioticDietAndSupplementIntakeSurvey,"Antibiotic, Diet,'
                 ' and Supplement Intake Survey",2/28/13,antibiotic,'
                 'In the past 3 months?,(ex. amoxicillin),TRUE,FALSE,FALSE,'
                 'FALSE,choice,0=No;1=Yes;3=Not sure;4=Refuse to answer,'
                 '100000000\n')
    output.write('AntibioticDietAndSupplementIntakeSurvey,"Antibiotic, Diet,'
                 ' and Supplement Intake Survey",3/1/13,antibiotic,In the '
                 'past 3 months?,(ex. amoxicillin),TRUE,FALSE,FALSE,FALSE,'
                 'choice,0=No;1=Yes;3=Not sure;4=Refuse to answer,100000000\n')

    output.seek(0)

    reader = csv.DictReader(output)
    reader.fieldnames

    actual = get_file_output(reader, forms)

    output.close()

    assert len(actual) == 2
    assert actual[0]['form'] == ''
    assert actual[1]['publish_date'] == '3/1/13'


def test_get_forms():
    """Test the correct output is filtered."""
    from occams_merge_publish_dates import get_forms

    output = io.StringIO()
    output.write('table,form,publish_date,field,title,description,'
                 'is_required,is_system,is_collection,is_private,type,'
                 'decimal_places,choices,order\n')
    output.write('AdverseEventsLog,,,modify_user,,,TRUE,TRUE,FALSE,FALSE,'
                 'string,,,\n')
    output.write('AntibioticDietAndSupplementIntakeSurvey,"Antibiotic, Diet,'
                 ' and Supplement Intake Survey",2/28/13,antibiotic,'
                 'In the past 3 months?,(ex. amoxicillin),TRUE,FALSE,FALSE,'
                 'FALSE,choice,0=No;1=Yes;3=Not sure;4=Refuse to answer,'
                 '100000000\n')
    output.write('AntibioticDietAndSupplementIntakeSurvey,"Antibiotic, Diet,'
                 ' and Supplement Intake Survey",3/1/13,antibiotic,In the '
                 'past 3 months?,(ex. amoxicillin),TRUE,FALSE,FALSE,FALSE,'
                 'choice,0=No;1=Yes;3=Not sure;4=Refuse to answer,100000000\n')

    output.seek(0)

    reader = csv.DictReader(output)
    reader.fieldnames

    actual = get_forms(reader)

    output.close()

    assert len(actual) == 1
    assert actual['Antibiotic, Diet, and Supplement Intake Survey'] \
                 ['antibiotic'][0] \
                 ['publish_date'] == datetime.date(2013, 2, 28)
    assert actual['Antibiotic, Diet, and Supplement Intake Survey'] \
                 ['antibiotic'][1]['publish_date'] == datetime.date(2013, 3, 1)


def test_merge_forms():
    """Test the correct output is filtered."""
    from occams_merge_publish_dates import merge_forms

    forms = {
        'Antibiotic, Diet, and Supplement Intake Survey':
            {'antibiotic': [
                {'': '',
                 'choices': '0=No;1=Yes;3=Not sure;4=Refuse to answer',
                 'decimal_places': '',
                 'description': '(ex. amoxicillin, azithromycin, doxycycline, '
                                'ciprofloxacin, etc.)\n',
                 'field': 'antibiotic',
                 'form': 'Antibiotic, Diet, and Supplement Intake Survey',
                 'is_collection': 'FALSE',
                 'is_private': 'FALSE',
                 'is_required': 'TRUE',
                 'is_system': 'FALSE',
                 'order': '100000000',
                 'publish_date': datetime.date(2013, 2, 28),
                 'table': 'AntibioticDietAndSupplementIntakeSurvey',
                 'title': 'In the past 3 months has the subject consumed an '
                          'antibiotic?',
                 'type': 'choice'},
                {'': '',
                 'choices': '0=No;1=Yes;3=Not sure;4=Refuse to answer',
                 'decimal_places': '',
                 'description': '(ex. amoxicillin, azithromycin, doxycycline, '
                                'ciprofloxacin, etc.)\n',
                 'field': 'antibiotic',
                 'form': 'Antibiotic, Diet, and Supplement Intake Survey',
                 'is_collection': 'FALSE',
                 'is_private': 'FALSE',
                 'is_required': 'TRUE',
                 'is_system': 'FALSE',
                 'order': '100000000',
                 'publish_date': datetime.date(2013, 3, 1),
                 'table': 'AntibioticDietAndSupplementIntakeSurvey',
                 'title': 'In the past 3 months has the subject consumed an '
                          'antibiotic?',
                 'type': 'choice'}]}
    }

    actual = merge_forms(forms)

    assert len(actual) == 1
    assert actual['Antibiotic, Diet, and Supplement Intake Survey'] \
                 ['antibiotic'][0]['publish_date'] == datetime.date(2013, 3, 1)
