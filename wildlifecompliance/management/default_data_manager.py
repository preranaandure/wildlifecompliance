import datetime
import json
import logging
import os

import pytz
from django.contrib.auth.models import Group
from django.contrib.gis.geos import GEOSGeometry, fromfile
from django.core.exceptions import MultipleObjectsReturned
from ledger.settings_base import TIME_ZONE

from wildlifecompliance import settings
from wildlifecompliance.components.main.models import (
        RegionGIS, DistrictGIS, Region,
        VolunteerGroup, InfringementNoticeCoordinatorGroup, ProsecutionCoordinatorGroup,
        ProsecutionManagerGroup, ProsecutionCouncilGroup, ComplianceManagementReadOnlyGroup,
        ComplianceManagementCallEmailReadOnlyGroup, ComplianceManagementApprovedExternalUserGroup,
        ComplianceAdminGroup, LicensingAdminGroup,
        )
from wildlifecompliance.components.call_email.models import Classification

logger = logging.getLogger(__name__)


class DefaultDataManager(object):

    def __init__(self):

        # RegionGIS: store geometries
        path_to_regions = os.path.join(settings.BASE_DIR, 'wildlifecompliance', 'static', 'wildlifecompliance', 'DBCA_regions.geojson')
        count = RegionGIS.objects.all().count()
        if not count > 0:
            with open(path_to_regions) as f:
                data = json.load(f)

                for region in data['features']:
                    json_str = json.dumps(region['geometry'])
                    geom = GEOSGeometry(json_str)
                    region_obj = RegionGIS.objects.create(
                        wkb_geometry=geom,
                        region_name=region['properties']['DRG_REGION_NAME'],
                        office=region['properties']['DRG_OFFICE'],
                        object_id=region['properties']['OBJECTID'],
                    )
                    region_obj.save()
                    logger.info("Created Region: {}".format(region['properties']['DRG_REGION_NAME']))

        # DistrictGIS: store geometries
        path_to_districts = os.path.join(settings.BASE_DIR, 'wildlifecompliance', 'static', 'wildlifecompliance', 'DBCA_districts.geojson')
        count = DistrictGIS.objects.all().count()
        if not count > 0:
            with open(path_to_districts) as f:
                data = json.load(f)

                for district in data['features']:
                    json_str = json.dumps(district['geometry'])
                    geom = GEOSGeometry(json_str)
                    district_obj = DistrictGIS.objects.create(
                        wkb_geometry=geom,
                        district_name=district['properties']['DDT_DISTRICT_NAME'],
                        office=district['properties']['DDT_OFFICE'],
                        object_id=district['properties']['OBJECTID'],
                    )
                    district_obj.save()
                    logger.info("Created District: {}".format(district['properties']['DDT_DISTRICT_NAME']))

        ## Head Office Region
        region, created = Region.objects.get_or_create(name=settings.HEAD_OFFICE_NAME, head_office=True)
        if created:
            logger.info("Created Head Office Region: {}".format(region.name))

        # Call Email
        # Classification
        for item in Classification.NAME_CHOICES:
            try:
                classification, created = Classification.objects.get_or_create(name=item[0])
                if created:
                    #classification.description = item[1]
                    #classification.save()
                    logger.info("Created Call/Email Classification: {}".format(item[1]))
            except Exception as e:
                logger.error('{}, Call/Email Classification: {}'.format(e, item[1]))

        # Set up CM security Groups without Region/District
        if not VolunteerGroup.objects.exists():
            VolunteerGroup.objects.create()
            logger.info("Created Volunteer Group")
        if not InfringementNoticeCoordinatorGroup.objects.exists():
            InfringementNoticeCoordinatorGroup.objects.create()
            logger.info("Created Infringement Notice Coordinator Group")
        if not ProsecutionCoordinatorGroup.objects.exists():
            ProsecutionCoordinatorGroup.objects.create()
            logger.info("Created Prosecution Coordinator Group")
        if not ProsecutionManagerGroup.objects.exists():
            ProsecutionManagerGroup.objects.create()
            logger.info("Created Prosecution Manager Group")
        if not ProsecutionCouncilGroup.objects.exists():
            ProsecutionCouncilGroup.objects.create()
            logger.info("Created Prosecution Council Group")
        if not ComplianceManagementReadOnlyGroup.objects.exists():
            ComplianceManagementReadOnlyGroup.objects.create()
            logger.info("Created Compliance Management Read Only Group")
        if not ComplianceManagementCallEmailReadOnlyGroup.objects.exists():
            ComplianceManagementCallEmailReadOnlyGroup.objects.create()
            logger.info("Created Compliance Management Call Email Read Only Group")
        if not ComplianceManagementApprovedExternalUserGroup.objects.exists():
            ComplianceManagementApprovedExternalUserGroup.objects.create()
            logger.info("Created Compliance Management Approved External User Group")
        if not ComplianceAdminGroup.objects.exists():
            ComplianceAdminGroup.objects.create()
            logger.info("Created Compliance Admin Group")
        if not LicensingAdminGroup.objects.exists():
            LicensingAdminGroup.objects.create()
            logger.info("Created Licensing Admin Group")

