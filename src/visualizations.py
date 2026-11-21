import matplotlib.pyplot as plt

COMPLEXITY = {
    'binary_search': ('O(log n)', 'O(1)', 'Best: O(1) · Average/Worst: O(log n)', 'The search interval is halved after each comparison. The input must already be sorted.'),
    'linear_search': ('O(1)', 'O(1)', 'Best: O(1) · Average/Worst: O(n)', 'The algorithm may find the target immediately, but in the worst case it checks every item.'),
    'bubble_sort': ('O(n²)', 'O(1)', 'Best/Average/Worst: O(n²) in this implementation', 'This version always completes its nested passes and does not use an early-stop flag, so even already-sorted input has quadratic comparisons.'),
    'insertion_sort': ('O(n²)', 'O(1)', 'Best: O(n) · Average/Worst: O(n²)', 'Already sorted input needs very little shifting; reverse-sorted input requires many shifts.'),
    'quick_sort': ('O(n log n) average', 'O(log n) average recursion', 'Best/Average: O(n log n) · Worst: O(n²)', 'Balanced partitions produce shallow recursion. Repeatedly unbalanced partitions create the quadratic worst case.'),
    'merge_sort': ('O(n log n)', 'O(n)', 'Best/Average/Worst: O(n log n)', 'The list is divided into halves at each level, then merged. There are about log₂(n) levels and n work per level.'),
}

ALGORITHM_CODE = {
    'binary_search': [
        'low, high = 0, len(values) - 1',
        'while low <= high:',
        '    mid = (low + high) // 2',
        '    if values[mid] == target:',
        '        return mid',
        '    elif values[mid] < target:',
        '        low = mid + 1',
        '    else:',
        '        high = mid - 1',
        'return -1',
    ],
    'linear_search': [
        'for index, value in enumerate(values):',
        '    if value == target:',
        '        return index',
        'return -1',
    ],
    'bubble_sort': [
        'for end in range(len(values) - 1, 0, -1):',
        '    for index in range(end):',
        '        if values[index] > values[index + 1]:',
        '            values[index], values[index + 1] = values[index + 1], values[index]',
        'return values',
    ],
    'insertion_sort': [
        'for index in range(1, len(values)):',
        '    current = values[index]',
        '    position = index - 1',
        '    while position >= 0 and values[position] > current:',
        '        values[position + 1] = values[position]',
        '        position -= 1',
        '    values[position + 1] = current',
        'return values',
    ],
    'quick_sort': [
        'if len(values) <= 1:',
        '    return values',
        'pivot = values[-1]',
        'left = [x for x in values[:-1] if x <= pivot]',
        'right = [x for x in values[:-1] if x > pivot]',
        'return quick_sort(left) + [pivot] + quick_sort(right)',
    ],
    'merge_sort': [
        'if len(values) <= 1:',
        '    return values',
        'middle = len(values) // 2',
        'left = merge_sort(values[:middle])',
        'right = merge_sort(values[middle:])',
        'return merge(left, right)',
    ],
}

LINE_MEANINGS = {
    'binary_search': ['Set the first and last positions of the search range.', 'Continue while the range still contains items.', 'Inspect the middle position of the current range.', 'Check whether the middle value is the target.', 'Return the position when the target is found.', 'If the middle value is too small, keep the right half.', 'Discard the left half by moving the lower boundary.', 'Otherwise, the middle value is too large.', 'Discard the right half by moving the upper boundary.', 'The target is not present in the list.'],
    'linear_search': ['Visit each item in order, starting at the beginning.', 'Compare the current value with the target.', 'Return the current position when the values match.', 'No item matched the target.'],
    'bubble_sort': ['Start a pass over the unsorted portion.', 'Compare neighboring positions from left to right.', 'Check whether this adjacent pair is out of order.', 'Swap the pair so the larger value moves right. Then continue the pass.', 'Return the sorted list.'],
    'insertion_sort': ['Take each item after the first as the next item to insert.', 'Remember the value being inserted into the sorted section.', 'Start comparing with the item immediately to its left.', 'Continue while earlier values are larger than the value being inserted.', 'Shift a larger value one position to the right.', 'Move one position farther left.', 'Place the current value into the open position.', 'Return the sorted list.'],
    'quick_sort': ['A list with zero or one item is already sorted.', 'Return the small list unchanged.', 'Choose the final value as this partition’s pivot.', 'Collect values no larger than the pivot.', 'Collect values larger than the pivot.', 'Sort both partitions recursively and place the pivot between them.'],
    'merge_sort': ['A list with zero or one item is already sorted.', 'Return the small list unchanged.', 'Find the midpoint to split the list.', 'Recursively sort the left half.', 'Recursively sort the right half.', 'Merge the two sorted halves into one sorted list.'],
}


