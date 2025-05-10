"""
Site: Defines an abstract computing location which exposes canonical verbs for
the Auth, Run, and Repo and Spin logical subsystems. The purpose
of lwfm is to permit workflows which span Sites. A new Site would inherit or
implement a driver for each of the subsystems. An application will instantiate
a Site driver using the Site factory method.

The Auth portion of the Site is responsible for user authentication and
authorization. The Run sub-interface provides verbs such as job submit and job
cancel. The Repo portion provides verbs for managing files and metadata.
The Spin portion provides verbs for spinning up and spinning down computing 
resources from a cafeteria of options.

The Site factory method returns the Python class which implements the
interfaces for the named Site. ~/.lwfm/sites.txt can be used to augment the
list of sites provided here with a user's own custom Site implementations. 
"""

#pylint: disable = invalid-name, missing-class-docstring, missing-function-docstring
#pylint: disable = broad-exception-caught

from abc import ABC, abstractmethod
import importlib
import os

from typing import List, TYPE_CHECKING, Union, Optional

from lwfm.midware.Logger import logger
from lwfm.base.JobContext import JobContext
from lwfm.base.JobStatus import JobStatus
from lwfm.base.Metasheet import Metasheet
from lwfm.base.Workflow import Workflow

# Only import for type checking, not at runtime
if TYPE_CHECKING:
    from lwfm.base.JobDefn import JobDefn





# ***************************************************************************
class SitePillar(ABC):
    pass


# ***************************************************************************

class SiteAuth(SitePillar):
    """
    Auth: an interface for a Site's user authentication and authorization
    functions.  Permits a Site to provide some kind of a "login" be it
    programmatic, forced interactive, etc.  A given Site's implementation of
    Auth might squirrel away some returned token (should the Site use such
    things). It could conceptually then provide a quicker "is the auth current"
    method. We assume the implementation of a Site's Run and Repo subsystems
    will, if needed, be provided access under the hood to the necessary
    implementation details from the Auth subsystem.
    """

    @abstractmethod
    def login(self, force: bool = False) -> bool:
        """
        Login to the Site using the Site's own mechanism for authentication and
        caching.

        Params:
            force - if true, forces a login even if the Site detects that the 
                current login is still viable
        Returns:
            bool - true if success, else false

        Example:
            site = Site.getSite(siteName)
            site.getAuth().login()
        """


    @abstractmethod
    def isAuthCurrent(self) -> bool:
        """
        Is the currently cached Site login info still viable?

        Returns:
            bool - true if the login is still viable, else false; the Site might
            not cache, and thus always return false

        Example:
            site = Site.getSite(siteName)
            site.getAuth().login()
            site.getAuth().isAuthCurrent()
        """


# **************************************************************************


class SiteRun(SitePillar):
    """
    Run: in its most basic form, the Run subsystem provides a mechanism to
    submit a job, cancel the job, and interrogate the job's status.  The
    submitting of a job might, for some Sites, involve a batch scheduler.
    Or, for some Sites (like a "local" Site), the run might be immediate.
    On submit of a job the method returns a JobStatus.  A job definition
    (JobDefn) is a description of the job.  Its the role of the Site's Run
    subsystem to interpret the abstract JobDefn in the context of that
    Site.  Thus the JobDefn permits arbitrary name=value pairs which might
    be necessary to submit a job at that Site.  The JobStatus returned is
    canonical - the Site's own status name set is mapped into the lwfm
    canonical name set by the implementation of the Site.Run itself.
    """

    @classmethod
    def _submitJob(cls, jobDefn, parentContext=None, computeType=None, runArgs=None):
        """
        This helper function, not a member of the public interface, lets Python
        threading instantiate a SiteRunDriver of the correct subtype on demand.
        It is used, for example, by the lwfm middleware's event handler mechanism
        to reflectively instantiate a Site Run driver of the correct subtype,
        and then call its submitJob() method.
        """
        runDriver = cls()
        runDriver.submit(jobDefn, parentContext, computeType, runArgs)

    @abstractmethod
    def submit(self, jobDefn: 'JobDefn', 
        parentContext: Union[JobContext, Workflow] = None,
        computeType: str = None, runArgs: dict = None) -> JobStatus:
        """
        Submit the job for execution on this Site. It is an implementation
        detail of the Site what that means - everything from pseudo-immediate
        command line execution, to scheduling on an HPC system. The caller
        should assume the run is asynchronous. We would assume all Sites would
        implement this method. Note that "compute type" is an optional member
        of JobDefn, and might be used by the Site to direct the execution of
        the job.

        [We note that both the JobDefn and the JobContext potentially contain
        a reference to a compute type. Since the Job Context is historical,
        and provided to give that historical context to the job we're about to
        run, its strongly suggested that Site.Run implementations use the
        compute type named in the JobDef, if the concept is present at all on
        the Site. We note also that compute type and Site are relatively
        interchangeable - one can model a compute resource as a compute type,
        or as its own Site, perhaps with a complete inherited Site driver
        implementation.]

        Params:
            jobDefn - the definition of the job to run, might include the name
                of a script, include arguments for the run, etc.
            parentContext - [optional - if none provided, one will be assigned
                and managed by the lwfm framework] information about the
                current JobContext which might be running, thus the job we are
                submitting will be tracked in the digital thread
        Returns:
            JobStatus - preliminary status, containing a JobContext including
                the canonical and Site-specific native job id
        """

    @abstractmethod
    def getStatus(self, jobId: str) -> JobStatus:
        """
        Check the status of a job running on this Site.  The JobContext is an 
        attribute of the JobStatus, and contains the canonical and Site-specific 
        native job id. The implementation of getJobStatus() may use any portion
        of the JobContext to obtain the status of the job, as needed by the Site.

        Parameters:
            jobContext - the context of the executing job, including the native
                job id
        Returns:
            JobStatus - the current known status of the job
        """

    @abstractmethod
    def cancel(self, jobContext: JobContext) -> bool:
        """
        Cancel the job, which might be in a queued state, or might already be running.
        Its up to to the Site how to handle the cancel, including not doing it.  The
        JobContext is obtained from the JobStatus returned by the call to
        submitJob(), or any call to getJobStatus().

        Params:
            jobContext - the context of the job, including the Site-native job id
        Returns:
            bool - true if a successful cancel, else false; callers should invoke the
                getJobStatus() method to obtain final terminal status (e.g., the job
                might have completed successfully prior to the cancel being received,
                the cancel might not be instantaneous, etc.)
        """


