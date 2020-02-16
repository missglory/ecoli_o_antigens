import os
import networkx as nx
import re, collections

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


def check_for_vertical(n, vertical_positions):
    for x in vertical_positions:
        if n["l"] <= x and n["r"] >= x:
            return True
    return False

def overlap(n, e):
    return max(0, min(n["r"], e["r"]) - max(n["l"], e["l"]))

def make_edges(nodes, edges):
    ret = []
    for e in edges:
        select_node1, select_node2 = [], []
        assert(not (\
            e["str"].find("->") == -1 and \
            e["str"].find("-N-") == -1 and \
            e["str"].find("-P-") == -1 and \
            e["str"].find("<-") == -1 \
        ))
        if e["str"].find("<-") == -1:
            select_node1 = [n for n in nodes if n["r"] == e["l"] and n["i"] == e["i"]]
        else:
            select_node1 = [n for n in nodes if n["l"] == e["r"] and n["i"] == e["i"]]
        
        if not e["vert"]:
            select_node2 = [n for n in nodes if n["l"] == e["r"] and n["i"] == e["i"]]
            assert(len(select_node2) == 1)
        else:
            select_node2 = [n for n in nodes if n["vert"] and overlap(n, e) > 0 and abs(n["i"] - e["i"]) == 2]
        assert(len(select_node1) == 1 and len(select_node2) == 1)
        if not e["str"].find("<-") == -1:
            e["str"] = e["str"].replace("<-", "->")
            ret.append((select_node2[0], select_node1[0]))
        else:
            ret.append((select_node1[0], select_node2[0]))
    return ret



def construct():
    graphs = {}
    with open(os.path.abspath("data.txt"), "r") as f:
        lines = f.readlines()
        next_name = ""
        next_str = ""
        next_graph = nx.Graph()
        vertical_edges, vertical_nodes = [], []
        edges = []
        nodes = []
        for li in range(len(lines)):
            l = lines[li]
            if not l.find("|") == -1: 
                next_str += l
                continue
            if l.find("-") == -1:
                if (next_name != ""):
                    # next_graph.add_nodes_from([n["str"] for n in nodes])
                    next_graph = nx.Graph()
                    frozen_nodes = [FrozenDict(n) for n in nodes]
                    next_graph.add_nodes_from(frozen_nodes)
                    frozen_edges = [(FrozenDict(p1), FrozenDict(p2)) for (p1, p2) in make_edges(nodes, edges)]
                    next_graph.add_edges_from(frozen_edges)
                    graphs[next_name] = (next_str, next_graph)
                next_name = l.replace("\t", "").replace("\n", "")
                edges, nodes = [], []
            else:
                vert_edge_positions = set()
                e_pos = 0
                while not e_pos == -1:
                    if (li > len(lines)-1): break
                    e_pos = lines[li+1].find("|", e_pos+1)
                    if not e_pos == -1: vert_edge_positions.add(e_pos)
                e_pos = 0
                while not e_pos == -1:
                    if (li == 0): break
                    e_pos = lines[li-1].find("|", e_pos+1)
                    if not e_pos == -1: vert_edge_positions.add(e_pos)                     
                next_str += l
                find_open_bracket = 0
                find_close_bracket = 1
                _end_crossed = False
                _add_node = False
                while find_open_bracket != -1:
                    if not _end_crossed:
                        _old = find_open_bracket
                        find_open_bracket = l.find("(", _old+1)
                        if not find_open_bracket == -1 and find_open_bracket == l.find("(S)"):
                            find_open_bracket = l.find("(", find_open_bracket+1)
                    else:
                        find_open_bracket = l.find("(")
                    if (_add_node):
                        if (find_open_bracket == -1):
                            _fob = l.find("(")
                            if not _fob == -1 and _fob == l.find("(S)"):
                                _fob = l.find("(", _fob+1)
                                assert(not _fob == -1)
                            node = {"str":l[0:_fob], "l":find_close_bracket, "r":_fob, "i": li, "vert":False}
                        else:
                            node = {"str":l[find_close_bracket+1:find_open_bracket], "l":find_close_bracket, "r":find_open_bracket, "i": li, "vert":False}
                        node["vert"] = check_for_vertical(node, vert_edge_positions)
                        nodes.append(node)
                        _add_node = False
                    if (_end_crossed or find_open_bracket == -1): break
                    if not find_open_bracket == -1 and find_open_bracket == l.find("(S)"):
                        find_close_bracket = l.find(")", find_open_bracket+3)
                    else:
                        find_close_bracket = l.find(")", find_open_bracket+1)
                    if (find_close_bracket == -1): 
                        find_close_bracket = l.find(")")
                        _end_crossed = True

                    # _end_crossed = find_close_bracket < find_open_bracket or find_open_bracket == -1
                    if (not _end_crossed):
                        edge = {"str": l[find_open_bracket:find_close_bracket+1], "l": find_open_bracket, "r": find_close_bracket, "vert": False, "i": li}
                    else:
                        edge = {"str": (l[find_open_bracket:-1] + l[0:find_close_bracket+1]).replace(" ", "").replace("->->", "->"), "l": find_open_bracket, "r": find_close_bracket, "i": li, "vert": False}
                    if (edge["str"].find("-") != -1):
                        edge["vert"] = check_for_vertical(edge, vert_edge_positions)
                        edges.append(edge)
                        _add_node = True

                # next_graph.add_edges_()
    return graphs

graphs = None
if __name__=="__main__":
    graphs = construct()


