import pytest, pdb
import numpy as np

from node import Node
from workflow import Workflow



def function_1f(a, b, c, **dict):
    return a, a, a

def function_1g(i, j, k, **dict):
    return 2*i, 2*j, 2*k

def function_1h(l, m, n, **dict):
    return l+1, m+1, n+1

@pytest.mark.xfail
def test_example_1():
    sn1 = Node(Interface=function_1f, mapper='a.(bxc)', output_name=["x", "y", "z"])
    sn2 = Node(Interface=function_1g, mapper='i.j.k', output_name=["r", "s", "t"])
    sn3 = Node(Interface=function_1h, mapper='(lxn)', output_name=["e", "f", "g"])#, reducer=["a"])

    sn1.inputs = {"a": [[1,2]], "b": [3], "c": [4,5]}
    # TODO example has two n
    #sn3.inputs = {"n": [6, 7]}

    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.add_node(sn3)

    wf.connect(sn1, ["x", "y", "z"], sn2, ["i", "j", "k"])
    wf.connect(sn2, ["r", "s", "t"], sn3, ["l", "m", "n"])

    wf.run()
    pdb.set_trace()
    for output_name in ["x", "y", "z"]:
        assert (wf.output_map["node1"][output_name] == [1,2]).all()

    for output_name in ["r", "s", "t"]:
        assert (wf.output_map["node2"][output_name] == [2,4]).all()

    for output_name in ["e", "f", "g"]:
        assert (wf.output_map["node3"][output_name] == [3,5]).all()







def function_2f(a, **dict):
    return a, a, a

def function_2g(i, j, k, **dict):
    return 2*i, 2*j, 2*k

def function_2h(l, m, n, **dict):
    return l+1, m+1, n+1


def test_example_2():
    sn1 = Node(Interface=function_2f, mapper='a', output_name=["x", "y", "z"])
    sn2 = Node(Interface=function_2g, mapper='i.j.k', output_name=["r", "s", "t"])
    sn3 = Node(Interface=function_2h, mapper='l.m.n', output_name=["e", "f", "g"], reducer=["a"])
    
    sn1.inputs = {"a": [1,2]}
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.add_node(sn3)

    wf.connect(sn1, ["x", "y", "z"], sn2, ["i", "j", "k"])
    wf.connect(sn2, ["r", "s", "t"], sn3, ["l", "m", "n"])

    wf.run()
    
    for output_name in ["x", "y", "z"]:
        assert (wf.output_map["node1"][output_name] == [1,2]).all()
        
    for output_name in ["r", "s", "t"]:
        assert (wf.output_map["node2"][output_name] == [2,4]).all()

    for output_name in ["e", "f", "g"]:
        assert (wf.output_map["node3"][output_name] == [3,5]).all()


    # reduced outputs
    for output_name in ["e", "f", "g"]:
        expected_redu = [([1], 3), ([2], 5)]
        for (i,out) in enumerate(wf.output_map_reduced["node3"][output_name]):
            assert out[0] == expected_redu[i][0]
            assert (out[1] == expected_redu[i][1]).all()

