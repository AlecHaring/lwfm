"""
Demonstrate triggering a handler job upon the failure of a preceding job on a local site:
MainJob (fails) -> HandlerJob (executes due to MainJob's failure).
"""
import asyncio

from lwfm.base.Site import Site
from lwfm.base.JobDefn import JobDefn
from lwfm.base.JobStatus import JobStatusValues
from lwfm.base.WorkflowEvent import JobEvent
from lwfm.base.Workflow import Workflow
from lwfm.midware.LwfManager import lwfManager
from lwfm.midware.Logger import logger

def main():
    # Authenticate on the local site
    site = Site.getSite("local")
    site.getAuthDriver().login()

    # Define jobs
    # job_main_defn uses the 'false' command, which exits with a non-zero status, causing the job to fail.
    job_main_defn = JobDefn('echo "Job Main: I am programmed to fail." && false')
    job_handler_defn = JobDefn('echo "Job Handler: Executed because Job Main failed as expected."')

    # Create a workflow
    wf = Workflow()
    wf.setName("FailedJobTriggerWorkflow")
    wf.setDescription("Demonstrates triggering a handler job when a preceding job fails.")
    lwfManager.putWorkflow(wf)

    # Submit job_main
    status_main_submitted = site.getRunDriver().submit(job_main_defn, wf)
    logger.info(f"Job Main ({status_main_submitted.getJobId()}) submitted.")

    # Set up the event: when Job Main FAILED, fire Job Handler
    status_handler_event = lwfManager.setEvent(
        JobEvent(
            ruleJobId=status_main_submitted.getJobId(),
            ruleStatus=JobStatusValues.FAILED.value,  # Trigger on FAILED status
            fireDefn=job_handler_defn,
            fireSite=site.getSiteName()
        )
    )
    logger.info(f"Job Handler ({status_handler_event.getJobId()}) event handler set, "
                f"awaits failure of Job Main ({status_main_submitted.getJobId()}).")

    # Wait for the handler job to finish. This implies job_main has already failed.
    logger.info(f"Waiting for the triggered Job Handler ({status_handler_event.getJobId()}) to complete...")
    final_status_handler = lwfManager.wait(status_handler_event.getJobId())
    logger.info(f"Job Handler ({final_status_handler.getJobId()}) finished with status: "
                f"{final_status_handler.getStatus().value}")

    # Retrieve and log the final statuses for verification
    final_status_main = lwfManager.getStatus(status_main_submitted.getJobId())
    logger.info(f"Final status for Job Main ({status_main_submitted.getJobId()}): "
                f"{final_status_main.getStatus().value}")


    # Verify the outcome
    if final_status_main.getStatus() == JobStatusValues.FAILED and \
       final_status_handler.getStatus() == JobStatusValues.COMPLETE:
        logger.info("SUCCESS: The failed job trigger example completed as expected.")
    else:
        logger.error("ERROR: The failed job trigger example did not behave as expected.")
        logger.error(f"Main Job status: {final_status_main.getStatus().value} (Expected: FAILED)")
        logger.error(f"Handler Job status: {final_status_handler.getStatus().value} (Expected: COMPLETE)")

if __name__ == "__main__":
    main()
