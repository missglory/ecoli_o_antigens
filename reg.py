import re, collections
import networkx as nx
import matplotlib.pyplot as plt
from collections import namedtuple
import numpy as np
import pickle, time
from concurrent.futures import ThreadPoolExecutor
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)-15s - %(message)s')
Graph = namedtuple("Graph", "name g nlabels elabels src_str")


def repeat_oantigen(g:tuple, mult:int=1):
    nm, ls = g
    lines = ls.split("\n")
    if lines[-1] == "": lines = lines[:-1]  
    maxlen = 0
    linesm = []
    for line in lines:
        maxlen = max(maxlen, len(line))
    for line in lines:
        linesm.append((line + " " * (maxlen - len(line))) * int(mult))
    for i in range(len(linesm)):
        assert(len(linesm[i]) == len(linesm[0]))
    return (nm, "\n".join(linesm))


def num_cycle_nodes(ls:str):
    if len(ls) == 0: return 0
    cycle_i = -1
    lines = ls.split("\n")
    for i, line in enumerate(lines):
        if line.replace(" ", "")[:2] == "->":
            cycle_i = i
            break
    assert(not cycle_i == -1)
    nodes_res = re.split(r"\(?\d?[<-][NP>]P?-?>?\d?\)?", lines[cycle_i].replace(" ", ""))
    res = int(len(nodes_res) - int(nodes_res[0] == "") - int(nodes_res[-1] == ""))
    return res


def get_graph_strings():
    graph_strings = {}
    with open("data.txt", "r") as file:
        next_name, next_str = "", ""
        for line in file.readlines():
            if not re.search(r"\||-", line):
                if not len(next_name) == 0 and not len(next_str) == 0:
                    valid_name = next_name.replace("\t","").replace("\n","")
                    _incr, name_postfix = 2, ""
                    while valid_name + name_postfix in graph_strings:
                        name_postfix = "." + str(_incr)
                        _incr += 1
                    graph_strings[valid_name + name_postfix] = next_str
                    next_str = ""
                next_name = line
            else:
                next_str += line
    return graph_strings


global_labels = {}
global_label_idx = 0
def get_label_idx(lbl: str):
    idx = -1
    global global_label_idx
    try:
        idx = global_labels[lbl]
    except:
        global_labels[lbl] = global_label_idx
        idx = global_label_idx
        global_label_idx += 1
    assert(not idx == -1)
    return idx

def add_edge(edge_labels: dict, g: nx.Graph, n1: int, n2: int, lbl: str):
    lbl = lbl.replace(" ", "").replace("->->", "->")
    g.add_edge(n1, n2, i=get_label_idx(lbl), label=lbl)
    edge_labels[(n1,n2)] = lbl


def parse(inp_g:tuple):
    nm, input_str = inp_g
    lines = input_str.split("\n")
    while len(lines) > 0 and lines[-1] == "": lines = lines[:-1]  
    assert(len(lines) in (0, 1, 3, 5))
    g = nx.DiGraph(name=nm)
    labels, edge_labels = {}, {}
    if len(lines) == 0: return Graph(nm, g, labels, edge_labels, input_str)
    edgess = []
    nodess = []
    for i in range(0,len(lines),2):
        line = lines[i]
        reg = re.compile(r"\(?\d?[<-][NP>] *P?-?>?\d?\)?")
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
                g.add_node(ind, i=get_label_idx(bc), label=bc)
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
    return Graph(nm, g, labels, edge_labels, input_str)
    

def nmatch(n1, n2):
    return not (len(n1) == 0 or len(n2) == 0) and n1["i"]==n2["i"]

def ematch(e1, e2):
    return e1["i"] == e2["i"]


edit_distances = None 

def gcd(a:int, b:int):
    """Compute the greatest common divisor of a and b"""
    while b:
        a, b = b, a % b
    return a

def lcm(a:int, b:int):
    """Compute the lowest common multiple of a and b"""
    return a * b // gcd(a, b)

