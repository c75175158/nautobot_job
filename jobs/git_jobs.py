from nautobot.apps.jobs import Job, register_jobs

# new
name = "Hello World Nautobot Jobs"


class HelloJobs(Job):
    # new
    class Meta:
        name = "Hello Jobs"
        description = "Hello World for first Nautobot Jobs"

    def run(self):
        self.logger.debug("Hello, this is my first Nautobot Job.")



register_jobs(
    HelloJobs,
)