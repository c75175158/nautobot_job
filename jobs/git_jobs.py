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

        # --- 1. Pre-fetch common objects outside the loop for efficiency ---
        try:
            STATUS_ACTIVE = Status.objects.get(name="Active")
            TYPE_DC = LocationType.objects.get(name="Data Center")
            TYPE_BR = LocationType.objects.get(name="Branch")
            TYPE_STATE = LocationType.objects.get(name="State")
            TYPE_CITY = LocationType.objects.get(name="City")
        except (Status.DoesNotExist, LocationType.DoesNotExist) as e:
            self.logger.error(f"Missing required LocationType or Status: {e}")
            return  # Exit job if required objects aren't configured

        states_map = {'CA': 'California', 'VA': 'Virginia', "NJ": "New Jersey", "IL": "Illinois"}

        for line in lines[1:]:
            location_data = line.strip().split(",")  # Use .strip() to remove newlines

            # Extract data from the row
            site_name = location_data[0]
            city_name = location_data[1]
            state_abbreviation = location_data[2]

            state_full_name = states_map.get(state_abbreviation, state_abbreviation)

            # Determine the type of the site itself (DC or Branch) based on its suffix
            site_type_suffix = site_name.split("-")[-1]
            site_location_type = TYPE_DC if site_type_suffix == 'DC' else TYPE_BR

            # --- 2. Resolve the Top-Level Site Location (e.g., "Den-DC") ---
            # Use get_or_create to prevent "unique constraint" errors if run multiple times
            site_obj, created = Location.objects.get_or_create(
                name=site_name,
                # A top-level site has no parent, so we only need name and type for uniqueness
                defaults={
                    'status': STATUS_ACTIVE,
                    'location_type': site_location_type,
                }
            )
            self.logger.info(
                f"Site Location Resolved ({'Created' if created else 'Existing'}): {site_obj.name} (UUID: {site_obj.id})")

            # --- 3. Resolve the State Location (Parent is now the site_obj) ---
            # This combination of (name=state_full_name, parent=site_obj) must be unique
            state_obj, created = Location.objects.get_or_create(
                name=state_full_name,
                parent=site_obj,  # Link to the unique site object UUID
                defaults={
                    'status': STATUS_ACTIVE,
                    'location_type': TYPE_STATE,
                }
            )
            self.logger.info(
                f"State Location Resolved ({'Created' if created else 'Existing'}): {state_obj.name} (Parent: {site_obj.name})")

            # --- 4. Resolve the City Location (Parent is now the state_obj) ---
            # This combination of (name=city_name, parent=state_obj) must be unique
            city_obj, created = Location.objects.get_or_create(
                name=city_name,
                parent=state_obj,  # Link to the unique state object UUID
                defaults={
                    'status': STATUS_ACTIVE,
                    'location_type': TYPE_CITY,
                }
            )
            self.logger.info(
                f"City Location Resolved ({'Created' if created else 'Existing'}): {city_obj.name} (Parent: {state_obj.name})")


register_jobs(
    ImportLocationTypes,
    ImportLocation,
)
