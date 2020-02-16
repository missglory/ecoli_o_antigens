import re, collections
import networkx as nx
import matplotlib.pyplot as plt

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

def parse(input_str: str):
    lines = input_str.split("\n")
    if lines[-1] == "": lines = lines[:-1]  
    assert(len(lines) in (0, 1, 3, 5))
    g = nx.DiGraph()
    labels, edge_labels = {}, {}
    if len(lines) == 0: return g
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
    for g_i in range(len(edgess)):
        edges = edgess[g_i]
        for i in range(len(edges)):
            edge = edges[i]
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

    for g_i in range(len(edgess)):
        edges = edgess[g_i]
        for i in range(len(edges)):
            edge = edges[i]
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
    return (g, labels, edge_labels)
    


if __name__=="__main__":
    gs = get_graph_strings()
    graphs = []
    for g in gs.items():
        graphs.append((g[0], *parse(g[1])))
    x=1