def _event(values, active=(), compare=(), swapped=(), pivot=None, line=0, action='', explanation='', snapshot=None, depth=0):
    return {
        'values': list(values if snapshot is None else snapshot),
        'active': list(active), 'compare': list(compare), 'swapped': list(swapped),
        'pivot': pivot, 'line': line, 'action': action, 'explanation': explanation,
        'depth': depth,
    }


def sorting_trace(algorithm, values):
    a = list(values)
    events = [_event(a, line=0, action='Start', explanation='Begin with the input list. No values have been changed.')]
    if algorithm == 'bubble_sort':
        for end in range(len(a) - 1, 0, -1):
            for i in range(end):
                events.append(_event(a, compare=(i, i + 1), line=2, action='Compare neighbors', explanation=f'Compare {a[i]} and {a[i+1]}.'))
                if a[i] > a[i + 1]:
                    a[i], a[i + 1] = a[i + 1], a[i]
                    events.append(_event(a, swapped=(i, i + 1), line=3, action='Swap', explanation='The pair was out of order, so the larger value moves one position to the right.'))
        events.append(_event(a, active=range(len(a)), line=4, action='Complete', explanation='Every pass is complete; the list is sorted.'))
    elif algorithm == 'insertion_sort':
        for i in range(1, len(a)):
            current = a[i]
            events.append(_event(a, active=(i,), line=1, action='Select next value', explanation=f'Select {current}; the section to its left is already sorted.'))
            j = i - 1
            while j >= 0:
                events.append(_event(a, compare=(j, i), line=3, action='Compare', explanation=f'Compare {a[j]} with the selected value {current}.'))
                if a[j] <= current:
                    break
                a[j + 1] = a[j]
                events.append(_event(a, active=(j + 1,), swapped=(j, j + 1), line=4, action='Shift right', explanation=f'{a[j]} is larger than {current}, so shift it one position right.'))
                j -= 1
            a[j + 1] = current
            events.append(_event(a, active=(j + 1,), line=6, action='Insert value', explanation=f'Place {current} into its correct position in the sorted section.'))
        events.append(_event(a, active=range(len(a)), line=7, action='Complete', explanation='Every value has been inserted into the sorted section.'))
    elif algorithm == 'quick_sort':
        def quick(lo, hi, depth):
            if lo > hi:
                return
            if lo == hi:
                events.append(_event(a, active=(lo,), line=0, action='Base case', explanation=f'{a[lo]} is alone, so this partition is already sorted.', depth=depth))
                return
            pivot_index = hi
            pivot = a[pivot_index]
            events.append(_event(a, active=(pivot_index,), pivot=pivot_index, line=2, action='Choose pivot', explanation=f'Choose {pivot} as the pivot for this section.', depth=depth))
            left = [x for x in a[lo:hi] if x <= pivot]
            right = [x for x in a[lo:hi] if x > pivot]
            events.append(_event(a, compare=range(lo, hi), pivot=pivot_index, line=3, action='Partition left', explanation=f'Values no larger than {pivot} belong in the left partition.', depth=depth))
            events.append(_event(a, compare=range(lo, hi), pivot=pivot_index, line=4, action='Partition right', explanation=f'Values larger than {pivot} belong in the right partition.', depth=depth))
            ordered = left + [pivot] + right
            a[lo:hi + 1] = ordered
            p = lo + len(left)
            events.append(_event(a, active=range(lo, hi + 1), pivot=p, line=5, action='Place pivot', explanation=f'{pivot} is now between the smaller and larger values.', depth=depth))
            quick(lo, p - 1, depth + 1)
            quick(p + 1, hi, depth + 1)
        if a:
            quick(0, len(a) - 1, 0)
        events.append(_event(a, active=range(len(a)), line=5, action='Complete', explanation='All partitions are sorted; the full list is in ascending order.'))
    elif algorithm == 'merge_sort':
        def merge_sort(lo, hi, depth):
            if hi - lo <= 1:
                if hi > lo:
                    events.append(_event(a, active=(lo,), line=0, action='Base case', explanation=f'{a[lo]} is a one-item list and is already sorted.', depth=depth))
                return
            mid = (lo + hi) // 2
            events.append(_event(a, active=range(lo, hi), line=2, action='Divide', explanation=f'Split this section into positions {lo}–{mid-1} and {mid}–{hi-1}.', depth=depth))
            merge_sort(lo, mid, depth + 1)
            merge_sort(mid, hi, depth + 1)
            left, right = a[lo:mid], a[mid:hi]
            events.append(_event(a, active=range(lo, mid), compare=range(mid, hi), line=3, action='Prepare left half', explanation='The left half is sorted and ready to merge.', depth=depth))
            events.append(_event(a, active=range(mid, hi), compare=range(lo, mid), line=4, action='Prepare right half', explanation='The right half is sorted and ready to merge.', depth=depth))
            merged = []
            i = j = 0
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    merged.append(left[i]); i += 1
                else:
                    merged.append(right[j]); j += 1
            merged.extend(left[i:]); merged.extend(right[j:])
            a[lo:hi] = merged
            events.append(_event(a, active=range(lo, hi), line=5, action='Merge', explanation=f'Merge the two sorted halves into {merged}.', depth=depth))
        merge_sort(0, len(a), 0)
        events.append(_event(a, active=range(len(a)), line=5, action='Complete', explanation='Every section has been merged; the list is sorted.'))
    return events


