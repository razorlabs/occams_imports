"""Removes iform version numbers from form name and removes forms in spanish.

Note: This is a PYTHON 3 script.

After an iform script has been converted to OCCAMS format, the iform version
numbers are in the schema name and need to be removed, else they won't be
merged in the merge_ecrf_versions.py script.  Also, there is no need for
schemas in Spanish for OCCAMS imports, so they will be removed as well.

This script processes one form at a time.

Sample usage:

python remove_versions_and_sp.py source_file target_file
"""
import sys
import csv
import click
import re


def converted_schema_name(schema_name):
    """Parse the version number out of the schema name.

    Currently the version number is in the string, i.e.
    schema_name_v02

    :schema_name: name of the schema
    :return: the schema name without the version number
    """
    match = re.search('^.*(?=_v\d+)', schema_name)

    return match.group(0)


def is_spanish_schema(schema_name):
    """Identify if the schema is in spanish.

    If a schema is in spanish the name is as follows:

    schema_name_sp_v02

    :schema_name: name of the schema
    :return: the schema name without the version number
    """
    match = re.search('^.*(?=_sp_v\d+)', schema_name)

    return bool(match)


@click.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('target_file', type=click.Path())
def process(source_file, target_file):
    """Process the csv files."""
    with open(source_file, 'r', encoding="utf-8") as _in:
        reader = csv.reader(_in)

        headers = next(reader)
        with open(target_file, 'w', encoding="utf-8") as out:
            writer = csv.writer(out)

            writer.writerow(headers)

            for row in reader:
                schema_name = row[1]
                is_spanish = is_spanish_schema(schema_name)
                if is_spanish:
                    continue
                schema_name = converted_schema_name(schema_name)
                row[1] = schema_name
                writer.writerow(row)


if __name__ == '__main__':
    sys.exit(process())
