"""
Example of data management using lwfm's repository interface and metasheets.

Demonstrates:
- Storing a file with metadata in the repository.
- Querying for objects using exact and wildcard metadata values.
"""

from lwfm.base.Site import Site
from lwfm.base.Metasheet import Metasheet
from lwfm.util.IdGenerator import IdGenerator
from lwfm.midware.Logger import logger


DATA_FILE = "example_date.out"
DATA_FILE_DEST = "/tmp/someFile.dat"


def main() -> None:
    """Demonstrate repository interface and metasheet functionality.

    Steps performed:
    1. Authenticate to the local site.
    2. Generate unique ID and create metadata.
    3. Put a file into the repository with associated metadata.
    4. Query for objects using exact metadata values.
    5. Query for objects using wildcard metadata values.
    """

    # Site initialization and authentication
    site = Site.getSite("local")
    site.getAuthDriver().login()

    # Generate a unique sample ID and attached metadata
    sample_id = IdGenerator.generateId()
    metadata = {"foo": "bar", "hello": "world", "sampleId": sample_id}

    # Put a file into the repo
    msheet = Metasheet(site.getSiteName(), DATA_FILE, metadata)
    site.getRepoDriver().put(
        DATA_FILE,
        DATA_FILE_DEST,
        metasheet=msheet
    )

    # Query 1: Find by exact sampleId
    clause = {"sampleId": sample_id}
    logger.info(f"Finding metasheets matching: {clause}")
    sheets = site.getRepoDriver().find(clause)
    if sheets:
        for s in sheets:
            logger.info(f"Found match: {str(s)}")
    else:
        logger.error("No matches found")

    # Query 2: Find by wildcard on "foo"
    clause = {"foo": "b*"}
    logger.info(f"Finding metasheets matching: {clause}")
    sheets = site.getRepoDriver().find(clause)
    if sheets:
        for s in sheets:
            logger.info(f"Found match: {str(s)}")
    else:
        logger.error("No matches found")


if __name__ == "__main__":
    main()
