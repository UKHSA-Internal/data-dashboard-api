import logging

logger = logging.getLogger(__name__)


def update_api_geography(*, apps: StateApps, geographies):
    APITimeSeries = apps.get_model("data", "APITimeSeries")

    for geography in geographies:
        new = geography["new"]
        old = geography["old"]
        targets = APITimeSeries.objects.filter(
            geography=old["name"],
            geography_code=old["code"],
        )
        targets.update(
            geography=new["name"],
            geography_code=new["code"],
        )
        logger.info(
            "Migrated %s geography change on %s `APITimeSeries` records of %s total",
            geography,
            targets.count(),
            APITimeSeries.objects.count(),
        )


def revert_api_geography(*, apps: StateApps, geographies):
    APITimeSeries = apps.get_model("data", "APITimeSeries")

    for geography in geographies:
        new = geography["new"]
        old = geography["old"]
        targets = APITimeSeries.objects.filter(
            geography=new["name"],
            geography_code=new["code"],
        )
        targets.update(
            geography=old["name"],
            geography_code=old["code"],
        )
        logger.info(
            "Reverted %s geography change on %s `APITimeSeries` records of %s total",
            geography,
            targets.count(),
            APITimeSeries.objects.count(),
        )


def update_core_geography(*, apps: StateApps, geographies):
    Geography = apps.get_model("data", "Geography")

    for geography in geographies:
        new = geography["new"]
        old = geography["old"]

        try:
            target = Geography.objects.get(name=old["name"], geography_code=old["code"])
        except Geography.DoesNotExist:
            logger.exception(
                "`Geography` %s not found can't update the associated `geography_code`",
                old,
            )
        else:
            target.geography_code = new["code"]
            target.geography_name = new["name"]
            target.save()


def revert_core_geography(*, apps: StateApps, geographies):
    Geography = apps.get_model("data", "Geography")

    for geography in geographies:
        new = geography["new"]
        old = geography["old"]

        try:
            target = Geography.objects.get(name=new["name"], geography_code=new["code"])
        except Geography.DoesNotExist:
            logger.exception(
                "`Geography` %s not found, can't revert the associated `geography_code`",
                geography,
            )
        else:
            target.geography_code = old["code"]
            target.geography_name = old["name"]
            target.save()
