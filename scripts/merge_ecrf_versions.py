"""Merge forms with multiple publish dates to a single form.

The following logic will be applied hen this process occurs:

* The max publish date will be the publish date of the form/variable
* The title of the variable with the max publish date will be used
* Choices will be merged, i.e. the union of all choice keys from all forms will
  be used
* The values of the choice keys will be taken from the form with the
  greatest publish date
* System variables will remain

Note: This is a PYTHON 3 script.

Sample usage:

python occams_merge_publish_dates.py input.csv output.csv
"""
import sys
import csv
import re
import click
from datetime import datetime


def merge_choices(variables):
    """Merge the choices for all form versions to a single set of choices.

    :variables: list of dict reader rows
    :return: merged choices string
    """
    sorted_variables = sorted(
        variables,
        key=lambda k: k['publish_date']
    )

    choices = [row['choices'] for row in sorted_variables]
    choices = [re.compile(';(?=\d=)').split(choice) for choice in choices]
    converted_choices = []
    for choice in choices:
        choice_dict = {}
        for choice_str in choice:
            parsed = choice_str.split('=')
            choice_dict[parsed[0]] = parsed[1]
        converted_choices.append(choice_dict)

    merged = {}

    for choice in converted_choices:
        merged.update(choice)

    # convert merged dict into OCCAMS choices string
    merged_choices = ';'.join('{}={}'.format(
        key, val) for key, val in sorted(merged.items()))

    return merged_choices


def get_file_output(reader, forms):
    """Derive the final list of rows to be written."""
    output = []
    for row in reader:
        # no form means it's a system variable and should be included in the
        # output
        if row['form'] == u'':
            output.append(row)
            continue

        publish_date = datetime.strptime(
            row['publish_date'], '%m/%d/%y')
        publish_date = publish_date.date()
        form = row['form']
        variable = row['field']

        # if the publish date matches, this is a merged form and should be
        # included in the output
        if forms[form][variable][0]['publish_date'] == publish_date:
            output.append(row)

    return output


def get_forms(reader):
    """Read the input file and create a data structure of forms.

    :reader: csvDictReader object
    :return: dictionary of forms
    """
    forms = {}

    reader.fieldnames
    for row in reader:
        form = row['form']
        variable = row['field']
        # if there is no form, it is a system record, we need to bypass
        if form == u'':
            continue

        publish_date = datetime.strptime(row['publish_date'], '%m/%d/%y')
        row['publish_date'] = publish_date.date()

        if form not in forms:
            forms[form] = {}
            forms[form][variable] = []
            forms[form][variable].append(row)
        else:
            if variable not in forms[form]:
                forms[form][variable] = []

            forms[form][variable].append(row)

    return forms


def merge_forms(forms):
    """Merge forms with multiple versions.

    :forms: dictionary of forms obtained from the input file
    :return: merged forms data structure
    """
    for form in forms:
        for variable in forms[form]:
            # we only need to merge if there is more than one publish date
            if len(forms[form][variable]) > 1:
                dates = [row['publish_date'] for row in forms[form][variable]]
                max_date_index = dates.index(max(dates))
                data_type = forms[form][variable][max_date_index]['type']
                # we only need to merge if it's a choice
                if data_type == u'choice':
                    merged_choices = merge_choices(forms[form][variable])
                    # overwrite choices with merged choices
                    forms[form][variable][max_date_index]['choices'] \
                        = merged_choices

                # only keep the row with the most recent publish date
                forms[form][variable] = [forms[form][variable][max_date_index]]

    return forms


@click.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('target_file')
def process(source_file, target_file):
    """Process the inpug file.

    Example of the forms data structure:

    {
    'demographics': {
        'race': [
            {},
            {}
        ]
    }
    }
    """
    with open(source_file, 'r', encoding="utf-8") as _in:
        reader = csv.DictReader(_in)

        forms = get_forms(reader)

    forms = merge_forms(forms)

    with open(source_file, 'r', encoding="utf-8") as _in:
        reader = csv.DictReader(_in)
        headers = reader.fieldnames

        with open(target_file, 'w', encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=headers)
            writer.writeheader()

            output = get_file_output(reader, forms)

            for row in output:
                writer.writerow(row)

if __name__ == '__main__':
    sys.exit(process())
