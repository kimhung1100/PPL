import unittest
from TestUtils import TestParser


class ParserSuite(unittest.TestCase):
    
        
    # def test_program(self):
    #     """Simple program: int main() {} """
    #     input = """x: integer = 65;
    #     fact: function integer (n: integer) {
    #         if (n == 0) return 1;
    #         else return n * fact(n - 1);
    #     }
    #     inc: function void(out n: integer, delta: integer) {
    #         n = n + delta;
    #     }
    #     main: function void() {
    #         delta: integer = fact(3);
    #         inc(x, delta);
    #         printInteger(x);
    #     }"""
    #     expect = "successful"
    #     self.assertTrue(TestParser.test(input, expect, 201))
        
    def test_simple_program(self):
        """test array"""
        input = """func: function integer (n: integer) {
            a = b[1];
            x: integer = 12.;
            }"""
        expect = "successful"
        self.assertTrue(TestParser.test(input, expect, 202))
        
    # def test_simple_program(self):
    #     """test array"""
    #     input = """func: function integer (n: integer) {
    #         0a12 = b[1];
    #         }"""
    #     expect = "Error on line 2 col 21: ;"
    #     self.assertTrue(TestParser.test(input, expect, 203))
        
    # def test_nonline_program(self):
    #     """test array"""
    #     input = """"""
    #     expect = "Success"
    #     self.assertTrue(TestParser.test(input, expect, 204))
        
    # def test_simple_program(self):
    #     """test array"""
    #     input = """func: function integer (n: integer) {
    #         a = b[[1]];
    #         }"""
    #     expect = "successful"
    #     self.assertTrue(TestParser.test(input, expect, 203))
