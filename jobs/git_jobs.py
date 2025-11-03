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
                payload = {}
                pattern = r'"(.*?)"'
                contents = line.split(",")
                parent_type = contents[4]
                ne_stable = contents[3]
                content_type = re.findall(pattern, line)

                child_object = LocationType.objects.get_or_create(name=contents[0])
                parent_obj = LocationType.objects.get_or_create(name=parent_type)

                self.logger.info(child_object)
                self.logger.info(content_type)
                self.logger.info(contents[0])

                if content_type:
                    payload["content_types"] = content_type[0].split(",")

                self.logger.info(parent_obj[1])
                self.logger.info(payload)

                if not parent_obj[1] and parent_type != 'NoObject':

                    payload = {
                        "name": contents[0],
                        "parent": parent_type,
                        "nestable": convert[ne_stable],
                    }

                    LocationType.objects.update(**payload)

                if  parent_type == 'NoObject':

                    payload = {
                        "name": contents[0],
                        "nestable": convert[ne_stable],
                    }

                    if content_type:
                        payload["content_types"] = content_type[0].split(",")

                    LocationType.objects.create(**payload)

            except Exception as e:
                self.logger.info(f'Failed to parse line "{e}"', exc_info=True)
                continue

register_jobs(
    ImportLocationTypes,
)
