# -*- coding:utf-8 -*-

import unittest

# import sys
# sys.setrecursionlimit(10000)


# ======================== 算法实现 ================================


def less(num1, num2):
    """
    简单的比较大小
    """
    return num1 < num2


def merge(arr, start, mid, end):
    """
    二路归并
    """
    # 辅助数组初始化
    aux = arr[:]
    # 辅助数组优化
    # aux = arr[start:end+1]
    # for 循环中的 `arr[k] = aux[i]` 改成 `arr[k+start] = aux[i]`

    # 计数器初始化
    i = start
    j = mid + 1

    # 大循环条件
    for k in xrange(start, end + 1):
        # 左边取完
        if (i > mid):
            arr[k] = aux[j]
            j += 1
        # 右边取完
        elif (j > end):
            arr[k] = aux[i]
            i += 1
        # 左边当前小于右边当前
        elif (less(aux[i], aux[j])):
            arr[k] = aux[i]
            i += 1
        # 右边当前小于左边当前
        else:
            arr[k] = aux[j]
            j += 1


def merge_sort(arr, start, end):
    """
    归并排序主函数
    """
    # 递归结束条件
    if (start >= end):
        return

    # 取中间数
    mid = start + (end - start)/2

    # 递归处理
    merge_sort(arr, start, mid)
    merge_sort(arr, mid + 1, end)
    # 原地二路归并
    merge(arr, start, mid, end)

    # 返回排好序的数组
    return arr

# ======================== 单元测试 ================================


class TestCaseMergeSort(unittest.TestCase):

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

    def test_merge_sort(self):
        self.assertEqual(merge_sort(self.data_arr1, self.data_arr1_start, self.data_arr1_end),
                         self.result_arr1)

        self.assertEqual(merge_sort(self.data_arr2, self.data_arr2_start, self.data_arr2_end),
                         self.result_arr2)

        self.assertEqual(merge_sort(self.data_arr3, self.data_arr3_start, self.data_arr3_end),
                         self.result_arr3)


if __name__ == '__main__':
    unittest.main()
