"""Process OCCAMS export files to a csv that's within the DRSC data agreement.

Note: This is a PYTHON 3 script.

This script walks each csv file in the source_dir and converts it to a new file
and writes it to the target_dir

The conversion includes:

* Renaming visit_cycle column to visit
* If more than one visit cycle exists create a new row for each
* Remove columns: id, form_publish_date, state, create_date create_user
                  modify_date modify_user

Sample usage:

python cctg_to_drsc.py source_dir target_dir
"""
import sys
import csv
import os
import click

IGNORE = [
    'id',
    'site',
    'enrollment',
    'enrollment_ids',
    'visit_id',
    'visit_date',
    'form_publish_date',
    'state',
    'create_date',
    'create_user',
    'modify_date',
    'modify_user'
]


def get_headers(headers):
    """Return a list of headers used in the output file.

    Renames a header and filters out headers to be ignored

    :headers: list of raw headers from source file
    :return: list of headers
    """
    # visit_cycles is called visits in the data agreement
    headers = [h.replace('visit_cycles', 'visit') for h in headers]

    # only include column headings not in the data agreement
    headers = [h for h in headers if h not in IGNORE]

    return headers


def get_target(source, headers):
    """Convert source data to format outlined in data agreement.

    :source: a list of dictionaries representing each row in source file
    :headers: a list of headers used in the output file
    :return: a list of dictionaries representing each row in target file
    """
    target = []

    for row in source:
        # we already renamed the header, but we need to rename
        # the key in the data so the values are populated
        row['visit'] = row.pop('visit_cycles')

        # special handling where more than one visit is on a row
        if len(row['visit'].split(';')) > 1:
            rows = row['visit'].split(';')
            for r in rows:
                data = {key: value for key,
                        value in row.items()
                        if key in headers}
                data['visit'] = r
                target.append(data)
            continue
        data = {key: value for key,
                value in row.items()
                if key in headers}
        target.append(data)

    return target


@click.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.argument('target_dir', type=click.Path(exists=True))
def process(source_dir, target_dir):
    """Process the csv files."""
    for subdir, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.csv'):
                source_file = os.path.join(source_dir, file)
                target_file = os.path.join(target_dir, file)

                source = []
                with open(source_file, 'r', encoding="utf-8") as _in:
                    reader = csv.DictReader(_in)

                    raw_headers = reader.fieldnames
                    headers = get_headers(raw_headers)
                    for row in reader:
                        source.append(row)

                    with open(target_file, 'w', encoding="utf-8") as out:
                        writer = csv.DictWriter(out, fieldnames=headers)
                        writer.writeheader()

                        target = get_target(source, headers)

                        for row in target:
                            writer.writerow(row)


if __name__ == '__main__':
    sys.exit(process())
