# -*- coding:utf-8 -*-

import unittest


# ======================== 算法实现 ================================


def binary_search_by_recursion(target, arr, start, end):
    """
    二分查找递归版
    返回匹配的 item 的 index, 没找到就返回 -1, 当有重复 item 时, 不保证是返回第一个 item 的 index
    """
    # 递归结束条件
    if (start <= end):
        # 计算中间值
        mid = start + (end - start)/2
        compare = arr[mid]

        # target 与 compare 比较, 并递归处理
        if (target == compare):
            return mid
        elif (target < compare):
            return binary_search_by_recursion(target, arr, start, mid - 1)
        else:
            return binary_search_by_recursion(target, arr, mid + 1, end)
    else:
        return -1


def binary_search_by_loops(target, arr, start, end):
    """
    二分查找循环版
    返回匹配的 item 的 index, 没找到就返回 -1, 当有重复 item 时, 不保证是返回第一个 item 的 index
    """
    # 循环结束条件
    while (start <= end):
        # 计算中间值
        mid = start + (end - start)/2
        compare = arr[mid]

        # target 与 compare 比较, 并改变循环条件
        if (target == compare):
            return mid
        elif (target < compare):
            end = mid - 1
        else:
            start = mid + 1

    return -1


# ======================== 单元测试 ================================


class TestCaseBinarySearch(unittest.TestCase):

    def setUp(self):
        self.target_1 = 8
        self.target_2 = 9
        self.target_3 = 90
        self.target_4 = 1000

        self.data_arr = [0, 1, 2, 2, 3, 4, 4, 4, 4, 6, 8, 8, 9, 9, 10, 11, 23, 34, 54, 55, 77, 90]
        self.data_arr_start = 0
        self.data_arr_end = 21

    def test_binary_search_by_recursion(self):
        self.assertEqual(binary_search_by_recursion(self.target_1, self.data_arr,
            self.data_arr_start, self.data_arr_end), 10)
        self.assertEqual(binary_search_by_recursion(self.target_2, self.data_arr,
            self.data_arr_start, self.data_arr_end), 13)
        self.assertEqual(binary_search_by_recursion(self.target_3, self.data_arr,
            self.data_arr_start, self.data_arr_end), 21)
        self.assertEqual(binary_search_by_recursion(self.target_4, self.data_arr,
            self.data_arr_start, self.data_arr_end), -1)

    def test_binary_search_by_loops(self):
        self.assertEqual(binary_search_by_loops(self.target_1, self.data_arr,
            self.data_arr_start, self.data_arr_end), 10)
        self.assertEqual(binary_search_by_loops(self.target_2, self.data_arr,
            self.data_arr_start, self.data_arr_end), 13)
        self.assertEqual(binary_search_by_loops(self.target_3, self.data_arr,
            self.data_arr_start, self.data_arr_end), 21)
        self.assertEqual(binary_search_by_loops(self.target_4, self.data_arr,
            self.data_arr_start, self.data_arr_end), -1)


if __name__ == '__main__':
    unittest.main()
