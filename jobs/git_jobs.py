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

                name, description, content_type, ne_stable, parent_type, parent_descr = line.split(",")
                # test = Location.location_type.create(name=location_name)
                payload =  {
                    "name":  name,
                    "parent": parent_type if parent_type != 'NoObject' else None,
                    "nestable": convert[ne_stable],
                }

                self.logger.info(payload)

                LocationType.objects.create(**payload)

            except Exception as e:
                pass

            # self.logger.info(f"State: {name}")
            # self.logger.info(f"City: {description}")
            # self.logger.info(f"DC type: {type}")
            # self.logger.info(f"Branch: {ne_stable}")
            # self.logger.info(f"Branch: {parent_type}")
            # self.logger.info(f"Branch: {parent_descr}")


register_jobs(
    ImportLocationTypes,
)
