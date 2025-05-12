"""
Example demonstrating triggering a job based on metadata events.

Demonstrates:
1. Setting up a metadata event trigger.
2. Submitting a job triggered by a repository data event.
"""

from lwfm.base.Site import Site
from lwfm.base.Metasheet import Metasheet
from lwfm.midware.Logger import logger
from lwfm.midware.LwfManager import lwfManager
from lwfm.base.WorkflowEvent import MetadataEvent
from lwfm.base.JobDefn import JobDefn
from lwfm.util.IdGenerator import IdGenerator

DATA_FILE_SRC = "example_date.out"
DATA_FILE_DEST = "/tmp/someFile-ex3.dat"


def main():
    # Site initialization and authentication
    site = Site.getSite("local")
    site.getAuthDriver().login()

    # Generate unique timestamp/sampleId for the event trigger
    sample_id = IdGenerator.generateId()

    # Define a metadata-triggered job event
    metadata_trigger = {"sampleId": sample_id}
    job_defn = JobDefn("echo 'Metadata event triggered'")

    future_job_status = lwfManager.setEvent(
        MetadataEvent(metadata_trigger, job_defn, site.getSiteName())
    )

    logger.info(f"Job {future_job_status.getJobId()} configured as metadata event trigger for {metadata_trigger}")

    # Put the file into the repository with the triggering metadata
    metasheet = Metasheet(site.getSiteName(), DATA_FILE_DEST, metadata_trigger)
    site.getRepoDriver().put(DATA_FILE_SRC, DATA_FILE_DEST, metasheet=metasheet)
    logger.info(f"File '{DATA_FILE_SRC}' stored as '{DATA_FILE_DEST}' with triggering metadata {metadata_trigger}")

    # Optional: wait for the triggered job to complete
    final_status = lwfManager.wait(future_job_status.getJobId())
    logger.info(f"Metadata-triggered job completed with status: {final_status}")


if __name__ == "__main__":
    main()