# ****************************************************************************

class SiteRepo(SitePillar):
    """
    SiteRepo defines the interface for a Site's repository operations.
    """

    # The siteObjPath can be many things depending on the site.  For a local site,
    # its just a path.  For a remote site, its a reference to an object in some
    # remote repository which might be filesystem, or use some URI, or whatever
    # the site wants.  Some sites may provide no mechanism at all.
    # The siteObjPath can also be blank, which is intended to mean the
    # data is not moved anywhere by instead is just being checked into management
    # in place with metadata.

    @abstractmethod
    def put(self, localPath: str, siteObjPath: str, jobContext: JobContext = None, metasheet: Metasheet = None) -> Metasheet:
        """
        Puts a local file into the site's repository.

        This method copies a file from a local path to a specified
        object path on the site. It can optionally associate metadata
        (Metasheet) with the object and operate within a given JobContext.

        Args:
            localPath: The path to the local file to be uploaded.
            siteObjPath: The site-specific path or reference where the
                         object will be stored.
            jobContext: Optional. The JobContext under which this operation
                        is performed. If None, a new context might be created.
            metasheet: Optional. A Metasheet object containing metadata to
                       associate with the uploaded object.

        Returns:
            A Metasheet object representing the metadata of the stored object,
            including any new metadata generated during the put operation.
            Returns None if the operation fails.
        """
        pass


    @abstractmethod
    def get(self, siteObjPath: str, localPath: str, jobContext: JobContext = None) -> str:
        """
         Gets (downloads) an object from the site's repository to a local path.

         Args:
             siteObjPath: The site-specific path or reference of the object
                          to retrieve.
             localPath: The local path where the retrieved object should be
                        written.
             jobContext: Optional. The JobContext under which this operation
                         is performed. If None, a new context might be created.

         Returns:
             The local path where the object was written. Returns None if
             the operation fails.
         """
        pass

    @abstractmethod
    def find(self, queryRegExs: dict) -> Optional[List[Metasheet]]:
        """
        Finds Metasheets in the site's repository based on query criteria.

        The query is specified as a dictionary of regular expressions, where
        keys are metadata field names and values are regular expressions
        to match against the field values.

        Args:
            queryRegExs: A dictionary where keys are metadata property names
                         and values are regular expressions to match.

        Returns:
            A list of Metasheet objects that match the query criteria.
            Returns an empty list or None if no matches are found or if
            an error occurs.
        """
        pass


# *****************************************************************************
# Spin: mostly vaporware.  In theory some Sites would expose mechanisms to create
# (provision) and destroy various kinds of computing devices.  These might be
# single nodes, or entire turnkey cloud-bases HPC systems.

class SiteSpin(SitePillar):

    @abstractmethod
    def listComputeTypes(self) -> List[str]:
        """
        List the compute types supported by the Site.  Compute types are specific
        runtime resources (if any) within the Site. The Site might not have any concept
        and return an empty list, or a list of one singular type of the Site.  Or, the
        Site might front a number of resources, and return a list of names.

        Returns:
            List[str] - a list of names, potentially empty or None
        """


# ****************************************************************************
# Site: the Site is simply a name and the getters and setters for its Auth, Run,
# Repo subsystems.
#
# The getSite() factory utility method returns the Python class which implements the
# interfaces for the named Site. ~/.lwfm/sites.txt can be used to augment the
# list of sites provided here with a user's own custom Site implementations. In the
# event of a name collision between the user's sites.txt and those hardcoded here,
# the user's sites.txt config trumps.


