"""
Different kids of workflow events 
- job reaches a status, i.e. any job on any site reaching a canonical status
- a remote job reaches a status, i.e. the middleware polls for it's completion
- a data triggered event - data with a certain metadata profile is touched
in these cases, a user-provided handler is fired
"""

#pylint: disable = invalid-name, missing-class-docstring, missing-function-docstring

from enum import Enum
from typing import Optional

from lwfm.util.IdGenerator import IdGenerator
from lwfm.base.JobDefn import JobDefn


# ************************************************************************
class WorkflowEvent:
    """
    Base class for workflow events within the lwfm system.

    A WorkflowEvent represents a condition or occurrence within a workflow
    that can trigger a subsequent action, such as launching a new job.
    This class provides common attributes and methods for all event types.
    """

    def __init__(self, fireDefn=None, fireSite=None, fireJobId=None):
        self._event_id = IdGenerator.generateId()
        self._fire_defn = fireDefn
        self._fire_site = fireSite
        self._fire_job_id = fireJobId

    def getEventId(self) -> str:
        """
        Gets the unique identifier of the event.

        Returns:
            str: The event ID.
        """
        return self._event_id

    def setFireDefn(self, fireDefn: JobDefn):
        """
        Sets the JobDefn to be executed when the event triggers.

        Args:
            fireDefn (JobDefn): The job definition.
        """
        self._fire_defn = fireDefn

    def getFireDefn(self) -> JobDefn:
        """
        Gets the JobDefn that will be executed when the event triggers.

        Returns:
            JobDefn: The job definition.
        """
        return self._fire_defn

    def setFireSite(self, fireSite: str):
        """
        Sets the site where the triggered job will be executed.

        Args:
            fireSite (str): The name of the target site.
        """
        self._fire_site = fireSite

    def getFireSite(self) -> str:
        """
        Gets the site where the triggered job will be executed.

        Returns:
            str: The name of the target site.
        """
        return self._fire_site

    def setFireJobId(self, fireJobId: str):
        """
        Sets the job ID for the job that will be fired by this event.

        Args:
            fireJobId (str): The job ID.
        """
        self._fire_job_id = fireJobId

    def getFireJobId(self) -> str:
        """
        Gets the job ID for the job that will be fired by this event.

        Returns:
            str: The job ID.
        """
        return self._fire_job_id

    def __str__(self) -> str:
        return f"[event defn:{str(self.getFireDefn())} site:{str(self.getFireSite())} jobId:{str(self.getFireJobId())}]"

    def getKey(self):
        return self.getEventId()

# ***************************************************************************

class RemoteJobEvent(WorkflowEvent):
    def __init__(self, context):
        super().__init__(JobDefn(), context.getSiteName(), context.getJobId())
        self._native_job_id = context.getNativeId()

    def getNativeJobId(self):
        return self._native_job_id

    def __str__(self):
        return super().__str__() + f"+[remote nativeId:{self.getNativeJobId()}]"

# ***************************************************************************

class JobEvent(WorkflowEvent):
    """
    Represents an event triggered when a specific job reaches a particular canonical status.

    Jobs emit status updates, including informational ones. Some statuses are terminal
    (e.g., "COMPLETE", "FAILED"), while others represent interim states. lwfm normalizes
    status strings from native site-specific names to a canonical set. This event type
    allows users to define triggers based on these canonical statuses:
    "When job <ruleJobId> reaches <ruleStatus>, execute job <fireDefn> on Site <fireSite>".
    """
    def __init__(self, ruleJobId: str = None, ruleStatus: str = None, fireDefn: JobDefn = None, fireSite: str = None,
        fireJobId: Optional[str] = None):
        """
        Initializes a new JobEvent.

        Args:
            ruleJobId (str, optional): The ID of the job to monitor for status changes.
                                       Defaults to None.
            ruleStatus (str, optional): The canonical status (e.g., "COMPLETE", "FAILED")
                                        that triggers the event. Defaults to None.
            fireDefn (JobDefn, optional): The JobDefn to execute when the event triggers.
                                          Defaults to None.
            fireSite (str, optional): The site on which to fire the job. Defaults to None.
            fireJobId (Optional[str], optional): The job ID to be assigned to the fired job.
                                                 Defaults to None.
        """
        super().__init__(fireDefn, fireSite, fireJobId)
        self._rule_job_id = ruleJobId
        self._rule_status = ruleStatus

    def setRuleJobId(self, ruleJobId: str):
        """
        Sets the ID of the job whose status change triggers this event.

        Args:
            ruleJobId (str): The job ID to monitor.
        """
        self._rule_job_id = ruleJobId

    def getRuleJobId(self) -> str:
        """
        Gets the ID of the job whose status change triggers this event.

        Returns:
            str: The monitored job ID.
        """
        return self._rule_job_id

    def setRuleStatus(self, ruleStatus: str):
        """
        Sets the canonical job status that triggers this event.

        Args:
            ruleStatus (str): The triggering canonical status (e.g., from JobStatusValues).
        """
        self._rule_status = ruleStatus

    def getRuleStatus(self) -> str:
        """
        Gets the canonical job status that triggers this event.

        Returns:
            str: The triggering canonical status.
        """
        return self._rule_status

    def __str__(self):
        return super().__str__() + f"+[rule jobId:{self.getRuleJobId()} status:{self.getRuleStatus()}]"

    def getKey(self) -> str:
        return str("" + self.getRuleJobId() + "." + str(self.getRuleStatus()))

    @staticmethod
    def getJobEventKey(jobId: str, status: Enum) -> str:
        return str(jobId) + "." + str(status)


class MetadataEvent(WorkflowEvent):
    """
    Represents an event triggered by a change in metadata.

    This event type is used to define triggers that fire a job when a
    Metasheet matching certain criteria is created or modified in the lwfm system.
    The criteria are specified as a dictionary of regular expressions.
    """

    def __init__(self, queryRegExs: dict, fireDefn: 'JobDefn', fireSite: str):
        """
        Initializes a new MetadataEvent.

        Args:
            queryRegExs (dict): A dictionary where keys are metadata property names
                                and values are regular expressions. The event triggers
                                when a Metasheet's properties match these regular expressions.
            fireDefn (JobDefn): The definition of the job to be fired when this event occurs.
            fireSite (str): The name of the site where the `fireDefn` job should be executed.
        """
        super().__init__(fireDefn, fireSite)
        self._query_regexs = queryRegExs

    def getQueryRegExs(self) -> dict:
        """
        Gets the dictionary of query regular expressions for this event.

        Returns:
            dict: The dictionary where keys are metadata property names and values
                  are the regular expressions used to match against Metasheet properties.
        """
        return self._query_regexs

    def __str__(self):
        return super().__str__() + f"+[meta dict:{self.getQueryRegExs()}]"
