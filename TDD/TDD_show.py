"""This page is just to get the Graphical output of TDD"""
from graphviz import Digraph, nohtml

from IPython.display import Image

def TDD_show(tdd):
    edge=[]              
    dot=Digraph(name='reduced_tree')
    dot=layout(tdd.node,dot,edge)
    dot.node('-0','',shape='none')
    dot.edge('-0',str(tdd.node.idx),color="blue",label=str(complex(round(tdd.weight.real,2),round(tdd.weight.imag,2))))
    dot.format = 'png'
    return Image(dot.render('output'))


def layout(node,dot=Digraph(),succ=[]):
    dot.node(str(node.idx), str(node.key), fontname="helvetica",shape="circle",color="red")
    k=0
    if node.successor[k]:
        label1=str(complex(round(node.out_weight[k].real,2),round(node.out_weight[k].imag,2)))
        if not node.successor[k] in succ:
            dot=layout(node.successor[k],dot,succ)
            dot.edge(str(node.idx),str(node.successor[k].idx),style="dotted",color="blue",label=label1)
            if isinstance(node.successor[k].key,str):
                succ.append(node.successor[k])
        else:
            dot.edge(str(node.idx),str(node.successor[k].idx),style="dotted",color="blue",label=label1)
    k=1
    if node.successor[k]:
        label1=str(complex(round(node.out_weight[k].real,2),round(node.out_weight[k].imag,2)))
        if not node.successor[k] in succ:
            dot=layout(node.successor[k],dot,succ)
            dot.edge(str(node.idx),str(node.successor[k].idx),color="blue",label=label1)
            succ.append(node.successor[k])
            if isinstance(node.successor[k].key,str):
                succ.append(node.successor[k])            
        else:
            dot.edge(str(node.idx),str(node.successor[k].idx),color="blue",label=label1)
    return dot
    