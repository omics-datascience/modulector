from django.test.runner import DiscoverRunner


class DjangoTestSuiteRunner(DiscoverRunner):
    """
    This runner prevents Django from creating and destroying the test database. This is useful as Modulector has
    read-only preloaded data in the database.
    """
    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass
