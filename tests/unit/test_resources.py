import unittest

from resources import bundle_dir, resource_path, user_data_dir


class ResourcesTests(unittest.TestCase):
    def test_bundle_contains_project_files(self):
        bd = bundle_dir()
        self.assertTrue((bd / "levels_data.py").exists() or (bd / "main.py").exists())
        self.assertTrue((bd / "csharp_validator" / "MeowValidator.csproj").is_file())
        self.assertTrue((bd / "assets" / "meow_pink.json").is_file())

    def test_resource_path_audio(self):
        p = resource_path("assets", "audio", "meow.wav")
        self.assertTrue(str(p).endswith("meow.wav"))
        self.assertTrue(p.is_file(), "run: python tools/generate_meow_wav.py")

    def test_user_data_is_dir(self):
        ud = user_data_dir()
        self.assertTrue(ud.is_dir())

    def test_paw_window_icon_files_exist(self):
        bd = bundle_dir()
        self.assertTrue((bd / "assets" / "paw_icon.png").is_file())
        self.assertTrue((bd / "assets" / "paw_icon.ico").is_file())


if __name__ == "__main__":
    unittest.main()
