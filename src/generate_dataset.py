from pathlib import Path
import csv
import random
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'processed' / 'algorithm_samples.csv'

TEMPLATES = {
    'binary_search': [
        '''def find_value(values, target):
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1''',
        '''def locate(items, key):
    left = 0
    right = len(items)
    while left < right:
        mid = (left + right) // 2
        if items[mid] < key:
            left = mid + 1
        else:
            right = mid
    if left < len(items) and items[left] == key:
        return left
    return None''',
        '''def search(nums, wanted):
    start, end = 0, len(nums) - 1
    while start <= end:
        pivot = start + (end - start) // 2
        current = nums[pivot]
        if current == wanted:
            return pivot
        elif current > wanted:
            end = pivot - 1
        else:
            start = pivot + 1
    return -1''',
        '''def recursive_find(array, value, lo, hi):
    if lo > hi:
        return -1
    center = (lo + hi) // 2
    if array[center] == value:
        return center
    if value < array[center]:
        return recursive_find(array, value, lo, center - 1)
    return recursive_find(array, value, center + 1, hi)''',
        '''def lower_bound(data, x):
    a, b = 0, len(data)
    while a < b:
        m = (a + b) // 2
        if data[m] >= x:
            b = m
        else:
            a = m + 1
    return a''',
        '''def contains(sorted_data, needle):
    first = 0
    last = len(sorted_data) - 1
    while first <= last:
        guess = (first + last) // 2
        if needle == sorted_data[guess]:
            return True
        elif needle < sorted_data[guess]:
            last = guess - 1
        else:
            first = guess + 1
    return False''',
        '''def bisect_index(seq, item):
    lo = 0
    hi = len(seq)
    while lo < hi:
        mid = (lo + hi) // 2
        if seq[mid] < item:
            lo = mid + 1
        else:
            hi = mid
    return lo''',
        '''def lookup(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) >> 1
        if arr[mid] > target:
            high = mid - 1
        elif arr[mid] < target:
            low = mid + 1
        else:
            return mid
    return None''',
    ],
    'linear_search': [
        '''def find_value(values, target):
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1''',
        '''def locate(items, key):
    position = 0
    while position < len(items):
        if items[position] == key:
            return position
        position += 1
    return None''',
        '''def search(nums, wanted):
    for i in range(len(nums)):
        if nums[i] == wanted:
            return i
    return -1''',
        '''def contains(data, item):
    found = False
    for element in data:
        if element == item:
            found = True
            break
    return found''',
        '''def first_match(sequence, query):
    matches = [i for i, current in enumerate(sequence) if current == query]
    if matches:
        return matches[0]
    return -1''',
        '''def lookup(arr, target):
    index = 0
    while index != len(arr):
        current = arr[index]
        if current == target:
            return index
        index = index + 1
    return -1''',
        '''def scan(values, wanted):
    for position, candidate in enumerate(values):
        if candidate is wanted or candidate == wanted:
            return position
    return None''',
        '''def index_of(seq, value):
    for offset in range(0, len(seq)):
        candidate = seq[offset]
        if candidate == value:
            return offset
    return -1''',
    ],
    'bubble_sort': [
        '''def sort_values(values):
    result = list(values)
    for end in range(len(result) - 1, 0, -1):
        for index in range(end):
            if result[index] > result[index + 1]:
                result[index], result[index + 1] = result[index + 1], result[index]
    return result''',
        '''def order(items):
    data = items[:]
    changed = True
    while changed:
        changed = False
        for j in range(len(data) - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                changed = True
    return data''',
        '''def ascending(nums):
    arr = list(nums)
    n = len(arr)
    for pass_num in range(n):
        for k in range(0, n - pass_num - 1):
            if arr[k] > arr[k + 1]:
                temp = arr[k]
                arr[k] = arr[k + 1]
                arr[k + 1] = temp
    return arr''',
        '''def sort_list(seq):
    output = seq.copy()
    for i in range(len(output)):
        for j in range(0, len(output) - i - 1):
            left = output[j]
            right = output[j + 1]
            if left > right:
                output[j], output[j + 1] = right, left
    return output''',
        '''def bubble(data):
    a = data.copy()
    for i in range(len(a) - 1, 0, -1):
        swapped = False
        for j in range(i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a''',
        '''def arrange(numbers):
    result = numbers[:]
    size = len(result)
    for i in range(size):
        for j in range(size - 1):
            if result[j] > result[j + 1]:
                result[j + 1], result[j] = result[j], result[j + 1]
    return result''',
        '''def sort_array(array):
    values = array.copy()
    for outer in range(len(values)):
        for inner in range(len(values) - outer - 1):
            if values[inner] > values[inner + 1]:
                values[inner], values[inner + 1] = values[inner + 1], values[inner]
    return values''',
        '''def bubble_order(seq):
    copy = list(seq)
    n = len(copy)
    while n > 1:
        new_n = 0
        for i in range(1, n):
            if copy[i - 1] > copy[i]:
                copy[i - 1], copy[i] = copy[i], copy[i - 1]
                new_n = i
        n = new_n
    return copy''',
    ],
    'insertion_sort': [
        '''def sort_values(values):
    result = list(values)
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        while j >= 0 and result[j] > current:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result''',
        '''def order(items):
    data = items[:]
    for position in range(1, len(data)):
        key = data[position]
        cursor = position
        while cursor > 0 and data[cursor - 1] > key:
            data[cursor] = data[cursor - 1]
            cursor -= 1
        data[cursor] = key
    return data''',
        '''def ascending(nums):
    arr = list(nums)
    for i in range(1, len(arr)):
        j = i
        while j > 0:
            if arr[j] < arr[j - 1]:
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
                j -= 1
            else:
                break
    return arr''',
        '''def sort_list(seq):
    output = seq.copy()
    for index, value in enumerate(output):
        scan = index
        while scan > 0 and output[scan - 1] > value:
            output[scan] = output[scan - 1]
            scan -= 1
        output[scan] = value
    return output''',
        '''def insertion(data):
    a = data.copy()
    for i in range(1, len(a)):
        item = a[i]
        k = i - 1
        while k >= 0 and a[k] > item:
            a[k + 1] = a[k]
            k = k - 1
        a[k + 1] = item
    return a''',
        '''def arrange(numbers):
    result = numbers[:]
    for i in range(1, len(result)):
        selected = result.pop(i)
        j = i - 1
        while j >= 0 and result[j] > selected:
            j -= 1
        result.insert(j + 1, selected)
    return result''',
        '''def sort_array(array):
    values = array.copy()
    for step in range(1, len(values)):
        value = values[step]
        pos = step - 1
        while pos >= 0 and values[pos] > value:
            values[pos + 1] = values[pos]
            pos -= 1
        values[pos + 1] = value
    return values''',
        '''def insertion_order(seq):
    copy = list(seq)
    index = 1
    while index < len(copy):
        candidate = copy[index]
        place = index
        while place and candidate < copy[place - 1]:
            copy[place] = copy[place - 1]
            place -= 1
        copy[place] = candidate
        index += 1
    return copy''',
    ],
    'quick_sort': [
        '''def sort_values(values):
    if len(values) <= 1:
        return values
    pivot = values[len(values) // 2]
    smaller = [x for x in values if x < pivot]
    equal = [x for x in values if x == pivot]
    larger = [x for x in values if x > pivot]
    return sort_values(smaller) + equal + sort_values(larger)''',
        '''def quicksort(items):
    if len(items) < 2:
        return items
    pivot = items[0]
    left = [v for v in items[1:] if v <= pivot]
    right = [v for v in items[1:] if v > pivot]
    return quicksort(left) + [pivot] + quicksort(right)''',
        '''def order(data):
    arr = data[:]
    def partition(lo, hi):
        pivot = arr[hi]
        boundary = lo
        for current in range(lo, hi):
            if arr[current] <= pivot:
                arr[boundary], arr[current] = arr[current], arr[boundary]
                boundary += 1
        arr[boundary], arr[hi] = arr[hi], arr[boundary]
        return boundary
    def sort(lo, hi):
        if lo < hi:
            p = partition(lo, hi)
            sort(lo, p - 1)
            sort(p + 1, hi)
    sort(0, len(arr) - 1)
    return arr''',
        '''def ascending(nums):
    if not nums:
        return []
    pivot = nums[-1]
    low = [n for n in nums[:-1] if n < pivot]
    high = [n for n in nums[:-1] if n >= pivot]
    return ascending(low) + [pivot] + ascending(high)''',
        '''def sort_list(seq):
    if len(seq) <= 1:
        return list(seq)
    pivot = seq[0]
    before, after = [], []
    for value in seq[1:]:
        if value < pivot:
            before.append(value)
        else:
            after.append(value)
    return sort_list(before) + [pivot] + sort_list(after)''',
        '''def quick(data):
    result = list(data)
    def divide(start, end):
        if start >= end:
            return
        pivot = result[end]
        i = start
        for j in range(start, end):
            if result[j] < pivot:
                result[i], result[j] = result[j], result[i]
                i += 1
        result[i], result[end] = result[end], result[i]
        divide(start, i - 1)
        divide(i + 1, end)
    divide(0, len(result) - 1)
    return result''',
        '''def arrange(numbers):
    if len(numbers) <= 1:
        return numbers
    pivot = numbers[len(numbers) // 2]
    left = [x for x in numbers if x < pivot]
    middle = [x for x in numbers if x == pivot]
    right = [x for x in numbers if x > pivot]
    return arrange(left) + middle + arrange(right)''',
        '''def sort_array(array):
    if len(array) <= 1:
        return array
    pivot = array[0]
    lower = list(filter(lambda x: x < pivot, array[1:]))
    upper = list(filter(lambda x: x >= pivot, array[1:]))
    return sort_array(lower) + [pivot] + sort_array(upper)''',
    ],
    'merge_sort': [
        '''def sort_values(values):
    if len(values) <= 1:
        return values
    middle = len(values) // 2
    left = sort_values(values[:middle])
    right = sort_values(values[middle:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]''',
        '''def order(items):
    if len(items) < 2:
        return items
    mid = len(items) // 2
    a = order(items[:mid])
    b = order(items[mid:])
    output = []
    while a and b:
        if a[0] < b[0]:
            output.append(a.pop(0))
        else:
            output.append(b.pop(0))
    return output + a + b''',
        '''def ascending(nums):
    arr = list(nums)
    if len(arr) <= 1:
        return arr
    half = len(arr) // 2
    first = ascending(arr[:half])
    second = ascending(arr[half:])
    return combine(first, second)

def combine(x, y):
    merged = []
    while len(x) > 0 and len(y) > 0:
        if x[0] <= y[0]:
            merged += [x.pop(0)]
        else:
            merged += [y.pop(0)]
    merged.extend(x)
    merged.extend(y)
    return merged''',
        '''def sort_list(seq):
    if len(seq) <= 1:
        return list(seq)
    center = len(seq) // 2
    left = sort_list(seq[:center])
    right = sort_list(seq[center:])
    merged = []
    while left or right:
        if not right or (left and left[0] <= right[0]):
            merged.append(left.pop(0))
        else:
            merged.append(right.pop(0))
    return merged''',
        '''def merge_sort(data):
    if len(data) <= 1:
        return data
    midpoint = len(data) // 2
    part1 = merge_sort(data[:midpoint])
    part2 = merge_sort(data[midpoint:])
    result = []
    while part1 and part2:
        smallest = part1.pop(0) if part1[0] < part2[0] else part2.pop(0)
        result.append(smallest)
    return result + part1 + part2''',
        '''def arrange(values):
    if len(values) == 1 or not values:
        return values
    split = len(values) // 2
    a = arrange(values[:split])
    b = arrange(values[split:])
    merged = []
    while a and b:
        chosen = a.pop(0) if a[0] <= b[0] else b.pop(0)
        merged.append(chosen)
    return merged + a + b''',
        '''def sort_array(array):
    if len(array) < 2:
        return array
    mid = len(array) // 2
    left_half = sort_array(array[:mid])
    right_half = sort_array(array[mid:])
    i = j = 0
    answer = []
    while i < len(left_half) and j < len(right_half):
        if left_half[i] < right_half[j]:
            answer.append(left_half[i]); i += 1
        else:
            answer.append(right_half[j]); j += 1
    answer.extend(left_half[i:])
    answer.extend(right_half[j:])
    return answer''',
        '''def merge_order(seq):
    if len(seq) <= 1:
        return seq[:]
    mid = len(seq) // 2
    one = merge_order(seq[:mid])
    two = merge_order(seq[mid:])
    result = []
    while one and two:
        result.append(one.pop(0) if one[0] <= two[0] else two.pop(0))
    result.extend(one or two)
    return result''',
    ],
}

