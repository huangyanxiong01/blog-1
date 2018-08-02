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
    将基准数摆放到有序的位置上, 并返回该位置
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


def quick_select(k, arr, start, end):
    """
    快速选择, 返回第 k 小的数
    """
    # 递归结束条件
    if (start <= end):
        # 基准数下标, 即第 k 小的数
        index = partition(arr, start, end)

        # 和快速排序的区别主要是下面这部分
        # (因为编码中是从 0 开始的, 所以 k 要减 1, 但是为了方便讨论下面的注释省略这个减 1 的说明)
        # 若 k == index, 即找到这个数
        if ((k - 1) == index):
            return arr[index]
        # 如果 k < index, 则从递归处理左边的子问题
        elif ((k - 1) < index):
            return quick_select(k, arr, start, index - 1)
        # 如果 k > index, 则从递归处理右边的子问题
        else:
            return quick_select(k, arr, index + 1, end)
    else:
        return -1

# ======================== 单元测试 ================================


class TestCaseQuickSelect(unittest.TestCase):

    def setUp(self):
        self.data_arr = [78, 4, 31, 12, 1]
        self.data_arr_start = 0
        self.data_arr_end = 4

        self.data_k_1 = 1
        self.data_k_2 = 2
        self.data_k_3 = 3
        self.data_k_4 = 4
        self.data_k_5 = 5
        self.data_k_6 = 6

        self.result_1 = 1
        self.result_2 = 4
        self.result_3 = 12
        self.result_4 = 31
        self.result_5 = 78
        self.result_6 = -1

    def test_quick_select(self):
        self.assertEqual(quick_select(self.data_k_1, self.data_arr,
                                      self.data_arr_start, self.data_arr_end),
                         self.result_1)

        self.assertEqual(quick_select(self.data_k_2, self.data_arr,
                                      self.data_arr_start, self.data_arr_end),
                         self.result_2)

        self.assertEqual(quick_select(self.data_k_3, self.data_arr,
                                      self.data_arr_start, self.data_arr_end),
                         self.result_3)

        self.assertEqual(quick_select(self.data_k_4, self.data_arr,
                                      self.data_arr_start, self.data_arr_end),
                         self.result_4)

        self.assertEqual(quick_select(self.data_k_5, self.data_arr,
                                      self.data_arr_start, self.data_arr_end),
                         self.result_5)

        self.assertEqual(quick_select(self.data_k_6, self.data_arr,
                                      self.data_arr_start, self.data_arr_end),
                         self.result_6)


if __name__ == '__main__':
    unittest.main()
