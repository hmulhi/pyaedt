import logging
import os.path

from _unittest.conftest import config
import pytest

from pyaedt import Icepak
from pyaedt.aedt_logger import AedtLogger
from pyaedt.generic.settings import settings

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app()
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_00_global_messenger(self):
        msg = AedtLogger()
        msg.clear_messages()
        msg.add_info_message("Test desktop level - Info")
        msg.add_info_message("Test desktop level - Info", level="Design")
        msg.add_info_message("Test desktop level - Info", level="Project")
        msg.add_info_message("Test desktop level - Info", level="Global")
        msg.clear_messages(level=0)
        msg.clear_messages(level=3)

    @pytest.mark.skipif(config["NonGraphical"], reason="Messages not functional in non-graphical mode")
    def test_01_get_messages(self, add_app):  # pragma: no cover
        settings.enable_desktop_logs = True
        msg = self.aedtapp.logger
        msg.clear_messages(level=3)
        msg.add_info_message("Test Info design level")
        msg.add_info_message("Test Info project level", "Project")
        msg.add_info_message("Test Info", "Global")
        assert msg.info_messages
        assert msg.aedt_info_messages
        assert len(msg.messages.info_level) >= 1
        assert len(msg.aedt_messages.project_level) >= 1
        ipk_app = add_app(application=Icepak)
        box = ipk_app.modeler.create_box([0, 0, 0], [1, 1, 1])
        ipk_app.modeler.create_3dcomponent(os.path.join(self.local_scratch.path, "test_m.a3dcomp"))
        box.delete()
        cmp = ipk_app.modeler.insert_3d_component(os.path.join(self.local_scratch.path, "test_m.a3dcomp"))
        ipk_app_comp = cmp.edit_definition()
        msg_comp = ipk_app_comp.logger
        msg_comp.add_info_message("3dcomp, Test Info design level")
        # In 3DComponents, only Global and info level available.
        assert len(msg_comp.messages.info_level) >= 1
        settings.enable_desktop_logs = False
        ipk_app_comp.close_project()

    def test_02_messaging(self, add_app):  # pragma: no cover
        settings.enable_desktop_logs = True
        ipk_app = add_app(application=Icepak)
        msg = ipk_app.logger
        msg.clear_messages(level=3)
        msg.add_info_message("Test Info")
        msg.add_info_message("Test Info", "Project")
        msg.add_info_message("Test Info", "Global")
        msg.add_warning_message("Test Warning at Design Level")
        msg.add_warning_message("Test Warning at Project Level", "Project")
        msg.add_warning_message("Test Warning at Global Level", "Global")
        assert msg.warning_messages
        assert msg.aedt_warning_messages
        msg.add_error_message("Test Error at Design Level")
        msg.add_error_message("Test Error at Project Level", "Project")
        msg.add_error_message("Test Error at Global Level", "Global")
        assert msg.error_messages
        assert msg.aedt_error_messages
        msg.add_info_message("Test Debug")
        msg.add_info_message("Test Debug", "Project")
        msg.add_info_message("Test Debug", "Global")
        assert len(msg.messages.info_level) > 0
        assert len(msg.aedt_messages.global_level) >= 4
        assert len(msg.aedt_messages.project_level) >= 4
        assert len(msg.aedt_messages.design_level) >= 4
        settings.enable_desktop_logs = False

        assert ipk_app.desktop_class.messenger
        assert ipk_app.desktop_class.clear_messages()
