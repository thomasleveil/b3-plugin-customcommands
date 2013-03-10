import logging
from mock import Mock, patch
from mockito import when
import time
import unittest2
from b3.config import XmlConfigParser
from b3.plugins.admin import AdminPlugin


class logging_disabled(object):
    """
    context manager that temporarily disable logging.

    USAGE:
        with logging_disabled():
            # do stuff
    """
    DISABLED = False

    def __init__(self):
        self.nested = logging_disabled.DISABLED

    def __enter__(self):
        if not self.nested:
            logging.getLogger('output').propagate = False
            logging_disabled.DISABLED = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.nested:
            logging.getLogger('output').propagate = True
            logging_disabled.DISABLED = False


class CustomcommandsTestCase(unittest2.TestCase):

    def setUp(self):
        self.sleep_patcher = patch("time.sleep")
        self.sleep_mock = self.sleep_patcher.start()

        # create a FakeConsole parser
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString(r"""<configuration/>""")
        with logging_disabled():
            from b3.fake import FakeConsole
            self.console = FakeConsole(self.parser_conf)

        # load the admin plugin
        with logging_disabled():
            self.adminPlugin = AdminPlugin(self.console, '@b3/conf/plugin_admin.xml')
            self.adminPlugin._commands = {}  # work around known bug in the Admin plugin which makes the _command property shared between all instances
            self.adminPlugin.onStartup()

        # make sure the admin plugin obtained by other plugins is our admin plugin
        when(self.console).getPlugin('admin').thenReturn(self.adminPlugin)

        self.console.screen = Mock()
        self.console.time = time.time
        self.console.upTime = Mock(return_value=3)

        self.console.cron.stop()

    def tearDown(self):
        self.sleep_patcher.stop()