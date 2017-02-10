import pytest, pdb
import numpy as np

from node import Node
from workflow import Workflow

from test_node import my_function_1, my_function_1a

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
    pdb.set_trace()
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
    pdb.set_trace()
    assert (wf.output_map["node1"]["out"] == [0, -8, 55]).all()
    assert (wf.output_map["node2"]["out"] == [-9, 55, 3016]).all()