graphs = []
_gfc = 0
_gtime = 0
def thread_func(tup: tuple):
    i, j = tup
    gi, gj = graphs[i], graphs[j]
    ni, nj = num_cycle_nodes(gi.src_str), num_cycle_nodes(gj.src_str)
    repeat_lcm = ni
    if (not ni == nj):
          repeat_lcm = lcm(ni, nj)        
          imult = repeat_lcm // ni
          if imult > 1:
              istr = repeat_oantigen((gi.name, gi.src_str), imult)
              gi = parse(istr)
          jmult = repeat_lcm // nj
          if jmult > 1:
              jstr = repeat_oantigen((gj.name, gj.src_str), jmult)
              gj = parse(jstr)

    logging.warning(f"start {gi.name}, {gj.name}.\nlcm: {repeat_lcm}, m: {repeat_lcm//ni}, {repeat_lcm//nj} ({ni},{nj})")
    fname = "rep_graphs/%s"+str(i)+"_"+str(j)+"_"+gi.name.replace(" ", "_")+"___"+gj.name.replace(" ", "_")+".pkl"
    # try:
    #     with open(fname%"g", "rb") as in_pkl:
    #         ob = pickle.load(in_pkl)
    #         assert(ni == ob[0][0])
    #         assert(nj == ob[0][1])
    #         assert(repeat_lcm == ob[0][2])
    #         assert(gi.name == ob[1].name)
    #         assert(gj.name == ob[2].name)
    #         assert(i == ob[4])
    #         assert(j == ob[5])
    #         logging.warning(f"deserialize {gi.name}, {gj.name} (m: {repeat_lcm//ni}, {repeat_lcm//nj})")
    #         return (i,j,ob[3][-1])
    # except: pass

    # with open(fname % "_g", "wb+") as outf:
        # pickle.dump(((ni, nj, repeat_lcm, repeat_lcm // ni, repeat_lcm // nj), gi, gj), outf)
    _start_time = time.time()
    ed = nx.optimize_graph_edit_distance(gi.g, gj.g, node_match=nmatch, edge_match=ematch)
    _vs = []
    for v in ed:
        _vs.append(v)
    _end_time = time.time()
    global _gfc
    global _gtime
    logging.warning(f"finish calc {gi.name}, {gj.name}. Time: {_end_time - _gtime:.3f}. Num of finished: {_gfc}. lcm: {repeat_lcm}, multipliers: {repeat_lcm//ni}, {repeat_lcm//nj} ({ni},{nj})")
    _gfc += 1
    with open(fname % "g", "wb+") as outf:
        pickle.dump(((ni, nj, repeat_lcm, repeat_lcm // ni, repeat_lcm // nj),
            gi, gj, _vs, i, j), outf)

    return (i, j, _vs[-1])
    # , ni ,repeat_gcd, repeat_gcd // ni, repeat_gcd // nj)


def calc_edit_distances(graphs:list, pickle_save = "edit_dists_cld.pkl"):
    _start_time = time.time()
    _l = len(graphs)
    global _gtime
    _gtime = time.time()
    edit_distances = np.zeros((_l, _l))
    threads = []

    _len = 2
    _inds = []
    for i, g in enumerate(graphs):
        if num_cycle_nodes(g.src_str) == _len:
            _len += 1
            _inds.append((i, g.name))
        if _len > 5:
            break
    for _i, i in enumerate(_inds):
        for _j, j in enumerate(_inds):
            if not _j > _i: continue
            threads.append((i,j))
    
    results = []
    with ThreadPoolExecutor(max_workers = 8) as executor:
        results = executor.map(thread_func, threads)
    for res in results:
        edit_distances[res[0], res[1]] = res[2]
        edit_distances[res[1], res[0]] = res[2]
    with open(pickle_save, "wb+") as outf:
        pickle.dump(edit_distances, outf)
    _end_time = time.time()
    logging.warning(f"TOTAL TIME: {_end_time - _start_time}")
    return edit_distances



if __name__=="__main__":
    gs = get_graph_strings()
    for g in gs.items():
        if len(g[1]) > 0: 
            graphs.append(Graph(*parse(g)))
    calc_edit_distances(graphs)

    x=1

