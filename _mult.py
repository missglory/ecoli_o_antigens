from reg import get_graph_strings

gs = get_graph_strings()
gss = {}
for g in gs.items():
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
    gss[nm] = "\n".join(linesm)

with open("datam.txt", "w") as outf:
    for g in gss.items():
        outf.write(g[0] + "\n" + g[1] + "\n")