import logging
import re

from nautobot.apps.jobs import Job, register_jobs, FileVar
from nautobot.dcim.models import Device, Location, DeviceType, LocationType
from nautobot.extras.models import Role, Status


class ImportLocationTypes(Job):
    class Meta:
        name = "CSV File Upload and Process"
        description = "Please select a CSV file for upload"

    file = FileVar(
        description="CSV File to upload",
    )

    def run(self, file):

        file_contents = file.read().decode("utf-8")
        self.logger.info(file_contents)
        lines = file_contents.splitlines()
        self.logger.info(lines)

        self.logger.info("Parsing of the lines")

        convert = {'TRUE': True, 'FALSE': False, 'true': True, 'false': False}

        for line in lines[1:]:

            try:

                self.logger.info(line)
                pattern = r'"(.*?)"'
                contents = line.split(",")
                parent_type = contents[4]
                ne_stable = contents[3]
                content_type = re.findall(pattern, line)

                building_type, created = LocationType.objects.get_or_create(
                    name=contents[0],
                    description="A physical building location"
                )

                self.logger.info(building_type)
                self.logger.info(content_type)
                self.logger.info(contents[0])

                payload =  {
                     "name":  contents[0],
                     "parent": parent_type,
                     "nestable": convert[ne_stable],
                }

                if content_type:
                    payload["content_types"] = content_type[0].split(",")

                self.logger.info(payload)

                if not parent_obj:
                    LocationType.objects.create(**payload)

            except Exception as e:
                self.logger.info(f'Failed to parse line "{e}"', exc_info=True)
                continue

register_jobs(
    ImportLocationTypes,
)
