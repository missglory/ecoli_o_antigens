import re, collections
import networkx as nx
import matplotlib.pyplot as plt
from plot_tabs import *

class FrozenDict(collections.Mapping):
    """https://stackoverflow.com/questions/2703599/what-would-a-frozen-dict-be"""
    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for pair in self.items():
                self._hash ^= hash(pair)
        return self._hash




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

_dbg_edges = []

def parse_line(edge_iters, g: nx.Graph, labels: dict, ind: int, input_str: str):
    _skip_begin = 0
    node_prev = None
    for node_i in range(len(input_str)):
        node = input_str[node_i].replace(" ", "").replace("\t", "")
        if (len(node) == 0):
            _skip_begin += 1
            continue
        g.add_node(ind, label=node)
        labels[ind] = node
        if not node_prev is None:
            _entity = edge_iters[node_i-_skip_begin]
            name = _entity.group()
            g.add_edge(ind-1, ind, label=name)
        node_prev = node
        ind += 1
    return ind

def parse(input_str: str):
    lines = input_str.split("\n")
    if lines[-1] == "": lines = lines[:-1]  
    assert(len(lines) in (0, 1, 3, 5))
    g = nx.Graph()
    labels = {}
    if len(lines) == 0: return g
    edge_iterss = []
    node_iterss = []
    for i in range(0,len(lines),2):
        # print(lines[i])
        line = lines[i]
        reg = re.compile(r"\(?\d?[<-][NP>]-?\d?\)?")
        res = re.finditer(reg, line)
        _res = re.split(reg, line)
        edge_iterss.append(res)
        node_iterss.append(_res)
    verticalss = []
    retd = {}
    for i in range(1, len(lines), 2):
        verticalss.append(re.finditer(r"|", lines[i]))
        for v in verticalss[-1]:
            pass
    edge_iterss = [list(n) for n in edge_iterss]
    ring_ind = -1
    for i in range(len(lines)):
        l = lines[i].replace(" ", "").replace("\t", "")
        if l[:2] == "->":
            ring_ind = i
            break
    assert(ring_ind % 2 == 0)
    ring_ind //= 2
    edge_iters = edge_iterss[ring_ind]
    node_prev = None
    _skip = 0
    ind = 0
    _skip_last = 0
    ind = parse_line(edge_iters, g, labels, ind, node_iterss[ring_ind])
    last_edge = edge_iters[ind].group() + edge_iters[0].group()
    g.add_edge(ind-1, 0, label=last_edge)
    return (g, labels)
    


if __name__=="__main__":
    gs = get_graph_strings()
    graphs = []
    for g in gs.items():
        graphs.append((g[0], *parse(g[1])))
    x = 1
    pw = PlotWindow()
    for g in graphs:
    # g[0]
        fig = plt.figure()
        if len(g) == 3: nx.draw(g[1], with_labels=True, font_weight='bold', labels=g[2])
        pw.addPlot(fig)
    pw.show()
