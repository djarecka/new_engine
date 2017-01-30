import numpy as np
import pytest, pdb
from super_node import SNode
from test_node import my_function_4, my_function_2


def my_function_dot(a, b, **dict):
    return a*b

def my_function_dot_temp(c, d, **dict):
    return c*d

def my_function_4a(ab, c, d, **dict):
    pdb.set_trace()
    return ab - c * d


def my_function_4b(ab, cd, **dict):
    return ab - cd


def test_2nodes_1():
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_2, mapper='a.b', inputs=inputs_1)
    sn2 = SNode(function=my_function_4, mapper='(a.b)x(c.d)', inputs=inputs_2, run_node=False)
    sn1.__add__(sn2)
    sn1.run()
    expected_output = np.array([[1, 3], [0, 2]])
    assert (sn1.output == expected_output).all()


def test_2nodes_1a():
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_2, mapper='a.b', inputs=inputs_1, outp_name="ab")
    sn2 = SNode(function=my_function_4, mapper='(a.b)x(c.d)', inputs=inputs_2, outp_name="out", 
                run_node=False)
    sn1.__add__(sn2)
    sn1.run()
    expected_output = np.array([[1, 3], [0, 2]])
    expected_inp_ab = np.array([-6, -7])
    pdb.set_trace()
    assert (sn1.output == expected_output).all()
    assert (sn1.inputs["out"] == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()


def test_2nodes_1b():
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_dot, mapper='a.b', inputs=inputs_1, outp_name="ab")
    sn2 = SNode(function=my_function_4a, mapper='(ab)x(c.d)', inputs=inputs_2, run_node=False)
    sn1.__add__(sn2)
    sn1.run()
    #pdb.set_trace()
    expected_output = np.array([[1, 3], [0, 2]])
    expected_inp_ab = np.array([[3, 3], [2, 2]])
    assert (sn1.output == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()


def test_3nodes():
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_dot, mapper='a.b', inputs=inputs_1, outp_name="ab")
    sn2 = SNode(function=my_function_dot_temp, mapper='c.d', inputs=inputs_2, outp_name="cd")
    sn3 = SNode(function=my_function_4b, mapper='(ab)x(cd)', run_node=False)
    sn1.__add__(sn2)
    sn1.__add__(sn3)
    sn1.run()
    expected_output = np.array([[1, 3], [0, 2]])
    expected_inp_ab = np.array([[3, 3], [2, 2]])
    expected_inp_cd = np.array([[2, 0], [2, 0]])
    assert (sn1.output == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()            
    assert (sn1.inputs["cd"] == expected_inp_cd).all()


