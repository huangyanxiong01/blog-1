# -*- coding:utf-8 -*-

import unittest


# ======================== 算法实现 ================================
# 
# 优化提升：将 arr_counter 换成 byte 类型或者 bit 类型, 可以很好地降低计数排序的空间复杂度

def count_sort(arr, arr_counter):
    """
    计数排序
    一种不是基于比较的排序方式, 利用辅助数组下标本来就有序的特点对目标数组进行排序
    """
    # 利用 arr_counter 的下标对 arr 排序
    for item in arr:
        arr_counter[item] += 1

    # 简单输出排序结果
    for index, item in enumerate(arr_counter):
        if (item != 0):
            # 处理数组含有重复元素的情况
            for _ in range(item):
                print index


# ======================== 单元测试 ================================


class TestCaseCountSort(unittest.TestCase):

    def setUp(self):
        # TODO
        pass

    def test_count_sort(self):
        # TODO
        pass


if __name__ == '__main__':
    # unittest.main()

    # 待排序数组
    arr = [1, 0, 3, 1, 0, 1, 1]

    # 辅助数组的大小为：max(arr) - min(arr)
    # 这里跳过 max(arr) 和 min(arr) 的查询, 可以通过快速选择算法进行查询
    arr_counter = [0 for _ in range(7)]

    count_sort(arr, arr_counter)
