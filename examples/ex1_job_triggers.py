"""
Demonstrate asynchronous job chaining on a local site:
A -> B -> C, where each job triggers the next upon completion.
"""

from lwfm.base.Site import Site
from lwfm.base.JobDefn import JobDefn
from lwfm.base.JobStatus import JobStatusValues
from lwfm.base.WorkflowEvent import JobEvent
from lwfm.base.Workflow import Workflow
from lwfm.midware.LwfManager import lwfManager
from lwfm.midware.Logger import logger

DATA_FILE = "example_date.out"


def main():
    # Authenticate on the local site
    site = Site.getSite("local")
    site.getAuthDriver().login()

    # Define jobs
    job_a = JobDefn('echo "Job A: Pre-processing complete. Output pwd = $(pwd)"')
    job_b = JobDefn(f'echo "Job B: Writing date" && echo "$(date)" > {DATA_FILE}')
    job_c = JobDefn(f'echo "Job C: Reading {DATA_FILE}:" && cat {DATA_FILE}')

    # Create a workflow for the chain
    wf = Workflow()
    wf.setName("A->B->C test")
    wf.setDescription("Test of chaining three jobs (A, B, C) asynchronously")
    lwfManager.putWorkflow(wf)

    # Submit job A
    status_a = site.getRunDriver().submit(job_a, wf)
    logger.info(f"Job A ({status_a.getJobId()}) submitted.")

    # Run job B when job A completes
    status_b = lwfManager.setEvent(
        JobEvent(
            ruleJobId=status_a.getJobId(),
            ruleStatus=JobStatusValues.COMPLETE.value,
            fireDefn=job_b,
            fireSite=site.getSiteName()
        )
    )
    logger.info(f"Job B ({status_b.getJobId()}) event handler set, triggered by Job A completion.")

    # Run job C when job B completes
    # Set up the event: when Job B (status_b.getJobId()) reaches COMPLETE, fire Job C
    status_c = lwfManager.setEvent(
        JobEvent(
            ruleJobId=status_b.getJobId(),
            ruleStatus=JobStatusValues.COMPLETE.value,
            fireDefn=job_c,
            fireSite=site.getSiteName()
        )
    )
    logger.info(f"Job C ({status_c.getJobId()}) event handler set, triggered by Job B completion.")

    # Wait for job C to finish, which implies A and B are also done
    logger.info(f"Waiting for the chained Job C ({status_c.getJobId()}) to complete...")
    final_status_c = lwfManager.wait(status_c.getJobId())
    logger.info(f"Job C ({final_status_c.getJobId()}) finished, implying Jobs A and B also finished.")

    # Retrieve and log the final statuses for A, B, and C
    final_status_a = lwfManager.getStatus(status_a.getJobId())
    logger.info(f"Final status for Job A ({status_a.getJobId()}): {final_status_a}")

    final_status_b = lwfManager.getStatus(status_b.getJobId())
    logger.info(f"Final status for Job B ({status_b.getJobId()}): {final_status_b}")

    fetched_final_status_c = lwfManager.getStatus(status_c.getJobId())
    logger.info(f"Final status for Job C ({status_c.getJobId()}): {fetched_final_status_c}")


if __name__ == "__main__":
    main()
