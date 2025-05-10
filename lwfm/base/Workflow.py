"""
A collection of jobs and their associated (meta)information.
"""

#pylint: disable = invalid-name, missing-function-docstring

from lwfm.util.IdGenerator import IdGenerator

class Workflow:
    """
    A collection of jobs and their associated (meta)information.

    Workflows are used to group related jobs and manage their execution.
    Each workflow has a unique ID, an optional name, and an optional description.
    It can also store arbitrary properties as a dictionary.
    """

    def __init__(self, name: str = None, description: str = None):
        """
        Initializes a new Workflow instance.

        Args:
            name (str, optional): The name of the workflow. Defaults to None.
            description (str, optional): The description of the workflow. Defaults to None.
        """
        self._workflow_id = IdGenerator.generateId()
        self._name = name
        self._description = description
        self._props = {}

    def _setWorkflowId(self, idValue: str) -> None:
        self._workflow_id = idValue

    def getWorkflowId(self) -> str:
        return self._workflow_id

    def setName(self, name: str) -> None:
        self._name = name

    def getName(self) -> str:
        return self._name

    def setDescription(self, description: str) -> None:
        self._description = description

    def getDescription(self) -> str:
        return self._description

    def getProps(self) -> dict:
        return self._props

    def setProps(self, props: dict) -> None:
        self._props = props
