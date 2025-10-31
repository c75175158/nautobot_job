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
                parent_obj = LocationType.objects.get_or_create(name=parent_type)
                self.logger.info(parent_obj)
                payload =  {
                     "name":  contents[0],
                     "parent": parent_obj if parent_type  else None,
                     "nestable": convert[ne_stable],
                }

                self.logger.info(payload)
                LocationType.objects.create(**payload)

            except Exception as e:
                self.logger.info(e)
                continue

            # self.logger.info(f"State: {name}")
            # self.logger.info(f"City: {description}")
            # self.logger.info(f"DC type: {type}")
            # self.logger.info(f"Branch: {ne_stable}")
            # self.logger.info(f"Branch: {parent_type}")
            # self.logger.info(f"Branch: {parent_descr}")


register_jobs(
    ImportLocationTypes,
)
