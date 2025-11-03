import logging
import re
from django.contrib.contenttypes.models import ContentType
from nautobot.apps.jobs import Job, register_jobs, FileVar
from nautobot.dcim.models import Device, Location, DeviceType, LocationType, Rack
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import Prefix



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

            self.logger.info(line)
            content_type = re.findall(r'"(.*?)"', line)

            if content_type:
                content_type = content_type[0]
                contents = line.replace(f"{re.findall(r'\"(.*)\"', line)[0]}", "").replace(",\"\"", "").split(",")
                parent_type = contents[3]
                ne_stable = convert[contents[2]]
            else:
                contents = line.split(",")
                parent_type = contents[4]
                ne_stable = convert[contents[3]]

            # child_object = LocationType.objects.get_or_create(name=contents[0])

            self.logger.info(content_type)
            self.logger.info(parent_type)
            # self.logger.info(parent_obj[1])

            if parent_type != 'NoObject':

                try:
                    LocationType.objects.get_or_create(name=parent_type, nestable=ne_stable)
                except Exception as e:
                    pass

                self.logger.info('No Parent Type')

                payload = {
                    "name": contents[0],
                    "parent": LocationType.objects.get(name=parent_type),
                    "nestable": ne_stable,
                    "description": contents[1],
                }

                location_type = LocationType.objects.create(**payload)

                if content_type != 'NoObject':
                    if len(content_type) > 0:
                        classes = [ContentType.objects.get(app_label=i.split(".")[0], model=i.split(".")[1])
                                   for i in
                                   content_type.split(",")]
                        location_type.content_types.set(classes)

            else:

                self.logger.info('No Parent Type')

                self.logger.info('NoObject')

                if not parent_type[1] and parent_type != 'NoObject':

                    payload = {
                        "name": contents[0],
                        "nestable": ne_stable,
                        "description": contents[1],
                    }

                    location_type = LocationType.objects.create(**payload)

                    if content_type != 'NoObject':
                        if len(content_type) > 0:
                            classes = [ContentType.objects.get(app_label=i.split(".")[0], model=i.split(".")[1]) for i in
                                       content_type.split(",")]
                            location_type.content_types.set(classes)



register_jobs(
    ImportLocationTypes,
)
