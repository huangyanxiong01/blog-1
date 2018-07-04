# -*- coding:utf-8 -*-

import unittest


# ======================== 算法实现 ================================


def less(num1, num2):
    """
    简单的比较大小
    """
    return num1 <= num2


def partition(arr, start, end):
    """
    将基准数放到有序的位置上，以此来划分子问题
    """
    # 简单地以第一个 item 为基准数
    compare = arr[start]
    # 计数器初始化
    i = start
    j = end

    # 大循环条件
    # i == j 代表基准数已经处于有序位置, 可以结束本次划分, 否则继续执行循环体
    while (i != j):
        # j 从后往前移动
        while (j > i):
            # 找比基准数小的数
            if not (less(arr[j], compare)):
                # 没找到的话 j 就继续往前移
                j -= 1
            else:
                # 找到了就交换 arr[i] 和 arr[j]
                arr[i], arr[j] = arr[j], arr[i]
                # i 后移一位
                i += 1
                # 结束本次 j 前移查找
                break
        # i 从前往后移动
        while (i < j):
            # 找比基准数大的数
            if (less(arr[i], compare)):
                # 没找到的话 i 就继续后移
                i += 1
            else:
                # 找到了就交换 arr[i] 和 arr[j]
                arr[i], arr[j] = arr[j], arr[i]
                # j 前移一位
                j -= 1
                # 结束本次 i 后移查找
                break

    # 返回划分位置
    return i


def quick_sort(arr, start, end):
    """
    快速排序的主函数
    """
    # 递归结束条件
    if (start >= end):
        return

    # 得到划分点 compare, 实际的排序就是发生在这里
    compare = partition(arr, start, end)

    # 根据划分点递归处理左右子问题
    quick_sort(arr, start, compare - 1)
    quick_sort(arr, compare + 1, end)

    # 返回排好序的数组
    return arr


# ======================== 单元测试 ================================


class TestCaseQuickSort(unittest.TestCase):

    def setUp(self):
        self.data_arr1 = [3, 2, 5, 1, 8]
        self.data_arr1_start = 0
        self.data_arr1_end = 4

        self.data_arr2 = [1, 4, 8, 2, 55, 3, 4, 8, 6, 4, 0, 11, 34, 90, 23, 54, 77, 9, 2, 9, 4, 10]
        self.data_arr2_start = 0
        self.data_arr2_end = 21

        self.data_arr3 = [4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 0, 0, 0, -1, -1, -1]
        self.data_arr3_start = 0
        self.data_arr3_end = 17

        self.result_arr1 = [1, 2, 3, 5, 8]
        self.result_arr2 = [0, 1, 2, 2, 3, 4, 4, 4, 4, 6, 8, 8, 9, 9, 10, 11, 23, 34, 54, 55, 77, 90]
        self.result_arr3 =  [-1, -1, -1, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]

    def test_quick_sort(self):
        self.assertEqual(quick_sort(self.data_arr1, self.data_arr1_start, self.data_arr1_end),
                         self.result_arr1)

        self.assertEqual(quick_sort(self.data_arr2, self.data_arr2_start, self.data_arr2_end),
                         self.result_arr2)

        self.assertEqual(quick_sort(self.data_arr3, self.data_arr3_start, self.data_arr3_end),
                         self.result_arr3)


if __name__ == '__main__':
    unittest.main()
