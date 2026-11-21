from src.visualizations import COMPLEXITY, ALGORITHM_CODE, LINE_MEANINGS, sorting_trace, search_events, plot_array, recursion_tree
from src.predict import load_model, predict_code
from pathlib import Path
import sys
import html
import json
import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

CASE_COMPLEXITY = {
    'binary_search': ('O(1)', 'O(log n)', 'O(log n)'),
    'linear_search': ('O(1)', 'O(n)', 'O(n)'),
    'bubble_sort': ('O(n²)', 'O(n²)', 'O(n²)'),
    'insertion_sort': ('O(n)', 'O(n²)', 'O(n²)'),
    'quick_sort': ('O(n log n)', 'O(n log n)', 'O(n²)'),
    'merge_sort': ('O(n log n)', 'O(n log n)', 'O(n log n)'),
}

st.set_page_config(page_title='AlgoLens | Algorithm Studio',
                   page_icon='A', layout='wide', initial_sidebar_state='expanded')
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#202B36; --muted:#6B7785; --line:#E4E9EE; --paper:#F6F8FA; --green:#397C68; --blue:#557FA8; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:#F7F8FA; }
.block-container { max-width:1280px; padding-top:2rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.035em; color:#202B36; }
h1 { font-size:2.25rem !important; font-weight:800 !important; }
[data-testid="stSidebar"] { background:#EFF2F4; border-right:1px solid #E2E7EB; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2 { font-family:'Manrope',sans-serif; }
div[data-testid="stMetric"] { background:white; border:1px solid #E5E9ED; padding:16px 18px; border-radius:12px; }
.stButton>button { border-radius:9px; border:1px solid #DCE3E8; font-weight:600; min-height:2.55rem; }
.stButton>button[kind="primary"] { background:#397C68; border-color:#397C68; }
.stTextArea textarea, .stTextInput input, .stNumberInput input { border-radius:9px; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:14px; border-color:#E3E8EC; background:white; }
.algo-kicker { color:#397C68; text-transform:uppercase; font-size:.72rem; font-weight:700; letter-spacing:.12em; }
.algo-subtitle { color:#687583; font-size:1.02rem; margin-top:-.5rem; }
.algo-card { background:white; border:1px solid #E3E8EC; border-radius:14px; padding:18px 20px; }
.algo-step { font-size:.76rem; color:#687583; text-transform:uppercase; font-weight:700; letter-spacing:.1em; }
.code-line { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; white-space:pre; padding:5px 10px; border-radius:5px; font-size:.83rem; color:#344252; }
.code-line.active { background:#E6F1EC; border-left:3px solid #397C68; color:#1D493C; font-weight:700; }
.legend-dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }
.small-muted { color:#73808C; font-size:.82rem; }
</style>
''', unsafe_allow_html=True)


@st.cache_resource
def get_model():
    return load_model()


if 'recognized_algorithm' not in st.session_state:
    st.session_state.recognized_algorithm = None
if 'recognized_code' not in st.session_state:
    st.session_state.recognized_code = ''
if 'nav_page' not in st.session_state:
    st.session_state.nav_page = 'Recognize code'
if 'trace_step' not in st.session_state:
    st.session_state.trace_step = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'animation_interval' not in st.session_state:
    st.session_state.animation_interval = '1.6s'


def navigate_to_explore(label):
    st.session_state.nav_page = 'Explore algorithms'
    st.session_state.explore_algorithm = label
    st.session_state.trace_step = 0
    st.session_state.is_playing = False


def title_block(kicker, title, subtitle):
    st.markdown(
        f'<div class="algo-kicker">{kicker}</div><h1>{title}</h1><div class="algo-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def code_panel(lines, active_line, heading='Reference implementation'):
    st.markdown(f'**{heading}**')
    rendered = []
    for i, line in enumerate(lines):
        cls = 'code-line active' if i == active_line else 'code-line'
        rendered.append(
            f'<div class="{cls}"><span style="display:inline-block;width:25px;color:#93A0AC">{i+1:>2}</span>{html.escape(line)}</div>')
    st.markdown('<div style="background:#FBFCFD;border:1px solid #E5E9ED;border-radius:10px;padding:10px 8px;overflow-x:auto">' +
                ''.join(rendered) + '</div>', unsafe_allow_html=True)


def matching_source_line(code, algorithm, conceptual_line):
    source = code.splitlines()
    patterns = {
        'quick_sort': {2: ('pivot',), 3: ('< pivot', '<= pivot', 'if x <', 'if x <='), 4: ('>= pivot', '> pivot', 'if x >'), 5: ('return', 'quick_sort', 'f(lo)', 'merge')},
        'merge_sort': {2: ('mid', 'middle'), 3: ('left', '[:mid', '[:middle'), 4: ('right', '[mid:', '[middle:'), 5: ('merge', 'return')},
        'bubble_sort': {1: ('for',), 2: ('if', '>'), 3: ('swap', '],', '=')},
        'insertion_sort': {1: ('for',), 2: ('current', 'key'), 3: ('position', 'while'), 4: ('values[', 'arr['), 6: ('current', 'key')},
        'binary_search': {2: ('mid', 'middle'), 3: ('==',), 5: ('< target', '<'), 6: ('low',), 8: ('high',)},
        'linear_search': {0: ('for', 'enumerate'), 1: ('==',), 2: ('return',)},
    }
    options = patterns.get(algorithm, {}).get(conceptual_line, ())
    for i, line in enumerate(source):
        if any(token in line for token in options):
            return i
    return None


def draw_recursion_tree(algorithm, values):
    nodes, edges = recursion_tree(algorithm, values)
    if not nodes:
        return
    levels = {}
    for node in nodes:
        levels.setdefault(node['depth'], []).append(node)
    max_width = max(len(group) for group in levels.values())
    fig, ax = plt.subplots(figsize=(10, max(2.8, len(levels) * 1.15)))
    positions = {}
    for depth, group in levels.items():
        width = len(group)
        for index, node in enumerate(group):
            x = (index + 0.5) / width
            y = -depth
            positions[node['id']] = (x, y)
    for parent, child in edges:
        x1, y1 = positions[parent]
        x2, y2 = positions[child]
        ax.plot([x1, x2], [y1, y2], color='#C8D2D9', linewidth=1.5, zorder=1)
    for node in nodes:
        x, y = positions[node['id']]
        ax.text(x, y, node['label'], ha='center', va='center', fontsize=8,
                bbox=dict(boxstyle='round,pad=.55', facecolor='#EEF4F1' if node['depth'] else '#DDEBE5', edgecolor='#B7CEC3'), zorder=2)
    ax.set_xlim(0, 1)
    ax.set_ylim(-max(levels) - .7, .7)
    ax.axis('off')
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_trace(algorithm, values, target=None):
    if algorithm in ('binary_search', 'linear_search'):
        events = search_events(algorithm, values, int(target))
    else:
        events = sorting_trace(algorithm, values)
    if not events:
        st.info('No steps were generated for this input.')
        return
    if st.session_state.trace_step >= len(events):
        st.session_state.trace_step = len(events) - 1
    interval = st.session_state.animation_interval

    @st.fragment(run_every=interval if st.session_state.is_playing else None)
    def player():
        total = len(events)
        step = min(st.session_state.trace_step, total - 1)
        event = events[step]
        st.markdown(
            f'<div class="algo-card"><div class="algo-step">{event["action"]} · Step {step+1} of {total}</div><h3 style="margin:.35rem 0 .2rem">{html.escape(event["explanation"])}</h3><div class="small-muted">{html.escape(event["action"])} · Animation is deliberately paced so each operation is easy to follow.</div></div>', unsafe_allow_html=True)
        st.progress((step + 1) / total)
        fig = plot_array(event, f'Step {step+1} · {event["action"]}')
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.markdown('<div class="small-muted"><span class="legend-dot" style="background:#D69E36"></span>Pivot&nbsp;&nbsp; <span class="legend-dot" style="background:#5487B8"></span>Compared&nbsp;&nbsp; <span class="legend-dot" style="background:#D97757"></span>Swapped&nbsp;&nbsp; <span class="legend-dot" style="background:#4E927B"></span>Selected / active</div>', unsafe_allow_html=True)
        code_lines = ALGORITHM_CODE[algorithm]
        conceptual_line = min(max(event['line'], 0), len(code_lines)-1)
        code_panel(code_lines, conceptual_line, 'Step-by-step reference code')
        st.caption(LINE_MEANINGS[algorithm][conceptual_line] if conceptual_line < len(
            LINE_MEANINGS[algorithm]) else event['explanation'])
        if st.session_state.recognized_code and st.session_state.recognized_algorithm == algorithm:
            source_line = matching_source_line(
                st.session_state.recognized_code, algorithm, conceptual_line)
            with st.expander('Relate this step to the code you submitted'):
                if source_line is not None:
                    st.markdown(
                        f'Your submitted code · matching line {source_line+1}')
                    submitted = st.session_state.recognized_code.splitlines()
                    code_panel(submitted, source_line, 'Your submitted code')
                else:
                    st.write('This operation does not have a clear one-to-one line match in your submitted implementation. The highlighted reference code shows the equivalent algorithmic operation.')
                    st.code(st.session_state.recognized_code,
                            language='python')
        controls = st.columns([1, 1, 1.25, 1, 1.4])
        if controls[0].button('← Back', disabled=step == 0, use_container_width=True, key=f'back_{algorithm}'):
            st.session_state.trace_step = step - 1
            st.session_state.is_playing = False
            st.rerun()
        if controls[1].button('Next →', disabled=step >= total-1, use_container_width=True, key=f'next_{algorithm}'):
            st.session_state.trace_step = step + 1
            st.session_state.is_playing = False
            st.rerun()
        if controls[2].button('Pause' if st.session_state.is_playing else '▶ Play', use_container_width=True, key=f'play_{algorithm}'):
            st.session_state.is_playing = not st.session_state.is_playing
            st.rerun()
        if controls[3].button('Restart', use_container_width=True, key=f'restart_{algorithm}'):
            st.session_state.trace_step = 0
            st.session_state.is_playing = False
            st.rerun()
        speed = controls[4].selectbox('Playback speed', ['Slow · 2.4 sec', 'Relaxed · 1.6 sec', 'Normal · 1.1 sec'], index=['Slow · 2.4 sec', 'Relaxed · 1.6 sec', 'Normal · 1.1 sec'].index(
            {'2.4s': 'Slow · 2.4 sec', '1.6s': 'Relaxed · 1.6 sec', '1.1s': 'Normal · 1.1 sec'}.get(st.session_state.animation_interval, 'Relaxed · 1.6 sec')), key=f'speed_{algorithm}')
        speed_map = {'Slow · 2.4 sec': '2.4s',
                     'Relaxed · 1.6 sec': '1.6s', 'Normal · 1.1 sec': '1.1s'}
        if speed_map[speed] != st.session_state.animation_interval:
            st.session_state.animation_interval = speed_map[speed]
            st.rerun()
        if st.session_state.is_playing and step >= total - 1:
            st.session_state.is_playing = False
        elif st.session_state.is_playing:
            st.session_state.trace_step = step + 1
    player()
    return events


samples = {
    'Binary search': 'def search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        if arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1',
    'Linear search': 'def search(arr, target):\n    for index, value in enumerate(arr):\n        if value == target:\n            return index\n    return -1',
    'Bubble sort': 'def sort_values(values):\n    arr = values.copy()\n    for i in range(len(arr)):\n        for j in range(len(arr) - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr',
    'Insertion sort': 'def insertion_sort(values):\n    arr = values.copy()\n    for i in range(1, len(arr)):\n        current = arr[i]\n        j = i - 1\n        while j >= 0 and arr[j] > current:\n            arr[j + 1] = arr[j]\n            j -= 1\n        arr[j + 1] = current\n    return arr',
    'Quick sort': 'def quick_sort(values):\n    if len(values) <= 1:\n        return values\n    pivot = values[-1]\n    left = [x for x in values[:-1] if x <= pivot]\n    right = [x for x in values[:-1] if x > pivot]\n    return quick_sort(left) + [pivot] + quick_sort(right)',
    'Merge sort': 'def merge_sort(values):\n    if len(values) <= 1:\n        return values\n    middle = len(values) // 2\n    left = merge_sort(values[:middle])\n    right = merge_sort(values[middle:])\n    return merge(left, right)',
}

st.sidebar.markdown('## AlgoLens')
st.sidebar.caption('Algorithm learning studio')
page = st.sidebar.radio('Workspace', [
                        'Recognize code', 'Explore algorithms', 'Model evaluation'], key='nav_page')
st.sidebar.divider()
st.sidebar.caption(
    'A compact learning prototype. Predictions are suggestions, not proofs of algorithm identity.')
st.sidebar.markdown('[Dataset documentation](DATASET.md)')

if page == 'Recognize code':
    title_block('CODE ANALYSIS', 'Recognize an algorithm',
                'Paste a Python function to identify its likely algorithm, then explore how it works.')
    st.write('')
    left, right = st.columns([1.35, .8], gap='large')
    with left:
        sample = st.selectbox('Start with an example', [
                              'Choose an example'] + list(samples))
        code = st.text_area('Python source code', value=samples.get(
            sample, ''), height=300, placeholder='Paste a Python function here…')
        if st.button('Analyze code', type='primary', use_container_width=True):
            try:
                label, scores = predict_code(code, get_model())
                st.session_state.recognized_algorithm = label
                st.session_state.recognized_code = code
                st.session_state.recognition_scores = scores
                st.session_state.explore_algorithm = label
                st.session_state.trace_step = 0
                st.session_state.is_playing = False
            except Exception as exc:
                st.error(str(exc))
    with right:
        with st.container(border=True):
            st.markdown('**What happens next**')
            st.markdown('1. The classifier analyzes code patterns.\n2. It ranks the six supported algorithm classes.\n3. Explore opens a visual walkthrough of the predicted algorithm.')
            st.caption(
                'Supported: Binary Search, Linear Search, Bubble Sort, Insertion Sort, Quick Sort, Merge Sort.')
    if st.session_state.recognized_algorithm and st.session_state.recognized_code == code:
        label = st.session_state.recognized_algorithm
        scores = st.session_state.get('recognition_scores')
        st.divider()
        st.markdown('### Recognition result')
        st.success(f'Likely algorithm: **{label.replace("_", " ").title()}**')
        best_case, average_case, worst_case = CASE_COMPLEXITY[label]
        c1, c2, c3 = st.columns(3)
        c1.metric('Best-case time', best_case)
        c2.metric('Average-case time', average_case)
        c3.metric('Worst-case time', worst_case)
        note = COMPLEXITY[label][3]
        st.write(note)
        if scores:
            score_df = pd.DataFrame({'Algorithm': [k.replace('_', ' ').title() for k in scores], 'Decision score': list(
                scores.values())}).sort_values('Decision score', ascending=True)
            st.caption(
                'Classifier decision scores; these are not calibrated probabilities.')
            st.bar_chart(score_df.set_index('Algorithm'))
        st.warning(
            'This is a model prediction, not a proof. Unfamiliar implementations may be misclassified.')
        st.button('Explore the predicted algorithm', type='primary',
                  on_click=navigate_to_explore, args=(label,))

elif page == 'Explore algorithms':
    title_block('INTERACTIVE LEARNING', 'Explore an algorithm',
                'Follow each operation, see the active values, and connect the animation to the code.')
    labels = list(COMPLEXITY)
    default_index = labels.index(
        st.session_state.recognized_algorithm) if st.session_state.recognized_algorithm in labels else 0
    algorithm = st.selectbox('Choose an algorithm', labels, index=default_index,
                             format_func=lambda x: x.replace('_', ' ').title(), key='explore_algorithm')
    if st.session_state.recognized_algorithm:
        st.caption(
            f'Your most recent recognition result: {st.session_state.recognized_algorithm.replace("_", " ").title()}')
    intros = {
        'binary_search': 'Binary search works on sorted input. It checks the middle item and discards the half that cannot contain the target.',
        'linear_search': 'Linear search checks items in order and stops as soon as it finds the target.',
        'bubble_sort': 'Bubble sort compares neighboring values and swaps an out-of-order pair. Repeated passes move large values toward the end.',
        'insertion_sort': 'Insertion sort grows a sorted section from left to right, inserting each next value into its correct position.',
        'quick_sort': 'Quick sort selects a pivot, partitions values around it, and recursively sorts the smaller sections.',
        'merge_sort': 'Merge sort divides the list into halves, sorts each half, and merges the sorted halves back together.',
    }
    st.markdown(
        f'<div class="algo-card"><div class="algo-step">Algorithm overview</div><div style="font-size:1.05rem;font-weight:600;margin-top:6px">{intros[algorithm]}</div></div>', unsafe_allow_html=True)
    st.write('')
    default_numbers = '2, 5, 8, 12, 16, 23, 38' if algorithm in (
        'binary_search', 'linear_search') else '8, 3, 6, 2, 9, 1, 5'
    col1, col2 = st.columns([1.5, .7])
    with col1:
        raw = st.text_input('Input values · comma-separated',
                            default_numbers, key=f'input_{algorithm}')
    with col2:
        target = st.number_input('Search target', value=16, step=1, key=f'target_{algorithm}', disabled=algorithm not in (
            'binary_search', 'linear_search'))
    try:
        values = [int(x.strip()) for x in raw.split(',') if x.strip()]
        if not values:
            raise ValueError('Enter at least one whole number.')
        if len(values) > 12:
            raise ValueError(
                'Use 12 or fewer values to keep the walkthrough readable.')
        if algorithm == 'binary_search' and values != sorted(values):
            st.warning(
                'Binary search requires sorted input. The demonstration will use the sorted values.')
            values = sorted(values)
        trace_signature = (algorithm, tuple(values), int(
            target) if algorithm in ('binary_search', 'linear_search') else None)
        if st.session_state.get('trace_signature') != trace_signature:
            st.session_state.trace_signature = trace_signature
            st.session_state.trace_step = 0
            st.session_state.is_playing = False
        if algorithm == 'quick_sort':
            with st.expander('Choose a pivot for the first partition'):
                pivot_choice = st.selectbox(
                    'First pivot value', values, index=len(values)-1, key='pivot_choice')
                st.caption(
                    f'The teaching trace uses {pivot_choice} as the first pivot. Pivot choice affects the shape and efficiency of Quick Sort.')
                if pivot_choice != values[-1]:
                    adjusted = values.copy()
                    adjusted.remove(pivot_choice)
                    adjusted.append(pivot_choice)
                    st.caption(
                        'For this demonstration, the chosen pivot is moved to the final position before partitioning.')
                    values = adjusted
            pivot_signature = (algorithm, tuple(values), pivot_choice)
            if st.session_state.get('pivot_signature') != pivot_signature:
                st.session_state.pivot_signature = pivot_signature
                st.session_state.trace_step = 0
                st.session_state.is_playing = False
        if algorithm in ('quick_sort', 'merge_sort'):
            with st.expander('Recursion tree · see how the problem breaks down'):
                st.caption(
                    'Each node represents a smaller subproblem. Quick Sort partitions around a pivot; Merge Sort splits the list into halves.')
                draw_recursion_tree(algorithm, values)
        st.markdown('### Step-by-step walkthrough')
        events = render_trace(algorithm, values, target)
        st.markdown('### Predict the next operation')
        current_step = min(st.session_state.trace_step, len(events) - 1)
        if current_step < len(events) - 1:
            next_event = events[current_step + 1]
            possible_actions = list(dict.fromkeys(
                ['Compare', 'Swap', 'Select pivot', 'Partition', 'Divide', 'Merge', 'Insert value', 'Search next position', 'Finish']))
            expected_action = next_event['action']
            normalized = 'Compare' if 'Compare' in expected_action or 'Inspect' in expected_action or 'Check' in expected_action else 'Swap' if 'Swap' in expected_action else 'Select pivot' if 'pivot' in expected_action.lower(
            ) else 'Partition' if 'Partition' in expected_action or 'Place pivot' in expected_action else 'Divide' if 'Divide' in expected_action or 'Prepare' in expected_action else 'Merge' if 'Merge' in expected_action else 'Insert value' if 'Insert' in expected_action else 'Search next position' if 'Discard' in expected_action else 'Finish' if expected_action in ('Complete', 'Found', 'Not found') else expected_action
            quiz_answer = st.selectbox(
                'What do you think happens next?', possible_actions, key=f'next_quiz_{algorithm}')
            if st.button('Check prediction', key=f'next_quiz_check_{algorithm}'):
                if quiz_answer == normalized:
                    st.success(
                        f'Correct. Next: {next_event["action"]}. {next_event["explanation"]}')
                else:
                    st.error(
                        f'Not quite. The next operation is {next_event["action"].lower()}: {next_event["explanation"]}')
            if 1 <= len(next_event.get('compare', ())) <= 2:
                import itertools
                compare_count = len(next_event['compare'])
                candidates = list(itertools.combinations(
                    range(len(values)), compare_count))
                candidate_labels = [', '.join(
                    f'index {i} (value {events[current_step]["values"][i]})' for i in candidate) for candidate in candidates]
                expected_label = ', '.join(
                    f'index {i} (value {events[current_step]["values"][i]})' for i in next_event['compare'])
                picked = st.selectbox('Which element(s) will be examined next?',
                                      candidate_labels, key=f'compare_quiz_{algorithm}_{current_step}')
                if st.button('Check selected element(s)', key=f'compare_check_{algorithm}_{current_step}'):
                    if picked == expected_label:
                        st.success(
                            f'Correct. {expected_label} is the next position involved.')
                    else:
                        st.error(
                            f'Not quite. The next operation involves {expected_label}. Follow the highlighted index labels in the graph.')
        else:
            st.success(
                'The walkthrough is complete. Restart to practice predicting the steps again.')
    except ValueError as exc:
        st.error(str(exc))

    st.divider()
    st.markdown('### Complexity explorer')
    explanation = COMPLEXITY[algorithm][3]
    best_case, average_case, worst_case = CASE_COMPLEXITY[algorithm]
    c1, c2, c3 = st.columns(3)
    c1.metric('Best-case time', best_case)
    c2.metric('Average-case time', average_case)
    c3.metric('Worst-case time', worst_case)
    st.write(explanation)
    n = st.slider('Compare estimated growth as input size increases', min_value=10,
                  max_value=500, value=100, step=10, key=f'complexity_n_{algorithm}')
    sizes = list(range(10, n+1, 10))
    if algorithm in ('binary_search',):
        ops = [math.log2(x) for x in sizes]
    elif algorithm == 'linear_search':
        ops = [x for x in sizes]
    elif algorithm == 'bubble_sort':
        ops = [x*x for x in sizes]
    elif algorithm == 'insertion_sort':
        ops = [x*x for x in sizes]
    elif algorithm == 'quick_sort':
        ops = [x*math.log2(x) for x in sizes]
    else:
        ops = [x*math.log2(x) for x in sizes]
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ax.plot(sizes, ops, linewidth=2.5, color='#397C68')
    ax.fill_between(sizes, ops, alpha=.10, color='#397C68')
    ax.set_xlabel('Input size (n)')
    ax.set_ylabel('Relative operation growth')
    ax.grid(alpha=.2)
    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.caption('This chart illustrates asymptotic growth, not measured runtime. Actual runtime depends on implementation, input order, and hardware.')

    st.divider()
    st.markdown('### Check your understanding')
    if algorithm == 'quick_sort':
        correct = values[-1]
        choices = list(dict.fromkeys(values))
        answer = st.selectbox(
            'In this walkthrough, which value is selected as the first pivot?', choices, key='quiz_pivot')
        if st.button('Check my answer', key='check_pivot'):
            if answer == correct:
                st.success(
                    f'Correct. {correct} is selected as the pivot for the first partition.')
            else:
                st.error(
                    f'Not quite. The first pivot in this trace is {correct}. A pivot is used to divide the other values into two groups.')
    else:
        question = 'What does this algorithm do next?' if algorithm in (
            'binary_search', 'linear_search') else 'What is the main operation this algorithm repeats?'
        options = {
            'binary_search': ['Check the middle of the remaining range', 'Swap every adjacent pair', 'Merge two sorted lists'],
            'linear_search': ['Check the next item in order', 'Discard half the list', 'Choose a pivot'],
            'bubble_sort': ['Compare neighboring values', 'Split the list in half', 'Select a pivot'],
            'insertion_sort': ['Insert the next value into the sorted prefix', 'Compare the middle item', 'Merge two halves'],
            'merge_sort': ['Divide into halves, then merge sorted parts', 'Swap neighboring values only', 'Search from left to right'],
        }
        correct = options[algorithm][0]
        answer = st.radio(
            question, options[algorithm], key=f'quiz_{algorithm}')
        if st.button('Check my answer', key=f'check_{algorithm}'):
            if answer == correct:
                st.success(
                    'Correct. You identified the central operation of this algorithm.')
            else:
                st.error(
                    f'Not quite. {correct}. Review the walkthrough above and try again.')

else:
    title_block('MODEL REPORT', 'Training and evaluation',
                'Review how the classifier performs and where its predictions can go wrong.')
    metrics_path = ROOT / 'results' / 'metrics.json'
    image_path = ROOT / 'results' / 'confusion_matrix.png'
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding='utf-8'))
        st.markdown(
            f'**Selected baseline:** `{metrics.get("selected_model", "Not available")}`')
        st.markdown(
            f'**Dataset:** {metrics["dataset"]["total_examples"]} examples · **Held-out test:** {metrics["dataset"]["test_examples"]} examples')
        st.info(metrics['dataset']['data_note'])
        rows = [{'Model': name, 'Accuracy': values['accuracy'], 'Macro F1': values['macro_f1'],
                 'Weighted F1': values['weighted_f1']} for name, values in metrics['models'].items()]
        st.dataframe(pd.DataFrame(rows),
                     use_container_width=True, hide_index=True)
        if image_path.exists():
            st.image(str(image_path), caption='Held-out test confusion matrix',
                     use_container_width=True)
        st.caption('Results are from a grouped split of controlled examples. They are not evidence of performance on arbitrary code from the internet.')
        st.markdown('**How to read the confusion matrix**')
        st.write('Rows represent the true algorithm; columns represent the model prediction. Values on the diagonal are correct predictions. Off-diagonal values show which algorithms the model confuses.')
    else:
        st.info('No metrics found yet. Run `python src/generate_dataset.py` and `python src/train_model.py` from the project folder.')
