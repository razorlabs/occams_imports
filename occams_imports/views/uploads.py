"""
Views to support data file uploads after study lock.
"""

import unicodecsv as csv
from pyramid.view import view_config
from pyramid.session import check_csrf_token
from pyramid.renderers import render_to_response
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql import exists

from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_imports import models as models


@view_config(
    route_name='imports.upload',
    permission='import',
    renderer='../templates/uploads/upload.pt')
def index(context, request):
    """Serve the index page for file uploads."""
    return {}


@view_config(
    route_name='imports.upload_status',
    permission='import',
    renderer='../templates/uploads/status.pt')
def status(context, request):
    """Process file upload."""
    check_csrf_token(request)
    db_session = request.db_session

    site = request.POST['site'].lower()
    patient_site = studies.Site(name=site.lower(), title=site.upper())
    filename = request.POST['data-file'].filename

    upload_file = request.POST['data-file'].file

    reader = csv.DictReader(upload_file, encoding='utf-8', delimiter=',')

    for row in reader:
        schema_name = row['form_name']
        schema_publish_date = row['form_publish_date']

        schema = (
            db_session.query(datastore.Schema)
            .filter_by(name=schema_name)
            .filter_by(publish_date=schema_publish_date)
        ).one()

        study = (
            db_session.query(studies.Study)
            .filter_by(name=site.lower())
        ).one()

        patient_pid = row['pid']
        patient_exists = (
            db_session.query(
                exists()
                .where(studies.Patient.pid == patient_pid)).scalar()
        )

        if not patient_exists:
            patient = studies.Patient(
                pid=patient_pid,
                site=patient_site
            )
            db_session.add(patient)
            db_session.flush()

        data_row = models.SiteData(
            schema=schema,
            study=study,
            data=row
        )

        db_session.add(data_row)

    return {'site': site, 'filename': filename}
