# -*- encoding: utf-8 -*-
# !/usr/bin/env python

'''
基于python实现的单向链表操作
'''

__author__ = 'billy'

class Node(object):

    def __init__(self, value, next=None):
        self.value = value
        self.next = next

    def __repr__(self):
        return str(self.value)

class SingleLinkList(object):

    def __init__(self):
        self.length = 0
        self.head = None

    def init_links(self, list_data):
        # 创建头结点
        self.length = len(list_data)
        self.head = Node(list_data[0])
        p = self.head
        for data in list_data[1:]:
            p.next = Node(data)
            p = p.next
        print self.head.value, 465

    def _head(self):
        return self.head

    def is_empty(self):
        return self.head.next == 0

    def getlength(self):
        if self.is_empty():
            return None
        length = 0
        p = self.head
        while p:
            length += 1
            p = p.next
        return length


    def show_links(self):
        if self.getlength() == 0:
            return None
        p = self.head
        while p:
            print p.value
            p = p.next

    def insert(self, value, index):
        if self.is_empty():
            return None
        if index < 0 or index > self.getlength() - 1:
            if self.getlength() == index:
                # 调用 append 操作
                self.append(value)
            else:
                p = self.head
                pre = p
                i = 0
                while i <= index:
                    p = p.next
                    i += 1
                    pre = p
                node = Node(value)
                pre.next = Node(value)
                node.next = p
                self.length += 1

    def append(self, value):
        if self.getlength() == 0:
            return None
        p = self.head
        while p:
            p = p.next
        p.next = Node(value)
        self.length += 1

    def delect(self, index):
        if self.is_empty():
            return None
        if index < 0 or index > self.getlength() - 1:
            return 'index error'
        if index == 0:
            self.head = self.head.next
        p = self.head
        i = 0
        while i <= index:
            p = p.next
            i += 1
        p.next = None

    def get_data(self, index):
        if  index < 0 or index > self.length:
            return 'index error'
        p = self.head
        i = 0
        while i < index:
            p = p.next
            i += 1
        return p.value



if __name__ == '__main__':
    pass
    # a = [i for i in range(10, 50, 3)]
    # link = Linklist()
    # link.init_links(a)
    # print link.getlength()
    # print link.show_links()
