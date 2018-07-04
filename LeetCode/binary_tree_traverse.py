# -*- coding:utf-8 -*-

import unittest
from collections import deque


# ======================== 算法实现 ================================
# 
# 单元测试中的二叉树样子看这里：https://raw.githubusercontent.com/hsxhr-10/picture/master/一颗二叉搜索树.png


class BinarySearchTree():
    """
    定义二叉树结构
    """
    def __init__(self, value, light=None, right=None):
        # 值
        self.value = value
        # 左子树
        self.light = light
        # 右子树
        self.right = right


class BinarySearchTreeForLoops():
    """
    定义用于非递归遍历的结构
    """
    def __init__(self, BinarySearchTree, visited):
        # 二叉树结构
        self.BinarySearchTree = BinarySearchTree
        # 访问标记
        self.visited = visited


def create_binary_search_tree(root, value):
    """
    创建二叉搜索树
    """
    # 递归结束条件
    # root 为 None 代表本次递归结束, 创建并返回节点, 递归结束会返回上层调用处, 就可以对相应的子树进行赋值, 即对应下面两个递归语句的处理
    # 这个递归过程同样可以利用最小二叉树模型思考
    if (root == None):
        return BinarySearchTree(value)
    # 递归创建左子树
    elif (value < root.value):
        root.light = create_binary_search_tree(root.light, value)
    # 递归创建右子树
    else:
        root.right = create_binary_search_tree(root.right, value)

    # 返回树根
    return root


def preorder_by_redursion(root, result):
    """
    前序遍历 (递归版)
    result 收集遍历结果, 方便单元测试断言
    """

    # 递归结束条件
    if root is None:
        return

    result.append(root.value)
    print(root.value)

    # 递归遍历左右子树
    preorder_by_redursion(root.light, result)
    preorder_by_redursion(root.right, result)

    return result


def preorder_by_loops(root, result):
    """
    前序遍历 (非递归版)
    """
    # 初始化栈
    stack = []
    # 初始化访问标记
    visited = False
    # 根结点入栈
    stack.append(BinarySearchTreeForLoops(root, False))

    # 大循环条件栈非空
    while (stack):
        # 出栈
        top_item = stack.pop()
        # 栈顶节点
        root = top_item.BinarySearchTree
        # 栈顶节点的访问标记
        visited = top_item.visited

        # 如果栈顶节点为空节点, 结束本次循环 (优化后无需该条件判断)
        if (root is None):
            continue
        # 栈顶节点为 True 则访问
        if (visited):
            result.append(root.value)
            print(root.value)
        # 否则就进行入栈操作
        else:
            # 以最小二叉树为参考写出以下的入栈方式: 右子树 --> 左子树 --> 根
            # 此处可以优化, 当 root.light 或 root.right 为空时，无需入栈, 减少大循环次数
            stack.append(BinarySearchTreeForLoops(root.right, False))
            stack.append(BinarySearchTreeForLoops(root.light, False))
            stack.append(BinarySearchTreeForLoops(root, True))

    return result


def inorder_by_redursion(root, result):
    """
    中序遍历 (递归版)
    """
    # 递归结束条件
    if root is None:
        return

    # 递归遍历左右子树
    inorder_by_redursion(root.light, result)

    result.append(root.value)
    print(root.value)

    inorder_by_redursion(root.right, result)

    return result


def inorder_by_loops(root, result):
    """
    中序遍历 (非递归版)
    整体结构与前序、后序遍历都差不多, 区别是入栈操作不同
    """
    stack = []
    visited = False
    stack.append(BinarySearchTreeForLoops(root, False))

    while (stack):
        top_item = stack.pop()
        root = top_item.BinarySearchTree
        visited = top_item.visited

        if (root is None):
            continue
        if (visited):
            result.append(root.value)
            print(root.value)
        # 否则就进行入栈操作
        else:
            # 以最小二叉树为参考写出以下的入栈方式: 右子树 --> 根 --> 左子树
            # 此处可以优化, 当 root.light 或 root.right 为空时，无需入栈, 减少大循环次数
            stack.append(BinarySearchTreeForLoops(root.right, False))
            stack.append(BinarySearchTreeForLoops(root, True))
            stack.append(BinarySearchTreeForLoops(root.light, False))

    return result


def postorder_by_recursion(root, result):
    """
    后序遍历 (递归版)
    """
    # 递归结束条件
    if root is None:
        return

    # 递归遍历左右子树
    postorder_by_recursion(root.light, result)
    postorder_by_recursion(root.right, result)

    print(root.value)
    result.append(root.value)

    return result


def postorder_by_loops(root, result):
    """
    后序遍历 (非递归版)
    整体结构与前序、中序遍历都差不多, 区别是入栈操作不同
    """
    stack = []
    visited = False
    stack.append(BinarySearchTreeForLoops(root, False))

    while (stack):
        top_item = stack.pop()
        root = top_item.BinarySearchTree
        visited = top_item.visited

        if (root is None):
            continue
        if (visited):
            result.append(root.value)
            print(root.value)
        # 否则就进行入栈操作
        else:
            # 以最小二叉树为参考写出以下的入栈方式: 右子树 --> 根 --> 左子树
            # 此处可以优化, 当 root.light 或 root.right 为空时，无需入栈, 减少大循环次数
            stack.append(BinarySearchTreeForLoops(root, True))
            stack.append(BinarySearchTreeForLoops(root.right, False))
            stack.append(BinarySearchTreeForLoops(root.light, False))

    return result


def sequence(root, result):
    """
    层序遍历
    """
    # 初始化队列
    queue = deque([root])

    # 大循环条件队列非空
    while (queue):
        # 出队
        inode = queue.popleft()
        # 入队左右子树
        if (inode.light):
            queue.append(inode.light)
        if (inode.right):
            queue.append(inode.right)

        result.append(inode.value)
        print(inode.value)

    return result



# ======================== 单元测试 ================================


class TestCaseBinaryTreeTraverse(unittest.TestCase):
    
    def setUp(self):
        # 初始化根节点
        self.root = create_binary_search_tree(None, 10)

        # 创建子节点
        arr = [6, 14, 4, 8, 12, 16]
        for item in arr:
            self.root = create_binary_search_tree(self.root, item)    

        # 各种遍历结果
        self.result_preorder = [10, 6, 4, 8, 14, 12, 16]
        self.result_inorder = [4, 6, 8, 10, 12, 14, 16]
        self.result_postorder = [4, 8, 6, 12, 16, 14, 10]
        self.result_sequence = [10, 6, 14, 4, 8, 12, 16]

    def test_preorder_by_recursion(self):
        self.assertEqual(preorder_by_redursion(self.root, []), self.result_preorder)

    def test_preorder_by_loops(self):
        self.assertEqual(preorder_by_loops(self.root, []), self.result_preorder)

    def test_inorder_by_redursion(self):
        self.assertEqual(inorder_by_redursion(self.root, []), self.result_inorder)

    def test_inorder_by_loops(self):
        self.assertEqual(inorder_by_loops(self.root, []), self.result_inorder)

    def test_postorder_by_recursion(self):
        self.assertEqual(postorder_by_recursion(self.root, []), self.result_postorder)

    def test_postorder_by_loops(self):
        self.assertEqual(postorder_by_loops(self.root, []), self.result_postorder)

    def test_sequence(self):
        self.assertEqual(sequence(self.root, []), self.result_sequence)


if __name__ == '__main__':
    unittest.main()
