import unittest

import customtkinter as ctk


class HighlightThemeTests(unittest.TestCase):
    def test_good_bad_colors_differ_for_light_and_dark(self):
        ctk.set_appearance_mode("Light")
        g_l, b_l = "#2E7D52", "#D81B60"
        self.assertNotEqual(g_l, b_l)
        ctk.set_appearance_mode("Dark")
        g_d, b_d = "#69F0AE", "#FF80AB"
        self.assertNotEqual(g_d, b_d)


if __name__ == "__main__":
    unittest.main()
