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

        for line in lines[1:]:

            self.logger.info(line)

            name, description, content_type, ne_stable, parent_type, parent_descr = line.split(",")
            # test = Location.location_type.create(name=location_name)

            payload ={
                "name":  name,
                "slug": name,
                "parent": parent_type,
                "ne_stable": ne_stable,
                "content_types": content_type.split(',')
            }

            self.logger.info(payload)

            LocationType.objects.create(**payload)

            self.logger.info(LocationType.objects.get(name=name))

            # self.logger.info(f"State: {name}")
            # self.logger.info(f"City: {description}")
            # self.logger.info(f"DC type: {type}")
            # self.logger.info(f"Branch: {ne_stable}")
            # self.logger.info(f"Branch: {parent_type}")
            # self.logger.info(f"Branch: {parent_descr}")

        return "Execution completed"


register_jobs(
    ImportLocationTypes,
)
