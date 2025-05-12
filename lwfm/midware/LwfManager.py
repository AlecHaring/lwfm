"""
LwfManager - exposes the services of the lwfm middleware to workflows and Site 
implementations.  Permits emitting and fetching job status, setting workflow
event handlers, and notating provenancial metadata.
"""

#pylint: disable = invalid-name, missing-class-docstring, missing-function-docstring
#pylint: disable = broad-exception-caught

import time
import os
from typing import List, Optional

from lwfm.base.WorkflowEvent import WorkflowEvent
from lwfm.base.JobContext import JobContext
from lwfm.base.JobStatus import JobStatus
from lwfm.util.IdGenerator import IdGenerator
from lwfm.base.Metasheet import Metasheet
from lwfm.base.Workflow import Workflow
from lwfm.midware.impl.LwfmEventClient import LwfmEventClient

# ***************************************************************************
class LwfManager:
    """
    The LwfManager provides a high-level interface to the Lightweight Workflow Manager (lwfm)
    middleware services. It allows workflow definitions and site implementations to interact
    with the lwfm system for tasks such as:

    - Managing workflow lifecycle (creation, retrieval).
    - Emitting and retrieving job status information.
    - Setting up and managing event handlers that trigger actions based on job status
      changes or metadata events.
    - Recording and querying provenance metadata (Metasheets) associated with jobs and data.
    - Generating unique identifiers.
    """


    _client: LwfmEventClient = LwfmEventClient()

    def generateId(self) -> str:
        """
        Generates a unique identifier string.
        """
        return IdGenerator.generateId()


    #***********************************************************************
    # workflow methods

    def putWorkflow(self, workflow: Workflow) -> str:
        """
        Stores a workflow definition in the lwfm middleware.

        Args:
            workflow (Workflow): The workflow object to store.

        Returns:
            str: The ID of the stored workflow. Returns None if the operation fails.
        """
        return self._client.putWorkflow(workflow)

    def getWorkflow(self, workflow_id: str) -> Workflow:
        """
        Retrieves a workflow definition from the lwfm middleware by its ID.

        Args:
            workflow_id (str): The ID of the workflow to retrieve.

        Returns:
            Workflow: The retrieved workflow object, or None if not found or an error occurs.
        """
        return self._client.getWorkflow(workflow_id)


    #***********************************************************************
    # status methods

    def getStatus(self, jobId: str) -> Optional[JobStatus]:
        """
        Retrieves the most recent JobStatus for a given job ID.

        Args:
            jobId (str): The ID of the job for which to get the status.

        Returns:
            Optional[JobStatus]: The current JobStatus object, or None if not found
                                 or an error occurs.
        """
        return self._client.getStatus(jobId)

    def getAllStatus(self, jobId: str) -> Optional[List[JobStatus]]:
        """
        Retrieves all recorded JobStatus objects for a given job ID, in reverse
        chronological order (most recent first).

        Args:
            jobId (str): The ID of the job for which to get all statuses.

        Returns:
            A list of JobStatus objects, or None if not found
                 or an error occurs.
        """
        return self._client.getAllStatus(jobId)

    def getJobContextFromEnv(self) -> JobContext:
        """
        Attempts to retrieve a JobContext based on a job ID found in the
        `_LWFM_JOB_ID` environment variable.

        If the environment variable is set, this method fetches the status for that
        job ID and returns its associated JobContext. If the status cannot be
        retrieved, it constructs a new JobContext with the job ID from the environment.

        Returns:
            Optional[JobContext]: The JobContext if the environment variable is set,
                                  otherwise None.
        """
        if '_LWFM_JOB_ID' in os.environ:
            status = self.getStatus(os.environ['_LWFM_JOB_ID'])
            if status is not None:
                return status.getJobContext()
            else:
                context = JobContext()
                context.setJobId(os.environ['_LWFM_JOB_ID'])
                return context
        return None

    # emit a status message
    def emitStatus(self, context: JobContext, statusClass: type,
                   nativeStatus: str, nativeInfo: str = None) -> None:
        """
        Emits a job status update to the lwfm middleware.

        This method constructs a JobStatus object using the provided information and
        sends it to the middleware. The `statusClass` is used to instantiate the
        status object, allowing for site-specific status mapping.

        Args:
            context (JobContext): The context of the job for which the status is being emitted.
            statusClass (type): The class (typically a subclass of JobStatus) to use for
                                creating the status object. This allows for site-specific
                                mapping of native status codes.
            nativeStatus (str): The native status string from the site where the job is running.
            nativeInfo (str, optional): Additional native information or a message associated
                                        with the status. Defaults to None.
        """
        return self._client.emitStatus(context, statusClass, nativeStatus, nativeInfo)

    def wait(self, jobId: str) -> Optional[JobStatus]:  # return JobStatus when the job is done
        """
        Waits synchronously until the specified job reaches a terminal state
        (e.g., COMPLETE, FAILED, CANCELLED).

        This method polls the job's status using a progressively increasing sleep
        interval to avoid overwhelming the middleware.

        Args:
            jobId (str): The ID of the job to wait for.

        Returns:
            Optional[JobStatus]: The terminal JobStatus object once the job is done,
                                 or None if an error occurs during waiting or if the
                                 initial status cannot be retrieved.
        """

        try:
            increment = 3
            w_sum = 1
            w_max = 60
            maxMax = 6000
            status = self.getStatus(jobId)
            if status is not None and status.isTerminal():
                # we're done waiting
                return status
            doneWaiting = False
            while True:
                time.sleep(w_sum)
                # progressive: keep increasing the sleep time until we hit max,
                # then keep sleeping max
                if w_sum < w_max:
                    w_sum += increment
                elif w_sum < maxMax:
                    w_sum += w_max
                status = self.getStatus(jobId)
                if status is not None and status.isTerminal():
                    return status
        except Exception as ex:
            print("Error waiting for job: " + str(ex))
            return None


    #***********************************************************************
    # event methods

    # register an event handler, get back the initial queued status of the future job
    def setEvent(self, wfe: WorkflowEvent) -> JobStatus:
        """
        Registers a workflow event handler with the lwfm middleware.

        When the conditions of the WorkflowEvent are met (e.g., a specific job
        reaches a certain status), the middleware will trigger the associated action
        (often firing a new job).

        Args:
            wfe (WorkflowEvent): The workflow event to register. This object defines
                                 the trigger conditions and the action to take.

        Returns:
            Optional[JobStatus]: The initial JobStatus of the job that will be created
                                 by this event handler (often in a PENDING or READY state),
                                 or None if registration fails.
        """
        return self._client.setEvent(wfe)

    def unsetEvent(self, wfe: WorkflowEvent) -> None:
        """
        Unregisters a previously set workflow event handler from the lwfm middleware.

        Args:
            wfe (WorkflowEvent): The workflow event to unregister. The event's ID
                                 is typically used to identify it.
        """
        return self._client.unsetEvent(wfe)

    # get all active event handlers
    def getActiveWfEvents(self) -> List[WorkflowEvent]:
        """
         Retrieves a list of all currently active workflow event handlers
         registered with the lwfm middleware.

         Returns:
             Optional[List[WorkflowEvent]]: A list of active WorkflowEvent objects,
                                           or None if an error occurs.
         """
        return self._client.getActiveWfEvents()


    #***********************************************************************
    # repo methods

    def _emitRepoInfo(self, context: JobContext, metasheet: Metasheet) -> None:
        return self.emitStatus(context, JobStatus, "INFO", metasheet)

    def _notate(self, localPath: str, siteObjPath: str,
                jobContext: JobContext,
                metasheet: Metasheet,
                isPut: bool = False) -> Metasheet:
        if jobContext is not None:
            metasheet.setJobId(jobContext.getJobId())
        # now do the metadata notate
        props = metasheet.getProps()
        props['_direction'] = 'put' if isPut else 'get'
        props['localPath'] = localPath
        props['siteObjPath'] = siteObjPath
        metasheet.setProps(props)
        # persist
        sheet = LwfmEventClient().notate(metasheet.getSheetId(), metasheet)
        # now emit an INFO job status
        self._emitRepoInfo(jobContext, metasheet)
        return sheet

    def notatePut(self, localPath: str, siteObjPath: str,
        jobContext: JobContext,
        metasheet: Metasheet = None) -> Metasheet:
        return self._notate(localPath, siteObjPath, jobContext, metasheet, True)

    def notateGet(self, localPath: str, siteObjPath: str,
        jobContext: JobContext,
        metasheet: Metasheet = None) -> Metasheet:
        return self._notate(localPath, siteObjPath, jobContext, metasheet, False)

    def find(self, queryRegExs: dict) -> Optional[List[Metasheet]]:
        """
        Finds and retrieves Metasheets from the lwfm store that match a given
        set of query regular expressions.

        The query is a dictionary where keys are metadata field names and values
        are regular expressions to match against the field values.

        Args:
            queryRegExs (dict): A dictionary of {field_name: regex_pattern} to
                                search for.

        Returns:
            Optional[List[Metasheet]]: A list of Metasheet objects that match the query,
                                       or None if no matches are found or an error occurs.
        """
        return self._client.find(queryRegExs)


#***********************************************************************

lwfManager = LwfManager()
