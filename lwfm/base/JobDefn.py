"""
A Job Definition is the abstract representation of a job, the non-instantiated 
description. The JobDefn will be passed to the Site's Run driver which will use the 
args to instantiate a job from the definition.
"""

#pylint: disable = missing-function-docstring, invalid-name

from typing import List

from lwfm.util.IdGenerator import IdGenerator


class JobDefn:
    """
    The static definition of a job, to be instantiated at runtime by the Site.Run 
    subsystem. The JobDefn is not presumed to be portable, though it is possible 
    and the onus is on the user or the author of the Site driver.  
    Within the JobDefn will be baked arbitrary arguments, which might very well be 
    Site-specific (e.g., parameters to a specific Site HPC scheduler).  It is 
    ultimately the job of the Site Run subsystem to interpret the job defn and 
    execute it.  The standard arguments which would be needed to aid in broad 
    portability are not specified by this framework, nor are they precluded.
    """

    def __init__(self, entryPoint: str = None):
        """
        Initializes a new JobDefn object.

        Args:
            entryPoint (str, optional): The entry point or command for the job. Defaults to None.
        """
        self._defn_id = IdGenerator.generateId()
        self.setEntryPoint(entryPoint)
        self.setName("")
        self.setJobArgs([])

    def getDefnId(self) -> str:
        """
        Gets the unique definition ID for this job definition.

        Returns:
            str: The definition ID.
        """
        return self._defn_id

    def setName(self, name: str) -> None:
        """
        Sets the name of the job definition.

        Args:
            name (str): The human-readable name for the job definition.
        """
        self._name = name

    def getName(self) -> str:
        """
        Gets the name of the job definition.

        Returns:
            str: The name of the job definition.
        """
        return self._name

    def setEntryPoint(self, entryPoint: str) -> None:
        """
        Sets the entry point for the job.

        The entry point is a declaration of the command to run, from the perspective of the Site.
        This can be anything from an actual command string, or a complex serialized object.
        It is entirely up to the Site how to specify and interpret the entry point.

        Args:
            entryPoint (str): The entry point string or command.
        """
        self._entryPoint = entryPoint

    def getEntryPoint(self) -> str:
        """
        Gets the entry point for the job.

        Returns:
            str: The entry point string or command.
        """
        return self._entryPoint

    def setJobArgs(self, args: List[str]) -> None:
        """
        Sets the arguments for the job.

        These are distinct from the entry point and represent arbitrary arguments
        the job might desire at runtime.

        Args:
            args (List[str]): A list of string arguments for the job.
        """
        self._jobArgs = args

    def getJobArgs(self) -> List[str]:
        """
        Gets the arguments for the job.

        Returns:
            List[str]: A list of string arguments for the job.
        """
        return self._jobArgs