class Site:
    """
    Represents a computing site, encapsulating its authentication, run,
    repository, and spin (resource provisioning) capabilities.

    A Site object is typically obtained via the `Site.getSite()` factory method,
    which dynamically loads the appropriate driver implementation based on the
    site name.
    """

    def __init__(self, site_name: str = None, auth_driver: SiteAuth = None,
        run_driver: SiteRun = None, repo_driver: SiteRepo = None,
        spin_driver: SiteSpin = None):
        """
        Initializes a new Site instance.

        This constructor is typically called by the specific site driver's __init__
        method or by the `getSite` factory method.

        Args:
            site_name: The name of the site.
            auth_driver: An instance of a SiteAuth implementation.
            run_driver: An instance of a SiteRun implementation.
            repo_driver: An instance of a SiteRepo implementation.
            spin_driver: An instance of a SiteSpin implementation.
        """
        self._site_name = site_name
        self._auth_driver = auth_driver
        self._run_driver = run_driver
        self._repo_driver = repo_driver
        self._spin_driver = spin_driver
        # pre-defined Sites and their associated driver implementations
        self._sites = {
            "local": "lwfm.sites.LocalSite.LocalSite",
            #"insitu": "lwfm.sites.InSituSite.InSituSite",
            #"ibm_quantum": "lwfm.sites.IBMQuantumSite.IBMQuantumSite"
        }

    def getSiteName(self) -> Optional[str]:
        """
        Gets the name of the site.

        Returns:
            The name of the site, or None if not set.
        """
        return self._site_name

    def setSiteName(self, name: str) -> None:
        """
        Sets the name of the site.

        Args:
            name: The new name for the site.
        """
        self._site_name = name

    def getAuthDriver(self) -> SiteAuth:
        """
        Gets the authentication driver for this site.

        Returns:
            The SiteAuth driver instance.
        """
        return self._auth_driver

    def setAuthDriver(self, driver: SiteAuth):
        """
        Sets the authentication driver for this site.

        Args:
            driver: The SiteAuth driver instance.
        """
        self._auth_driver = driver

    def getRunDriver(self) -> SiteRun:
        """
        Gets the run (job execution) driver for this site.

        Returns:
            The SiteRun driver instance.
        """
        return self._run_driver

    def setRunDriver(self, driver: SiteRun) -> None:
        """
        Sets the run (job execution) driver for this site.

        Args:
            driver: The SiteRun driver instance.
        """
        self._run_driver = driver

    def getRepoDriver(self) -> Optional[SiteRepo]:
        """
        Gets the repository (data management) driver for this site.

        Returns:
            The SiteRepo driver instance, or None if not set.
        """
        return self._repo_driver

    def setRepoDriver(self, driver: SiteRepo):
        """
        Sets the repository (data management) driver for this site.

        Args:
            driver: The SiteRepo driver instance.
        """
        self._repo_driver = driver

    def getSpinDriver(self) -> Optional[SiteSpin]:
        """
        Gets the spin (resource provisioning) driver for this site.

        Returns:
            The SiteSpin driver instance, or None if not set.
        """
        return self._spin_driver

    def setSpinDriver(self, driver: SiteSpin):
        """
        Sets the spin (resource provisioning) driver for this site.

        Args:
            driver: The SiteSpin driver instance.
        """
        self._spin_driver = driver

    @staticmethod
    def _getSiteEntry(site: str):
        siteSet = {
            "local": "lwfm.sites.LocalSite.LocalSite",
            "insitu": "lwfm.sites.InSituSite.InSituSite",
            "ibm_quantum": "lwfm.sites.IBMQuantumSite.IBMQuantumSite"
        }
        # is there a local site config?
        path = os.path.expanduser("~") + "/.lwfm/sites.txt"
        # Check whether the specified path exists or not
        if os.path.exists(path):
            logger.info("Loading custom site configs from ~/.lwfm/sites.txt")
            with open(path) as f:
                for line in f:
                    name, var = line.split("=")
                    name = name.strip()
                    var = var.strip()
                    logger.info(
                        "Registering driver " + var + " for site " + name
                    )
                    siteSet[name] = var
        return siteSet.get(site)

    @staticmethod
    def getSite(site: str = "local") -> 'Site':
        """
          Factory method to get an instance of a specific Site driver.

          Dynamically imports and instantiates the Site driver class
          based on the provided site name.

          Args:
              site: The name of the site to instantiate. Defaults to "local".

          Returns:
              An instance of the specified Site driver.

          Raises:
              Exception: If the site driver cannot be found or instantiated.
          """

        try:
            entry = Site._getSiteEntry(site)
            module = importlib.import_module(entry.rsplit(".", 1)[0])
            class_ = getattr(module, str(entry.rsplit(".", 1)[1]))
            inst = class_()
            inst.setSiteName(site)
            return inst
        except Exception as ex:
            logger.error(
                f"Cannot instantiate Site for {site} {ex}"
            )
            raise ex
