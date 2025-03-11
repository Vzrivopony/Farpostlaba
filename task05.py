"""
Given a list of integers numbers "nums".

You need to find a sub-array with length less equal to "k", with maximal sum.

The written function should return the sum of this sub-array.

Examples:
    nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
    result = 16
"""
from typing import List

def find_maximal_subarray_sum(nums: List[int], k: int) -> int:
    max_sum = float('-inf')
    #»щем окна
    for i in range(1,k+1):
        window_sum = sum(nums[:i]) 
        max_sum = max(max_sum, window_sum) 

        #»спользуем окна
        for j in range(1, len(nums)-i+1):
            window_sum = window_sum - nums[j-1] + nums[j+i-1]
            max_sum = max(max_sum, window_sum) 
    return max_sum

print(find_maximal_subarray_sum([1, 3, -1, -3, 5, 3, 6, 7], 3))  # 16