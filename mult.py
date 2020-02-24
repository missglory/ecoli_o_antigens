from reg import get_graph_strings
import re

def repeat_oantigen(g:tuple, mult:int=1):
    nm, ls = g
    lines = ls.split("\n")
    if lines[-1] == "": lines = lines[:-1]  
    maxlen = 0
    linesm = []
    for line in lines:
        maxlen = max(maxlen, len(line))
    for line in lines:
        linesm.append((line + " " * (maxlen - len(line))) * 3)
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
    res = len(nodes_res) - int(nodes_res[0] == "") - int(nodes_res[-1] == "")
    return res


# if __name__=="__main__":
    # gs = get_graph_strings()
    # gss = {}
    # for g in gs.items():
    #     gnew = repeat_oantigen(g, 3)
    #     gss[gnew[0]] = gnew[1]

    # with open("datam.txt", "w") as outf:
    #     for g in gss.items():
    #         outf.write(g[0] + "\n" + g[1] + "\n")