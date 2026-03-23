import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "scripts" / "launchers" / "mysql_import.py"


def load_mysql_import_module():
    spec = importlib.util.spec_from_file_location("mysql_import", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestLauncherMysqlImport(unittest.TestCase):
    def test_build_mysql_import_command_bootstraps_without_preselecting_database(self):
        module = load_mysql_import_module()

        cmd, masked = module.build_mysql_import_command(
            mysql_client="/tmp/mysql",
            mysql_port=3306,
            password="secret",
        )

        self.assertEqual(
            cmd,
            ["/tmp/mysql", "-uroot", "-P3306", "-psecret"],
        )
        self.assertNotIn("-e", cmd)
        self.assertNotIn("source", " ".join(cmd))
        self.assertEqual(masked, "/tmp/mysql -uroot -P3306 -p***")

    def test_build_mysql_import_command_can_target_existing_database(self):
        module = load_mysql_import_module()

        cmd, masked = module.build_mysql_import_command(
            mysql_client="/tmp/mysql",
            mysql_port=3306,
            password="secret",
            database="zjt",
        )

        self.assertEqual(
            cmd,
            ["/tmp/mysql", "-uroot", "-P3306", "-psecret", "zjt"],
        )
        self.assertEqual(masked, "/tmp/mysql -uroot -P3306 -p*** zjt")


if __name__ == "__main__":
    unittest.main()
