from scrap import test
from scrap import utils


class UtilsTest(test.TestCase):
    def test_chunks(self):
        f = utils.chunks

        input = [1, 2, 3]
        self.assertEquals([[1, 2], [3]], f(input, 2))
        self.assertEquals([[1, 2, 3]], f(input, 3))
        self.assertEquals([[1, 2, 3]], f(input, 5))

        input = []
        self.assertEquals([], f(input, 2))
