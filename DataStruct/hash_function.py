# -*- coding:utf-8 -*-

import unittest


# ======================== 算法实现 ================================
# 
# 关于质素的选择参考：http://planetmath.org/goodhashtableprimes


def hash_integer(key, M):
    """
    用于整数的散列函数
    """
    return key % M


def hash_float(key, M):
    """
    用于浮点数的散列函数
    """
    return int(key * M)


def hash_string(key, M):
    """
    用于字符串的散列函数
    参考 djb2
    """
    hash = 5381

    for x in key:
        hash = (( hash << 5) + hash) + ord(x)

    return (hash & 0xFFFFFFFF) % M


# ======================== 单元测试 ================================


class TestCaseHashFunction(unittest.TestCase):

    def setUp(self):

        self.M = 769

        self.data_hash_integer_key = 99
        self.data_hash_float_key = 0.45
        self.data_hash_string_key = "I AM TIGER."

        self.result_hash_integer = 99
        self.result_hash_float = 346
        self.result_hash_string = 467

    def test_hash_integer(self):
        self.assertEqual(hash_integer(self.data_hash_integer_key, self.M), self.result_hash_integer)

    def test_hash_float(self):
        self.assertEqual(hash_float(self.data_hash_float_key, self.M), self.result_hash_float)

    def test_hash_string(self):
        self.assertEqual(hash_string(self.data_hash_string_key, self.M), self.result_hash_string)


if __name__ == '__main__':
    unittest.main()
