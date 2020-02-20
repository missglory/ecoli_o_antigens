import re, collections
import networkx as nx
import matplotlib.pyplot as plt
from collections import namedtuple
import numpy as np
import pickle
from concurrent.futures import ThreadPoolExecutor

def get_graph_strings():
    graph_strings = {}
    with open("data.txt", "r") as file:
        next_name, next_str = "", ""
        for line in file.readlines():
            if not re.search(r"\||-", line):
                if not next_name == "":
                    graph_strings[next_name.replace("\t","").replace("\n","")] = next_str
                    next_str = ""
                next_name = line
            else:
                next_str += line
    return graph_strings

def add_edge(edge_labels: dict, g: nx.Graph, n1: int, n2: int, label: str):
    g.add_edge(n1, n2, label=label)
    edge_labels[(n1,n2)] = label

def parse(nm:str, input_str: str):
    lines = input_str.split("\n")
    if lines[-1] == "": lines = lines[:-1]  
    assert(len(lines) in (0, 1, 3, 5))
    g = nx.DiGraph(name=nm)
    labels, edge_labels = {}, {}
    if len(lines) == 0: return (nm, g, labels, edge_labels)
    edgess = []
    nodess = []
    for i in range(0,len(lines),2):
        line = lines[i]
        reg = re.compile(r"\(?\d?[<-][NP>]P?-?\d?\)?")
        res = re.finditer(reg, line)
        nodes_res = re.split(reg, line)
        edgess.append(res)
        nodess.append(nodes_res)
    verticalss = []
    retd = {}
    for i in range(1, len(lines), 2):
        vs = re.finditer(r"\|", lines[i])
        verticalss.append([])
        for v in vs:
            verticalss[-1].append(v.start())
    assert(len(verticalss) in range(3))
    edgess = [list(n) for n in edgess]
    ind = 0
    labels = {}
    nds = []
    for g_i, edges in enumerate(edgess):
        for i, edge in enumerate(edges):
            edge_prev = edges[i-1] if i > 0 else None
            before = {}
            before["l"] = edge_prev.end() if edge_prev else 0
            before["r"] = edge.start()
            before["ws"] = lines[g_i*2][before["l"]:before["r"]]
            before["cut"] = before["ws"].replace(" ", "").replace("\t", "")
            before["i"] = g_i
            before["ind"]=ind
            bc = before["cut"]
            if len(bc) > 0: 
                g.add_node(ind, label=bc)
                labels[ind] = bc
                nds.append(before)
                ind += 1

    for g_i, edges in enumerate(edgess):
        for i, edge in enumerate(edges):
            adj_nodes = [n for n in nds if (n["l"] == edge.end() or n["r"] == edge.start()) and n["i"]==g_i]
            if edge.group()[:2] == "->":
                assert(len(adj_nodes)==1)
                adj_nodes.append(*[n for n in nds if n["r"]==edges[-1].start() and n["i"]==g_i])
                _lbl = edges[-1].group() + edge.group()
                assert(not _lbl.find("->->")==-1)
                _lbl = _lbl.replace("->->", "->")
                add_edge(edge_labels, g, adj_nodes[1]["ind"], adj_nodes[0]["ind"], _lbl)
                
                continue
            if edge.group()[-2:] == "->":
                continue
            assert(len(adj_nodes) in (1,2))
            vs = [] if len(verticalss)==0 else (verticalss[0] if g_i < 2 else verticalss[1])
            vf = [v for v in vs if v < edge.end() and v > edge.start()]
            assert(len(vf) in (0,1))
            if g_i == 1 and len(verticalss)>1:
                vf.extend([v for v in verticalss[1] if v < edge.end() and v > edge.start()])
            if (len(vf) > 0):
            # for j in range(len(vf)):
                assert(len(vf)==1)
                assert(len(adj_nodes)==1 or adj_nodes[1]["ws"][0]==' ')
                vstart = vf[0]
                adj_v_node = [n for n in nds if n["l"] < vstart and n["r"] > vstart and abs(n["i"]-g_i) == 1]
                assert(len(adj_v_node)==1)
                add_edge(edge_labels, g, adj_nodes[0]["ind"], adj_v_node[0]["ind"], edge.group())
            else:
                assert(not adj_nodes[0]["ws"][-1]==' ')
                assert(not adj_nodes[1]["ws"][0] ==' ')
                add_edge(edge_labels, g, adj_nodes[0]["ind"], adj_nodes[1]["ind"], edge.group())
    return (nm, g, labels, edge_labels)
    

def nmatch(n1, n2):
    return not (n1 == {} or n2 == {}) and n1["label"]==n2["label"]

def ematch(e1, e2):
    return e1["label"] == e2["label"]

Graph = namedtuple("Graph", "name g nlabels elabels")
edit_distances = None 
graphs = []

def thread_func(tup: tuple):
    i, j = tup
    ed = nx.optimize_graph_edit_distance(graphs[i].g, graphs[j].g, node_match=nmatch, edge_match=ematch)
    _vs = []
    for v in ed:
        _vs.append(v)
    return (i, j, _vs[-1])


def calc_edit_distances(pickle_save = "edit_dists.pkl"):
    _l = len(graphs)
    edit_distances = np.zeros((_l, _l))
    edpy = [[[] for _ in range(_l)]  for _ in range(_l)]
    threads = []
    for i in range(_l):
        for j in range(_l):
    # for i in range(5):
        # for j in range(5):
            threads.append((i,j))
    
    results = None
    with ThreadPoolExecutor(max_workers = 8) as executor:
        # results = {(*thp, executor.submit(thread_func, *thp)) for thp in threads}
        results = executor.map(thread_func, threads)
    for res in results:
        # print(res)
        edit_distances[res[0], res[1]] = res[2]
    with open(pickle_save, "wb") as outf:
        pickle.dump(edit_distances, outf)
        # pickle.dump()


if __name__=="__main__":
    gs = get_graph_strings()
    for g in gs.items():
        graphs.append(Graph(*parse(g[0], g[1])))


    x=1