RENAMES = [
    {'values':'numbers', 'target':'wanted', 'items':'records', 'key':'needle', 'nums':'data', 'arr':'sequence', 'result':'output', 'items':'elements'},
    {'values':'sequence', 'target':'query', 'items':'values', 'key':'wanted', 'nums':'numbers', 'arr':'items', 'result':'sorted_items', 'items':'records'},
    {'values':'data', 'target':'search_for', 'items':'collection', 'key':'value', 'nums':'entries', 'arr':'values', 'result':'answer', 'items':'collection'},
    {'values':'source', 'target':'goal', 'items':'source', 'key':'query', 'nums':'source', 'arr':'source', 'result':'ordered', 'items':'source'},
]


def variant(code, seed):
    mapping = RENAMES[seed % len(RENAMES)]
    out = code
    for old, new in mapping.items():
        out = re.sub(r'\b' + re.escape(old) + r'\b', new, out)
    if seed % 2:
        out = out.replace('    ', '  ')
    if seed % 3 == 0:
        out = '\n'.join(line.rstrip() for line in out.splitlines())
    return out


def main():
    rows = []
    for label, templates in TEMPLATES.items():
        for template_id, code in enumerate(templates):
            for variant_id in range(5):
                rows.append({
                    'code': variant(code, variant_id),
                    'label': label,
                    'template_group': f'{label}_{template_id}',
                    'source_type': 'original_controlled_example',
                    'source': 'Created specifically for AlgoLens; not copied from an external repository',
                })
    random.Random(42).shuffle(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} examples to {OUT}')
    for label in TEMPLATES:
        print(label, sum(row['label'] == label for row in rows))

if __name__ == '__main__':
    main()
