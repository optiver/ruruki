"""
Some test helper functions.
"""
import tempfile
import pkg_resources


def get_test_dump_graph_file_handler():  # pylint: disable=invalid-name
    """
    Find and return the small people test graph dump file.
    """
    return open(
        pkg_resources.resource_filename(
            "ruruki", "test_utils/small_people_graph.dump"
        )
    )


def create_tmp_file_handler(content=None, delete=False):
    """
    Create a temp named file.
    """
    if content is None:
        content = ""
    tmp_file = tempfile.NamedTemporaryFile(mode="w+", delete=delete)
    tmp_file.write(content)
    tmp_file.seek(0)
    return tmp_file
