"""Test cctg to drsc file converter."""

from cctg_to_drsc import get_headers
from cctg_to_drsc import get_target


def test_headers():
    """Test header function."""
    expected = [
        'pid',
        'visit',
        'form_name',
        'collect_date',
        'not_done',
        'rapiddate',
        'rapidtype',
        'typeother',
        'rapidres',
    ]

    headers = [
        'id',
        'pid',
        'site',
        'enrollment',
        'enrollment_ids',
        'visit_cycles',
        'visit_id',
        'visit_date',
        'form_name',
        'form_publish_date',
        'state',
        'collect_date',
        'not_done',
        'rapiddate',
        'rapidtype',
        'typeother',
        'rapidres',
        'create_date',
        'create_user',
        'modify_date',
        'modify_user'
    ]

    actual = get_headers(headers)

    assert actual == expected


def test_get_target():
    """Test convert source to target."""
    headers = [
        'pid',
        'visit',
        'form_name',
        'collect_date',
        'not_done',
        'rapiddate',
        'rapidtype',
        'typeother',
        'rapidres',
    ]

    source = [
        {
            'pid': '223-ghj',
            'visit_cycles': 'week4',
            'enrollment': '',
            'enrollment_ids': '',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
        {
            'pid': '223-ghk',
            'visit_cycles': 'week8',
            'enrollment': '',
            'enrollment_ids': '',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
        {
            'pid': '223-ghj',
            'visit_cycles': '593(-1);596 Network(0)',
            'enrollment': '',
            'enrollment_ids': '',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
        {
            'pid': '223-ghl',
            'visit_cycles': 'week12',
            'enrollment': '',
            'enrollment_ids': '',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
    ]

    expected = [
        {
            'pid': '223-ghj',
            'visit': 'week4',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
        {
            'pid': '223-ghk',
            'visit': 'week8',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
        {
            'pid': '223-ghj',
            'visit': '593(-1)',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
        {
            'pid': '223-ghj',
            'visit': '596 Network(0)',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        },
        {
            'pid': '223-ghl',
            'visit': 'week12',
            'form_name': 'demographics',
            'collect_date': '2015-09-06',
            'not_done': 0,
            'rapiddate': '2016-01-01',
            'rapidtype': 6,
            'typeother': 3,
            'rapidres': 2,
        }
    ]

    actual = get_target(source, headers)

    assert actual == expected
