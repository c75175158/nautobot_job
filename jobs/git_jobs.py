import logging
import re
from django.contrib.contenttypes.models import ContentType
from nautobot.apps.jobs import Job, register_jobs, FileVar
from nautobot.dcim.models import Device, DeviceType, LocationType, Rack, Location
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
        lines = file_contents.splitlines()

        convert = {'TRUE': True, 'FALSE': False, 'true': True, 'false': False}

        for line in lines[1:]:

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

            if parent_type != 'NoObject':

                try:
                    LocationType.objects.get_or_create(name=parent_type, nestable=ne_stable)[0]
                except Exception as e:
                    pass

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

                payload = {
                    "name": contents[0],
                    "nestable": ne_stable,
                    "description": contents[1],
                }

                location_type = LocationType.objects.get_or_create(**payload)

                if content_type != 'NoObject':
                    if len(content_type) > 0:
                        classes = [ContentType.objects.get(app_label=i.split(".")[0], model=i.split(".")[1]) for i in
                                   content_type.split(",")]
                        location_type.content_types.set(classes)




class ImportLocation(Job):
    class Meta:
        name = "CSV File Upload and Process"
        description = "Please select a CSV file for upload"

    file = FileVar(
        description="CSV File to upload",
    )

    def run(self, file):

        file_contents = file.read().decode("utf-8")
        lines = file_contents.splitlines()

        for line in lines[1:]:

            location = line.split(",")
            self.logger.info(location)
            location_type = location[0].split("-")[-1]
            states = {'CA': 'California', 'VA': 'Virginia'}
            status = Status.objects.get(name="Active")
            parent = Location.objects.get_or_create(
                name=location[0],
                status=status ,
                location_type= LocationType.objects.get(name="Data Center") if location_type == 'BR' else LocationType.objects.get(name="Branch"),
            )

            oldest = Location.objects.get_or_create(
                name=location[2],
                parent=parent,
                status=status,
                location_type = LocationType.objects.get(
                name="Data Center") if location_type == 'BR' else LocationType.objects.get(name="Branch"),

            )

            Location.objects.get_or_create(
                name=location[1] if not states.get(location[1]) else states.get(location[1]) ,
                parent=oldest,
                status=status,
                location_type=LocationType.objects.get(
                    name="Data Center") if location_type == 'BR' else LocationType.objects.get(name="Branch"),

            )

register_jobs(
    ImportLocationTypes,
    ImportLocation,
)
