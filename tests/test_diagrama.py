import os
import unittest
from CreateExpediente import generate_diagram


class TestGenerateDiagram(unittest.TestCase):
    def test_generate_creates_files(self):
        pkg_dir = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(pkg_dir, 'output_test')
        # Ensure clean state
        if os.path.exists(output_dir):
            for f in os.listdir(output_dir):
                try:
                    os.remove(os.path.join(output_dir, f))
                except Exception:
                    pass
        img, doc = generate_diagram(output_dir=output_dir)
        self.assertTrue(os.path.exists(img))
        self.assertTrue(os.path.getsize(img) > 0)
        self.assertTrue(os.path.exists(doc))
        self.assertTrue(os.path.getsize(doc) > 0)


if __name__ == '__main__':
    unittest.main()
