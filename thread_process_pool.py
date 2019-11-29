#!/usr/bin/env python
# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, as_completed,wait,ALL_COMPLETED
import threading
import time

# 参数times用来模拟网络请求的时间
def get_html(times, func):
    time.sleep(times)
    print("func: {0} get page {1} s finished".format(func, times))
    return times

time_list = [2,3,4,2,1,6,4,5,1]
executor = ThreadPoolExecutor(max_workers=10)
# 通过submit函数提交执行的函数到线程池中，submit函数立即返回，不阻塞
a = time.time()
task_list = [executor.submit(get_html, i, 'submit') for i in time_list]
wait(task_list)
print(int(time.time()-a), 12123)

a = time.time()
task_list = [executor.submit(get_html, i, 'submit') for i in time_list]
for task in as_completed(task_list):
    task.done()
print(int(time.time()-a), 12123)

# a = time.time()
# task_list2 = []
# for i in time_list:
#     t = threading.Thread(target=get_html, args=(i,'join'))
#     t.start()
#     task_list2.append(t)
#     if len(task_list2) >= 4:
#         for t in task_list2:
#             t.join()
#         task_list2 = []
# for t in task_list2:
#     t.join()
#
# print(int(time.time()-a), 12123)

# --------------------------------------------

