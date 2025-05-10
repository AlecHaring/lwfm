"""
A basic dictionary to hold metadata about data objects under management by lwfm
"""

#pylint: disable = invalid-name, missing-class-docstring, missing-function-docstring

from lwfm.util.IdGenerator import IdGenerator

class Metasheet:
    """
    A collection of name=value pairs representing metadata for a data object
    managed by lwfm. It typically includes information about the data's location (site and URL)
    and any other relevant properties.
    """

    def __init__(self, siteName: str, siteUrl: str, props: dict = None):
        """
        Initializes a new Metasheet object.

        Args:
            siteName (str): The name of the site where the associated data object is located.
            siteUrl (str): The URL or path of the data object on the site.
            props (dict, optional): A dictionary of properties for the metasheet.
                                     Defaults to None, which will be initialized as an empty
                                     dictionary if not provided, or used as is if provided.
        """
        self._sheet_id = IdGenerator.generateId()
        self._job_id = self._sheet_id
        self._siteName = siteName
        self._siteUrl = siteUrl
        self._props = props

    def __str__(self):
        return f"{self._props}"

    def getSheetId(self) -> str:
        return self._sheet_id

    def getJobId(self) -> str:
        return self._job_id

    def setJobId(self, jobId: str) -> None:
        self._job_id = jobId

    def getSiteName(self) -> str:
        return self._siteName

    def setSiteName(self, siteName: str) -> None:
        self._siteName = siteName

    def getSiteUrl(self) -> str:
        return self._siteUrl

    def setSiteUrl(self, siteUrl: str) -> None:
        self._siteUrl = siteUrl

    def getProps(self) -> dict:
        return self._props

    def setProps(self, props: dict) -> None:
        self._props = props