def _search_event_trace(algorithm, values, target):
    events = [_event(values, line=0, action='Start', explanation='Begin searching the input list.')]
    if algorithm == 'linear_search':
        for i, value in enumerate(values):
            events.append(_event(values, active=(i,), compare=(i,), line=1, action='Check item', explanation=f'Compare index {i}, value {value}, with target {target}.'))
            if value == target:
                events.append(_event(values, active=(i,), line=2, action='Found', explanation=f'The target {target} is at index {i}.'))
                return events
        events.append(_event(values, line=3, action='Not found', explanation=f'The target {target} does not appear in the list.'))
    else:
        lo, hi = 0, len(values) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            events.append(_event(values, active=(mid,), compare=(mid,), line=2, action='Inspect middle', explanation=f'Check the middle value {values[mid]} at index {mid}. Search range: indices {lo} through {hi}.'))
            if values[mid] == target:
                events.append(_event(values, active=(mid,), line=4, action='Found', explanation=f'The target {target} is at index {mid}.'))
                return events
            if values[mid] < target:
                lo = mid + 1
                events.append(_event(values, active=range(lo, hi + 1), line=6, action='Discard left half', explanation=f'{values[mid]} is smaller than {target}; continue to the right.'))
            else:
                hi = mid - 1
                events.append(_event(values, active=range(lo, hi + 1), line=8, action='Discard right half', explanation=f'{values[mid]} is larger than {target}; continue to the left.'))
        events.append(_event(values, line=9, action='Not found', explanation=f'The target {target} is not in the sorted list.'))
    return events


def recursion_tree(algorithm, values):
    nodes = []
    edges = []
    counter = [0]
    def visit(items, parent=None, depth=0):
        node_id = counter[0]; counter[0] += 1
        if algorithm == 'quick_sort':
            pivot = items[-1] if items else None
            label = f'{items}\npivot: {pivot}' if len(items) > 1 else f'{items}\nbase case'
            left = [x for x in items[:-1] if x <= pivot] if len(items) > 1 else []
            right = [x for x in items[:-1] if x > pivot] if len(items) > 1 else []
            children = [left, right] if len(items) > 1 else []
        else:
            label = f'{items}\nbase case' if len(items) <= 1 else f'{items}\nsplit'
            middle = len(items) // 2
            children = [items[:middle], items[middle:]] if len(items) > 1 else []
        nodes.append({'id': node_id, 'label': label, 'depth': depth})
        if parent is not None:
            edges.append((parent, node_id))
        for child in children:
            visit(child, node_id, depth + 1)
        return node_id
    visit(list(values))
    return nodes, edges


def plot_array(event, title='Algorithm trace'):
    values = event['values']
    fig, ax = plt.subplots(figsize=(9, 3.6))
    colors = []
    for i in range(len(values)):
        if i == event.get('pivot'):
            colors.append('#D69E36')
        elif i in event.get('swapped', ()):
            colors.append('#D97757')
        elif i in event.get('compare', ()):
            colors.append('#5487B8')
        elif i in event.get('active', ()):
            colors.append('#4E927B')
        else:
            colors.append('#AAB7C4')
    bars = ax.bar(range(len(values)), values, color=colors, width=0.68, edgecolor='white', linewidth=1.2)
    ax.set_title(title, loc='left', fontsize=12, fontweight='bold', pad=14)
    ax.set_xlabel('Array index', labelpad=9)
    ax.set_ylabel('Value', labelpad=9)
    ax.set_xticks(range(len(values)))
    ax.set_axisbelow(True)
    ax.grid(axis='y', alpha=0.2)
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(value), ha='center', va='bottom', fontsize=9)
        role = 'pivot' if i == event.get('pivot') else 'swap' if i in event.get('swapped', ()) else 'compare' if i in event.get('compare', ()) else 'active' if i in event.get('active', ()) else ''
        if role:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values or [1]) * .09, role.upper(), ha='center', va='bottom', fontsize=7, fontweight='bold', color='#344252')
    if values:
        ax.set_ylim(0, max(values) * 1.22 if max(values) > 0 else 1)
    for spine in ('top', 'right', 'left'):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return fig


def trace_steps(algorithm, values):
    return [event['values'] for event in sorting_trace(algorithm, values)]


def search_events(algorithm, values, target):
    return _search_event_trace(algorithm, values, target)


def search_trace(algorithm, values, target):
    return [(event['active'][0] if event['active'] else -1, event['action'] == 'Found')
            for event in _search_event_trace(algorithm, values, target)
            if event['action'] in ('Check item', 'Inspect middle', 'Found')]
