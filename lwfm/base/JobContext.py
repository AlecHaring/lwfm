"""
JobContext holds the identifier for the job, info about the target site, and
tracking info.
"""

#pylint: disable = invalid-name, missing-function-docstring

from lwfm.util.IdGenerator import IdGenerator


class JobContext:
    """
    The runtime execution context of the job.  It contains the id of the job and 
    references to its parent jobs, if any.  A JobStatus can reference a JobContext,
    and then augment it with updated job status information.
    """

    def __init__(self):
        self._job_id = IdGenerator.generateId()
        self._native_id = self._job_id      # important: can be set later
        self._parent_job_id = self._job_id
        self._workflow_id = self._job_id    # important: can be set later
        self._name = self._job_id           # important: can be set later
        self._compute_type = "default"
        self._site_name = "local"

    def addParentContext(self, parentContext: "JobContext") -> None:
        """
        Adds information from a parent JobContext to the current context.

        If a parentContext is provided, the current job's parent_job_id,
        workflow_id, site_name, and name are updated based on the parent.
        The name is prepended with the parent's name.

        Args:
            parentContext: The JobContext of the parent job.
        """
        if parentContext is not None:
            self._parent_job_id = parentContext.getJobId()
            self._workflow_id = parentContext.getWorkflowId()
            self._site_name = parentContext.getSiteName()
            self._name = (parentContext.getName() or "") + "_" + (self._name or "")

    def setJobId(self, idValue: str) -> None:
        """
        Sets the job identifier.

        Args:
            idValue: The new job identifier.
        """
        self._job_id = idValue

    def getJobId(self) -> str:
        """
        Gets the job identifier.

        Returns:
            The job identifier.
        """
        return self._job_id

    def setNativeId(self, nativeId: str) -> None:
        """
        Sets the native site's job identifier.

        Args:
            nativeId: The native job identifier.
        """
        self._native_id = nativeId

    def getNativeId(self) -> str:
        """
        Gets the native site's job identifier.

        Returns:
            The native job identifier.
        """
        return self._native_id

    def setParentJobId(self, parentId: str) -> None:
        """
        Sets the parent job identifier.

        Args:
            parentId: The parent job identifier.
        """
        self._parent_job_id = parentId

    def getParentJobId(self) -> str:
        """
        Gets the parent job identifier.

        Returns:
            The parent job identifier.
        """
        return self._parent_job_id

    def setWorkflowId(self, workflowId: str) -> None:
        """
        Sets the workflow identifier.

        Args:
            workflowId: The workflow identifier.
        """
        self._workflow_id = workflowId

    def getWorkflowId(self) -> str:
        """
        Gets the workflow identifier.

        Returns:
            The workflow identifier.
        """
        return self._workflow_id

    def setName(self, name: str) -> None:
        """
        Sets the name of the job.

        Args:
            name: The human-readable name for the job.
        """
        self._name = name

    def getName(self) -> str:
        """
        Gets the name of the job.

        Returns:
            The name of the job.
        """
        return self._name

    def setComputeType(self, computeType: str) -> None:
        """
        Sets the compute type for the job.

        Args:
            computeType: The type of compute resource.
        """
        self._compute_type = computeType

    def getComputeType(self) -> str:
        """
        Gets the compute type for the job.

        Returns:
            The compute type.
        """
        return self._compute_type

    def setSiteName(self, siteName: str) -> None:
        """
        Sets the name of the site where the job runs.

        Args:
            siteName: The name of the site.
        """
        self._site_name = siteName

    def getSiteName(self) -> str:
        """
        Gets the name of the site where the job runs.

        Returns:
            The site name.
        """
        return self._site_name

    def __str__(self) -> str:
        return f"[ctx job:{self.getJobId()} native:{self.getNativeId()} " + \
            f"parent:{self.getParentJobId()} wf:{self.getWorkflowId()} " + \
            f"site:{self.getSiteName()} " + \
            f"compute:{self.getComputeType()}]"
