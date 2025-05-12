"""
Example: submit a simple "echo 'hello world'" job to the local site.
"""

from lwfm.base.JobDefn import JobDefn
from lwfm.base.Site import Site
from lwfm.midware.Logger import logger
from lwfm.midware.LwfManager import lwfManager


def main() -> None:
    """Submit a trivial job to the local site and wait for completion.

    Steps performed:
    1. Acquire the `Site` driver.
    2. Perform authentication.
    3. Create a `JobDefn` for the command to execute.
    4. Submit the job and block until it reaches a terminal state.
    5. Retrieve the final, persisted status and log it.
    """

    # Site initialization and authentication
    site = Site.getSite("local")
    site.getAuthDriver().login()

    # Define the job with the hello world command
    job_defn = JobDefn("echo 'hello world'")

    # Submit asynchronously
    status = site.getRunDriver().submit(job_defn)

    # Block until the job reaches a terminal state (COMPLETE, FAILED, etc.).
    status = lwfManager.wait(status.getJobId())

    # The status is persisted
    # This simulates fetching it again later
    status = lwfManager.getStatus(status.getJobId())

    logger.info(f"Job completed with status: {str(status)}")


if __name__ == "__main__":
    main()
