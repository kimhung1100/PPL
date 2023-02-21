import unittest
from TestUtils import TestLexer


class LexerSuite(unittest.TestCase):

    # def test_lowercase_identifier(self):
    #     """test identifiers"""
    #     input="func : function integer ( n : integer)"
    #     expect= 'abc,a12,<EOF>'
    #     self.assertTrue(TestLexer.test(input, expect, 101))
        
    # def test_uppercase_identifier(self):
    #     """test identifiers 1"""
    #     input = "abc A12"
    #     expect = "abc,A12,<EOF>"
    #     self.assertTrue(TestLexer.test(input, expect, 102))
        
    # def test_3case_identifier(self):
    #     """test identifiers 3"""
    #     input = "abc?svn"
    #     expect = "abc,Error Token ?"
    #     self.assertTrue(TestLexer.test(input, expect, 103))
    
    # def test_3case_identifier(self):
    #     """test identifiers 4"""
    #     input = "0a12"
    #     expect = "Error Token 0"
    #     self.assertTrue(TestLexer.test(input, expect, 104))
        
    # def test_3case_identifier(self):
    #     """test stringlit 4"""
    #     input = """ "He asked me: \\"Where is John?\\"" """
    #     expect = "He asked me: \"Where is John?\",<EOF>"
    #     self.assertTrue(TestLexer.test(input, expect, 105))
    
    
    # def test_3case_identifier(self):
    #     """test stringlit 4"""
    #     input='"Oi con song que -> in english: \\"Oh my gosh, so shy\""'
    #     expect = "He asked me: \"Where is John?\",<EOF>"
    #     self.assertTrue(TestLexer.test(input, expect, 106))
        
    def test_3case_identifier(self):
        """test intlit 1"""
        input="""func: function integer (n: integer) {
            00aa = b[1];
            x: integer = 12.1;
            b = 0a12;
            }"""
        expect = ""
        self.assertTrue(TestLexer.test(input, expect, 106))
        
