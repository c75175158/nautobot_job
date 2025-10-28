from nautobot.apps.jobs import Job, register_jobs


class MyFirstJob(Job):
    name = "My First Nautobot Job"
    description = "A simple example job."

    def run(self):
        self.log_info(message="Hello from My First Nautobot Job!")
        return "Job completed successfully."

register_jobs(
    MyFirstJob,
)
