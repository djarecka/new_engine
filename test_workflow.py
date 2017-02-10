import pytest, pdb
import numpy as np

from node import Node
from workflow import Workflow

from test_node import my_function_1, my_function_1a,  my_function_2, my_function_2a

def test_workflow_single_node_1():
    sn = Node(Interface=my_function_1, mapper='a')
    sn.inputs = {"a" : [3, 1, 8]}
    wf = Workflow()
    wf.add_node(sn)
    wf.run()
    #pdb.set_trace()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()


def test_workflow_single_node_2():
    sn = Node(Interface=my_function_1, mapper='a')
    sn.inputs = {"a" : [3, 1, 8]}
    sn.name = "just_a_node"
    wf = Workflow()
    wf.add_node(sn)
    wf.run()
    #pdb.set_trace()
    assert (wf.output_map["just_a_node"]["out"] == [0, -8, 55]).all()


def test_workflow_mult_nodes_1():
    sn1 = Node(Interface=my_function_1, mapper='a')
    sn1.inputs = {"a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_1a, mapper='a1a')
    sn2.inputs = {"a1a" : [1, 8, 3]}
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    #pdb.set_trace()
    wf.run()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-8, 55, 0]).all()


def test_workflow_mult_nodes_connect_1():
    sn1 = Node(Interface=my_function_1, mapper='a')
    sn1.inputs = {"a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_1a, mapper='a1a')
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.connect(sn1, "out", sn2, "a1a")
    wf.run()
    #pdb.set_trace()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, 55, 3016]).all()

def test_workflow_mult_nodes_connect_reduce_1():
    sn1 = Node(Interface=my_function_1, mapper='a')
    sn1.inputs = {"a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_1a, mapper='a1a', reducer=["a"])
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.connect(sn1, "out", sn2, "a1a")
    wf.run()
    #pdb.set_trace()                                                                                            
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, 55, 3016]).all()
    
    expected_redu = [([3], -9), ([1], 55), ([8], 3016)]
    for (i,out) in enumerate(wf.output_map_reduced["node2"]["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()



def test_workflow_mult_nodes_connect_reduce_2():
    sn1 = Node(Interface=my_function_1a, mapper='a1a')
    sn1.inputs = {"a1a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_2, mapper='a.b', reducer=["a1a"])
    sn2.inputs = {"b" : [1, 1, 1]}
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.connect(sn1, "out", sn2, "a")
    wf.run()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, -17, 46]).all()
    expected_redu = [([3], -9), ([1], -17), ([8], 46)]
    for (i,out) in enumerate(wf.output_map_reduced["node2"]["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


def test_workflow_mult_nodes_connect_reduce_2a():
    sn1 = Node(Interface=my_function_1a, mapper='a1a')
    sn1.inputs = {"a1a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_2, mapper='a.b', reducer=["a1a"])
    sn2.inputs = {"b" : [1, 1, 1]}
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.connect(sn1, ["out"], sn2, ["a"])
    wf.run()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, -17, 46]).all()
    expected_redu = [([3], -9), ([1], -17), ([8], 46)]
    for (i,out) in enumerate(wf.output_map_reduced["node2"]["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


# TODO
@pytest.mark.xfail
def test_workflow_mult_nodes_connect_reduce_3():
    sn1 = Node(Interface=my_function_1a, mapper='a1a')
    sn1.inputs = {"a1a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_2, mapper='axb', reducer=["a1a"])
    sn2.inputs = {"b" : [1, 1, 1]}
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.connect(sn1, "out", sn2, "a")
    wf.run()
    pdb.set_trace()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, -17, 46]).all()
    expected_redu = [([3], -9), ([1], -17), ([8], 46)]
    for (i,out) in enumerate(wf.output_map_reduced["node2"]["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()

# TODO
def test_workflow_mult_nodes_connect_reduce_4():
    sn1 = Node(Interface=my_function_1a, mapper='a1a')
    sn1.inputs = {"a1a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_2, mapper='bxa', reducer=["a1a"])
    sn2.inputs = {"b" : [1, 1, 1]}
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.connect(sn1, "out", sn2, "a")
    wf.run()
    pdb.set_trace()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, -17, 46]).all()
    expected_redu = [([3], -9), ([1], -17), ([8], 46)]
    for (i,out) in enumerate(wf.output_map_reduced["node2"]["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()

# TODO
@pytest.mark.xfail
def test_workflow_mult_nodes_connect_reduce_5():
    sn1 = Node(Interface=my_function_1a, mapper='a1a')
    sn1.inputs = {"a1a" : [3, 1, 8]}
    sn2 = Node(Interface=my_function_2a, mapper='a.b', reducer=["a1a"], output_name=["out_1", "out_2"])
    sn2.inputs = {"b" : [1, 1, 1]}
    wf = Workflow()
    wf.add_node(sn1)
    wf.add_node(sn2)
    wf.connect(sn1, "out", sn2, "a")
    wf.run()
    pdb.set_trace()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, -17, 46]).all()
    expected_redu = [([3], -9), ([1], -17), ([8], 46)]
    for (i,out) in enumerate(wf.output_map_reduced["node2"]["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()



@pytest.mark.parametrize("reducer_var, expected_redu", [
        ("a", [([3], [1, 3]) , ([1], [0, 2])]),
        ("b", [([1], [1, 3]) , ([2], [0, 2])]),
        ("c", [([1], [1, 0]) , ([0], [3, 2])]),
        ("d", [([2], [1, 0]) , ([1], [3, 2])]),
        ])
def atest_workflow_mult_nodes_connect_reduce_1(reducer_var, expected_redu):
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_2, mapper='a.b', inputs=inputs_1, outp_name="ab", redu=True)
    sn2 = SNode(function=my_function_4, mapper='(a.b)x(c.d)', inputs=inputs_2, outp_name="out",
                run_node=False, redu=True)
    sn1.__add__(sn2)
    rn = ReduNode(reducer=[reducer_var])
    sn1.__add__(rn)
    sn1.run()
    expected_output = np.array([[1, 3], [0, 2]])
    expected_inp_ab = np.array([-6, -7])
    assert (sn1.output["out"] == expected_output).all()
    assert (sn1.inputs["out"] == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()
    for (i,out) in enumerate(sn1.output_reduced["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()
