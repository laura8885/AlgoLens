from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.algorithms import SAMPLE_GRAPH, array_search_trace, graph_trace, sorting_trace
from src.recognition import analyze_code, estimate_complexity, train

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="AlgoLens | Algorithm Studio", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#e9edf5; --muted:#9aa7ba; --panel:#111a2b; --line:#26344a; --cyan:#67e8f9; --violet:#a78bfa; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 12% 0%, rgba(56,189,248,.10), transparent 32%), radial-gradient(ellipse at 90% 8%, rgba(139,92,246,.10), transparent 30%), #080e19; color:var(--ink); }
.block-container { padding-top:2rem; max-width:1440px; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
[data-testid="stSidebar"] { background:#0b1321; border-right:1px solid #1d2b40; }
[data-testid="stMetric"] { background:linear-gradient(145deg,#111d30,#0d1727); border:1px solid #26364d; padding:15px 17px; border-radius:15px; }
[data-testid="stMetricLabel"] { color:#9aa7ba !important; }
[data-testid="stMetricValue"] { color:#f1f5f9 !important; font-family:'Space Grotesk',sans-serif; }
.panel { background:linear-gradient(145deg,rgba(20,31,50,.96),rgba(13,22,37,.96)); border:1px solid #26364d; border-radius:18px; padding:20px 22px; }
.eyebrow { color:#67e8f9; text-transform:uppercase; letter-spacing:.17em; font-size:.72rem; font-weight:700; }
.hero-title { font-family:'Space Grotesk',sans-serif; font-size:3.25rem; line-height:1.04; font-weight:700; letter-spacing:-.06em; color:#f8fafc; }
.hero-sub { color:#a7b4c8; font-size:1.05rem; max-width:760px; line-height:1.7; }
.tag { display:inline-block; padding:5px 10px; margin:3px 5px 3px 0; border:1px solid #30435d; border-radius:999px; color:#c5d4e8; font-size:.78rem; }
.small-muted { color:#9aa7ba; font-size:.88rem; }
.codebox { background:#080f1b; border:1px solid #25354d; border-radius:12px; padding:14px; }
div.stButton > button { border-radius:10px; border:1px solid #344862; background:#17263b; color:#e8f3ff; font-weight:600; }
div.stButton > button:hover { border-color:#67e8f9; color:#67e8f9; }
.stTabs [data-baseweb="tab"] { color:#a9b7ca; }
.stTabs [aria-selected="true"] { color:#67e8f9 !important; }
hr { border-color:#24344a; }
</style>
""", unsafe_allow_html=True)

SORTS = ["Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort", "Quick Sort"]
ARRAY_SEARCH = ["Linear Search", "Binary Search"]
GRAPH_SEARCH = ["Breadth-First Search", "Depth-First Search", "Dijkstra's", "A* Search"]
ALL_ALGORITHMS = ARRAY_SEARCH + GRAPH_SEARCH + SORTS

with st.sidebar:
    st.markdown("<div style='font-family:Space Grotesk;font-size:1.45rem;font-weight:700;color:#f1f5f9'>◈ Algo<span style='color:#67e8f9'>Lens</span></div>", unsafe_allow_html=True)
    st.caption("ALGORITHM STUDIO · v3.0")
    page = st.radio("WORKSPACE", ["Overview", "Algorithm Explorer", "Code Recognition", "Complexity Table", "About & Methodology"], label_visibility="visible")
    st.divider()
    st.markdown("<span class='small-muted'>11 algorithms · 3 families · multi-repository corpus builder</span>", unsafe_allow_html=True)


def metric_card(label, value, note):
    st.metric(label, value, note)


def complexity_table():
    rows = [
        ["Linear Search", "O(1)", "O(n)", "O(n)", "O(1)"],
        ["Binary Search", "O(1)", "O(log n)", "O(log n)", "O(1)"],
        ["BFS", "O(V + E)", "O(V + E)", "O(V + E)", "O(V)"],
        ["DFS", "O(V + E)", "O(V + E)", "O(V + E)", "O(V)"],
        ["Dijkstra", "O((V+E) log V)", "O((V+E) log V)", "O((V+E) log V)", "O(V)"],
        ["A*", "Heuristic-dependent", "Heuristic-dependent", "Exponential worst case", "O(V)"],
        ["Bubble Sort", "O(n)", "O(n²)", "O(n²)", "O(1)"],
        ["Selection Sort", "O(n²)", "O(n²)", "O(n²)", "O(1)"],
        ["Insertion Sort", "O(n)", "O(n²)", "O(n²)", "O(1)"],
        ["Merge Sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)"],
        ["Quick Sort", "O(n log n)", "O(n log n)", "O(n²)", "O(log n) avg."],
    ]
    return pd.DataFrame(rows, columns=["Algorithm", "Best", "Average", "Worst", "Auxiliary space"])


def draw_array(step: dict, sorting: bool):
    values = step["array"]
    active = set(step.get("active", []))
    found = set(step.get("found", []))
    sorted_idx = set(step.get("sorted", []))
    colors = []
    for i in range(len(values)):
        if i in found:
            colors.append("#34d399")
        elif i in active:
            colors.append("#fbbf24")
        elif sorting and i in sorted_idx:
            colors.append("#64748b")
        else:
            colors.append("#38bdf8")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(values))),
        y=[0] * len(values),
        mode="lines",
        line=dict(color="#26364d", width=3),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(values))),
        y=[0] * len(values),
        mode="markers+text",
        marker=dict(size=54, color=colors, line=dict(color="#dce8f5", width=2)),
        text=[str(value) for value in values],
        textposition="middle center",
        textfont=dict(color="#07111f", size=15, family="DM Sans"),
        customdata=list(range(len(values))),
        hovertemplate="Index %{customdata}<br>Value %{text}<extra></extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(values))),
        y=[-0.58] * len(values),
        mode="text",
        text=[f"Index {i}" for i in range(len(values))],
        textfont=dict(color="#94a3b8", size=11),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=15, r=15, t=25, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        xaxis=dict(visible=False, range=[-0.7, len(values) - 0.3]),
        yaxis=dict(visible=False, range=[-0.9, 0.65], fixedrange=True),
        showlegend=False,
    )
    return fig


def draw_graph(step: dict, algorithm: str):
    graph = nx.Graph()
    for u, neighbors in SAMPLE_GRAPH.items():
        for v, w in neighbors.items(): graph.add_edge(u, v, weight=w)
    pos = {"A":(0,2),"B":(2,3),"C":(2,1),"D":(4,3),"E":(4,1),"F":(6,2),"G":(2,5),"H":(4,5)}
    path = step.get("path", [])
    path_edges = {tuple(sorted((path[i],path[i+1]))) for i in range(len(path)-1)}
    edge_x=[]; edge_y=[]; edge_text=[]; path_x=[]; path_y=[]
    for u,v,data in graph.edges(data=True):
        target = path_x if tuple(sorted((u,v))) in path_edges else edge_x
        target.extend([pos[u][0],pos[v][0],None])
        (path_y if target is path_x else edge_y).extend([pos[u][1],pos[v][1],None])
        edge_text.append((u,v,data['weight']))
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=edge_x,y=edge_y,mode="lines",line=dict(width=2,color="#34445e"),hoverinfo="skip",showlegend=False))
    fig.add_trace(go.Scatter(x=path_x,y=path_y,mode="lines",line=dict(width=5,color="#34d399"),hoverinfo="skip",showlegend=False))
    ex=[];ey=[];et=[]
    for u,v,w in edge_text:
        ex.append((pos[u][0]+pos[v][0])/2);ey.append((pos[u][1]+pos[v][1])/2);et.append(str(w))
    fig.add_trace(go.Scatter(x=ex,y=ey,mode="text",text=et,textposition="middle center",textfont=dict(color="#d8e2f0",size=12),hoverinfo="skip",showlegend=False))
    current=step.get("current"); visited=set(step.get("visited",[])); frontier=set(step.get("frontier",[]));
    node_colors=[];node_sizes=[];texts=[]
    for node in graph.nodes:
        if node == current: node_colors.append("#fbbf24");node_sizes.append(34)
        elif node in path: node_colors.append("#34d399");node_sizes.append(30)
        elif node in frontier: node_colors.append("#a78bfa");node_sizes.append(29)
        elif node in visited: node_colors.append("#64748b");node_sizes.append(27)
        else: node_colors.append("#38bdf8");node_sizes.append(27)
        texts.append(f"Node {node}<br>Distance: {step.get('distances',{}).get(node,'—')}")
    fig.add_trace(go.Scatter(x=[pos[n][0] for n in graph.nodes],y=[pos[n][1] for n in graph.nodes],mode="markers+text",text=list(graph.nodes),textposition="middle center",textfont=dict(color="#07111f",size=13,family="DM Sans",),marker=dict(size=node_sizes,color=node_colors,line=dict(width=2,color="#dce8f5")),hovertext=texts,hoverinfo="text",showlegend=False))
    fig.update_layout(height=470,margin=dict(l=20,r=20,t=15,b=15),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(visible=False),yaxis=dict(visible=False,scaleanchor="x",scaleratio=1),font=dict(color="#cbd5e1"))
    return fig


def animated_array_figure(steps, sorting):
    first = draw_array(steps[0], sorting)
    frames = []
    slider_steps = []
    for index, step in enumerate(steps):
        frame_fig = draw_array(step, sorting)
        frames.append(go.Frame(data=frame_fig.data, name=str(index), layout=go.Layout(title_text=f"Step {index + 1} / {len(steps)} · {step['message']}")))
        slider_steps.append({"label": str(index + 1), "method": "animate", "args": [[str(index)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]})
    first.frames = frames
    first.update_layout(
        title=f"Step 1 / {len(steps)} · {steps[0]['message']}",
        updatemenus=[{"type": "buttons", "showactive": False, "x": 0.02, "y": 1.15, "buttons": [
            {"label": "▶ Play", "method": "animate", "args": [None, {"fromcurrent": True, "frame": {"duration": 650, "redraw": True}, "transition": {"duration": 250}}]},
            {"label": "Ⅱ Pause", "method": "animate", "args": [[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False}, "transition": {"duration": 0}}]},
        ]}],
        sliders=[{"active": 0, "currentvalue": {"prefix": "Trace step: "}, "pad": {"t": 35}, "steps": slider_steps}],
    )
    return first


def animated_graph_figure(steps, algorithm):
    first = draw_graph(steps[0], algorithm)
    frames = []
    slider_steps = []
    for index, step in enumerate(steps):
        frame_fig = draw_graph(step, algorithm)
        frames.append(go.Frame(data=frame_fig.data, name=str(index), layout=go.Layout(title_text=f"Step {index + 1} / {len(steps)} · {step['message']}")))
        slider_steps.append({"label": str(index + 1), "method": "animate", "args": [[str(index)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]})
    first.frames = frames
    first.update_layout(
        title=f"Step 1 / {len(steps)} · {steps[0]['message']}",
        updatemenus=[{"type": "buttons", "showactive": False, "x": 0.02, "y": 1.15, "buttons": [
            {"label": "▶ Play", "method": "animate", "args": [None, {"fromcurrent": True, "frame": {"duration": 800, "redraw": True}, "transition": {"duration": 250}}]},
            {"label": "Ⅱ Pause", "method": "animate", "args": [[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False}, "transition": {"duration": 0}}]},
        ]}],
        sliders=[{"active": 0, "currentvalue": {"prefix": "Trace step: "}, "pad": {"t": 35}, "steps": slider_steps}],
    )
    return first


if page == "Overview":
    st.markdown("<div class='eyebrow'>Interactive computer science learning environment</div><div class='hero-title'>Understand the logic.<br><span style='color:#67e8f9'>See every step.</span></div>", unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Explore classic algorithms through visual execution traces, inspect how graph-search strategies expand a network, and experiment with a lightweight code-recognition model.</p>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: metric_card("Algorithms", "11", "Searching · sorting · graphs")
    with c2: metric_card("Algorithm families", "3", "Arrays, sorting, graph traversal")
    with c3: metric_card("Graph methods", "4", "BFS, DFS, Dijkstra, A*")
    with c4: metric_card("Recognition", "11 classes", "AST + Linear SVM")
    st.write("")
    left,right=st.columns([1.25,1],gap="large")
    with left:
        st.markdown("<div class='panel'><div class='eyebrow'>01 / Explore</div><h3>Algorithm Explorer</h3><p class='small-muted'>Move through deterministic execution traces. Compare how different strategies inspect values, reorder data, or expand graph nodes.</p><span class='tag'>Step controls</span><span class='tag'>Node states</span><span class='tag'>Array animation</span><span class='tag'>Path highlighting</span></div>",unsafe_allow_html=True)
        st.write("")
        st.markdown("<div class='panel'><div class='eyebrow'>02 / Recognize</div><h3>Code Recognition</h3><p class='small-muted'>Submit Python code and inspect structural clues used to identify its algorithm. The analyzer ignores comments, docstrings, and user-defined identifiers.</p><span class='tag'>AST structure</span><span class='tag'>Identifier normalization</span><span class='tag'>Linear SVM</span></div>",unsafe_allow_html=True)
    with right:
        st.markdown("<div class='panel'><div class='eyebrow'>03 / Understand</div><h3>Complexity Table</h3><p class='small-muted'>Compare asymptotic growth and practical trade-offs. Learn why an algorithm that is fast on a small input may scale poorly.</p><span class='tag'>Big-O</span><span class='tag'>Best / average / worst</span></div>",unsafe_allow_html=True)
        st.write("")
        st.markdown("<div class='panel'><div class='eyebrow'>Design principle</div><h3>Algorithms first, ML second</h3><p class='small-muted'>The central experience is learning and experimentation. Machine learning supports code discovery rather than replacing the algorithm content.</p></div>",unsafe_allow_html=True)
    st.markdown("### Explore the algorithm families")
    a,b,c=st.columns(3)
    with a: st.markdown("<div class='panel'><h4>⌕ Array searching</h4><p class='small-muted'>Linear and Binary Search</p></div>",unsafe_allow_html=True)
    with b: st.markdown("<div class='panel'><h4>↗ Sorting</h4><p class='small-muted'>Bubble, Selection, Insertion, Merge, Quick</p></div>",unsafe_allow_html=True)
    with c: st.markdown("<div class='panel'><h4>◎ Graph search</h4><p class='small-muted'>BFS, DFS, Dijkstra, A*</p></div>",unsafe_allow_html=True)

elif page == "Algorithm Explorer":
    st.markdown("<div class='eyebrow'>Interactive execution</div><h1>Algorithm Explorer</h1><p class='hero-sub'>Choose an algorithm, configure an input, and inspect its execution one operation at a time.</p>",unsafe_allow_html=True)
    family=st.radio("Algorithm family",["Array Search","Sorting","Graph Search"],horizontal=True)
    options={"Array Search":ARRAY_SEARCH,"Sorting":SORTS,"Graph Search":GRAPH_SEARCH}[family]
    selected=st.selectbox("Algorithm",options)
    st.divider()
    if family == "Graph Search":
        c1,c2,c3=st.columns([1,1,2])
        with c1: start=st.selectbox("Start node",list(SAMPLE_GRAPH),index=0)
        with c2: goal=st.selectbox("Goal node",list(SAMPLE_GRAPH),index=5)
        with c3: st.caption("Weighted undirected sample graph · edge labels show costs · A* uses a scaled Euclidean-distance heuristic.")
        if st.button("Generate execution trace",type="primary") or "graph_steps" not in st.session_state or st.session_state.get("graph_key") != (selected,start,goal):
            st.session_state.graph_steps=graph_trace(selected,SAMPLE_GRAPH,start,goal)
            st.session_state.graph_key=(selected,start,goal)
            st.session_state.graph_index=0
        steps=st.session_state.graph_steps
        idx=st.session_state.get("graph_index",0)
        controls=st.columns([1,1,1,5])
        with controls[0]:
            if st.button("← Previous",disabled=idx==0): st.session_state.graph_index=max(0,idx-1);st.rerun()
        with controls[1]:
            if st.button("Next →",disabled=idx>=len(steps)-1): st.session_state.graph_index=min(len(steps)-1,idx+1);st.rerun()
        with controls[2]:
            if st.button("↺ Reset"): st.session_state.graph_index=0;st.rerun()
        with controls[3]: st.caption(f"Step {idx+1} of {len(steps)}")
        step=steps[idx]
        st.progress((idx+1)/len(steps))
        graph_col,info_col=st.columns([1.6,1],gap="large")
        with graph_col:
            st.plotly_chart(draw_graph(step,selected),use_container_width=True,config={"displayModeBar":False})
            st.markdown("<span class='tag'>● Current</span><span class='tag'>● Frontier</span><span class='tag'>● Visited</span><span class='tag'>● Final path</span>",unsafe_allow_html=True)
        with info_col:
            st.markdown("<div class='panel'><div class='eyebrow'>Current operation</div><h3>"+step["message"]+"</h3><p class='small-muted'>The highlighted node is the current node. Frontier nodes are candidates waiting to be explored.</p></div>",unsafe_allow_html=True)
            st.write("")
            st.metric("Visited nodes",len(step.get("visited",[])))
            st.metric("Frontier size",len(step.get("frontier",[])))
            if step.get("path"):
                st.success(" → ".join(step["path"]))
            st.markdown("**Algorithm behavior**")
            notes={"Breadth-First Search":"Uses a FIFO queue and explores the graph layer by layer. Finds a shortest path by edge count in an unweighted graph.","Depth-First Search":"Uses a LIFO stack to follow one branch before backtracking. Useful for reachability and structural exploration.","Dijkstra's":"Uses a min-priority queue to repeatedly finalize the closest unsettled node. Assumes non-negative edge weights.","A* Search":"Prioritizes nodes by f(n) = g(n) + h(n), combining the known path cost with a heuristic estimate to the goal."}
            st.info(notes[selected])
    else:
        c1,c2=st.columns([2,1])
        with c1: raw=st.text_input("Input values (comma-separated)","8, 3, 6, 2, 9, 1, 5")
        with c2:
            target=st.number_input("Target value",value=6,step=1,disabled=family!="Array Search")
        try:
            values=[int(x.strip()) for x in raw.split(",") if x.strip()]
            if not values or len(values)>18: raise ValueError("Enter between 1 and 18 integer values.")
        except ValueError as exc:
            st.error(str(exc));values=[8,3,6,2,9,1,5]
        if family=="Array Search" and selected=="Binary Search": st.caption("Binary Search requires sorted data. The trace automatically displays the sorted input.")
        key=(family,selected,tuple(values),int(target))
        if st.button("Build execution trace",type="primary") or "array_steps" not in st.session_state or st.session_state.get("array_key")!=key:
            st.session_state.array_steps=sorting_trace(selected,values) if family=="Sorting" else array_search_trace(selected,values,int(target))
            st.session_state.array_key=key;st.session_state.array_index=0
        steps=st.session_state.array_steps;idx=st.session_state.get("array_index",0)
        controls=st.columns([1,1,1,5])
        with controls[0]:
            if st.button("← Previous",disabled=idx==0,key="arrprev"): st.session_state.array_index=max(0,idx-1);st.rerun()
        with controls[1]:
            if st.button("Next →",disabled=idx>=len(steps)-1,key="arrnext"): st.session_state.array_index=min(len(steps)-1,idx+1);st.rerun()
        with controls[2]:
            if st.button("↺ Reset",key="arrreset"): st.session_state.array_index=0;st.rerun()
        with controls[3]: st.caption(f"Step {idx+1} of {len(steps)}")
        step=steps[idx];st.progress((idx+1)/len(steps))
        visual,detail=st.columns([1.6,1],gap="large")
        with visual: st.plotly_chart(draw_array(step,family=="Sorting"),use_container_width=True,config={"displayModeBar":False})
        with detail:
            st.markdown("<div class='panel'><div class='eyebrow'>Current operation</div><h3>"+step["message"]+"</h3><p class='small-muted'>Yellow indicates the active comparison or operation. Green marks a successful search result.</p></div>",unsafe_allow_html=True)
            st.markdown("**How it works**")
            descriptions={"Linear Search":"Checks elements sequentially until the target is found or the array ends.","Binary Search":"Compares the midpoint and discards half of the remaining sorted search interval.","Bubble Sort":"Compares adjacent values and swaps out-of-order pairs, moving large values toward the end.","Selection Sort":"Selects the smallest remaining value and places it at the next sorted position.","Insertion Sort":"Builds a sorted prefix by shifting larger values and inserting the next value.","Merge Sort":"Recursively divides the array, then merges sorted subarrays.","Quick Sort":"Partitions values around a pivot, then recursively sorts the partitions."}
            st.info(descriptions[selected])

elif page == "Code Recognition":
    st.markdown("<div class='eyebrow'>Learn from your code</div><h1>Code Recognition</h1><p class='hero-sub'>Paste a Python algorithm to identify it, compare its time complexity, and watch how it works.</p>",unsafe_allow_html=True)
    st.caption("Your code is analyzed but not executed. The visual trace uses the detected algorithm with the input you choose.")
    default="""def binary_search(values, target):
    low, high = 0, len(values) - 1
    while low <= high:
        mid = (low + high) // 2
        if values[mid] == target:
            return mid
        elif values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1"""
    code=st.text_area("Paste Python code",default,height=250)
    if st.button("Recognize algorithm",type="primary",use_container_width=True):
        if len(code.strip())<20:
            st.error("Please enter a longer Python snippet.")
        else:
            try:
                result=analyze_code(code)
                st.session_state.prediction=result
                st.session_state.recognized_code=code
            except Exception as exc:
                st.error(f"Could not analyze this code: {exc}")
    if "prediction" in st.session_state:
        result=st.session_state.prediction
        label=result["prediction"]
        complexity=estimate_complexity(st.session_state.get("recognized_code", code), label)
        st.markdown("<div class='panel'><div class='eyebrow'>Identified algorithm</div><div style='font-family:Space Grotesk;font-size:2.1rem;font-weight:700;color:#67e8f9'>"+label+"</div></div>",unsafe_allow_html=True)
        st.markdown("### Time complexity")
        best_col,avg_col,worst_col=st.columns(3)
        with best_col: st.metric("Best case",complexity["best"])
        with avg_col: st.metric("Average case",complexity["average"])
        with worst_col: st.metric("Worst case",complexity["worst"])
        st.caption(complexity["note"])
        st.divider()
        st.markdown("### See how it works")
        if label in SORTS or label in ARRAY_SEARCH:
            input_col,target_col=st.columns([2,1])
            with input_col: trace_raw=st.text_input("Input values (comma-separated)","8, 3, 6, 2, 9, 1, 5",key="recognition_trace_values")
            with target_col: trace_target=st.number_input("Search target",value=6,step=1,key="recognition_trace_target",disabled=label not in ARRAY_SEARCH)
            try:
                trace_values=[int(item.strip()) for item in trace_raw.split(",") if item.strip()]
                if not trace_values or len(trace_values)>18: raise ValueError("Enter between 1 and 18 integer values.")
                trace_steps=sorting_trace(label,trace_values) if label in SORTS else array_search_trace(label,trace_values,int(trace_target))
                st.plotly_chart(animated_array_figure(trace_steps,label in SORTS),use_container_width=True,config={"displayModeBar":False})
            except ValueError as exc:
                st.error(str(exc))
        else:
            graph_col1,graph_col2=st.columns(2)
            with graph_col1: trace_start=st.selectbox("Start node",list(SAMPLE_GRAPH),index=0,key="recognition_graph_start")
            with graph_col2: trace_goal=st.selectbox("Goal node",list(SAMPLE_GRAPH),index=5,key="recognition_graph_goal")
            trace_steps=graph_trace(label,SAMPLE_GRAPH,trace_start,trace_goal)
            st.plotly_chart(animated_graph_figure(trace_steps,label),use_container_width=True,config={"displayModeBar":False})

elif page == "Complexity Table":
    st.markdown("<div class='eyebrow'>Performance fundamentals</div><h1>Complexity Table</h1><p class='hero-sub'>Compare asymptotic growth and understand the trade-offs behind common algorithm choices.</p>",unsafe_allow_html=True)
    st.dataframe(complexity_table(),use_container_width=True,hide_index=True)
    st.caption("Graph algorithms assume adjacency-list representations. Dijkstra assumes non-negative weights. A* performance depends strongly on the heuristic and problem structure.")
    st.markdown("### Growth curves")
    n=st.slider("Input size (n)",10,200,80,10)
    x=list(range(1,n+1))
    curves={"O(1)": [1]*n,"O(log n)": [__import__('math').log2(i) for i in x],"O(n)":x,"O(n log n)":[i*__import__('math').log2(i) for i in x],"O(n²)":[i*i for i in x]}
    selected_curves=st.multiselect("Show growth classes",list(curves),default=["O(log n)","O(n)","O(n log n)","O(n²)"])
    fig=go.Figure()
    for label in selected_curves: fig.add_trace(go.Scatter(x=x,y=curves[label],mode="lines",name=label,line=dict(width=3)))
    fig.update_layout(height=430,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#cbd5e1"),xaxis_title="Input size",yaxis_title="Relative operation growth",legend_title="Complexity",xaxis=dict(gridcolor="#1e293b"),yaxis=dict(gridcolor="#1e293b"))
    st.plotly_chart(fig,use_container_width=True)

else:
    st.markdown("<div class='eyebrow'>Project documentation</div><h1>About AlgoLens</h1><p class='hero-sub'>An interactive algorithms learning environment with an optional machine-learning code-recognition component.</p>",unsafe_allow_html=True)
    st.markdown("### Architecture")
    st.code("""AlgoLens/
├── app.py                  # Streamlit interface and page routing
├── src/
│   ├── algorithms.py       # Deterministic execution-trace generators
│   ├── build_corpus.py     # License-checked public-source corpus collection
│   └── recognition.py      # AST normalization, structural analysis, training, inference
├── data/
│   ├── algorithm_samples.csv
│   └── SOURCES.md
├── models/
│   └── classifier.joblib
├── results/
│   └── metrics.json
├── tests/
│   └── test_algorithms.py
├── requirements.txt
└── README.md""",language="text")
    st.markdown("### Machine-learning methodology")
    st.write("The recognition component parses Python with the built-in AST module. It removes function names, variable names, comments, and docstrings before extracting node patterns, operators, recursion, indexing, queue/stack operations, and priority-queue behavior. A LinearSVC model ranks candidate algorithms alongside transparent structural rules. The corpus builder collects source files from public Python repositories after checking their SPDX license metadata. Each sample records its repository, source path, raw source URL, license, and path-derived algorithm label. Run the corpus builder to collect and deduplicate source files from the configured repositories, then retrain the classifier. Evaluation uses repository-held-out splits when the collected corpus has enough independent sources and class overlap.")
    st.markdown("### Scope and limitations")
    st.write("The visualizations are generated from independent algorithm implementations and controlled inputs; they do not execute arbitrary submitted code. The recognition model is a code-pattern classifier, not a formal program verifier. Source-path labels are useful collection signals but should be reviewed; repository-held-out metrics are only meaningful for classes and repositories represented in the split, and do not establish generalization to arbitrary Python code. Graph examples use a fixed weighted sample network. A* uses half the Euclidean distance over the sample node layout as its heuristic, keeping the estimate conservative for the sample edge costs.")
    st.markdown("### Reproducibility")
    st.code("python -m venv .venv\nsource .venv/bin/activate  # macOS / Linux\npip install -r requirements.txt\npython -m src.build_corpus\npython -m src.recognition\nstreamlit run app.py",language="bash")
    st.caption("For a Windows environment, activate the virtual environment with .venv\\Scripts\\activate.")
