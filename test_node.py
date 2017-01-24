import pytest, pdb
import numpy as np

from super_node import SNode

def my_function_1(a):
    #pdb.set_trace()
    return a**2 - 9

def my_function_2(a, b):
    #pdb.set_trace()
    return a * b - 9

def my_function_3(a, b, c):
    return a * b - c

def my_function_4(a, b, c, d):
    return a * b - c * d


def test_single_node_1():
    sn = SNode(function=my_function_1, mapper='a', inputs={"a" : [3, 1, 8]})
    #pdb.set_trace()
    sn.run()
    pdb.set_trace()
    assert (sn.output == [0, -8, 55]).all()

@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1, 8], "b":[0, 1, 2]}, [-9, -8, 7]),
        ({"a":[3, 1, 8], "b":[2]}, [-3, -7, 7]),
        ])
def test_single_node_2(inputs_dic, expected_output):
    sn = SNode(function=my_function_2, mapper='a.b', inputs=inputs_dic)
    sn.run()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2]}, np.array([[-6, -8], [-3, -7]])),
        ])
def test_single_node_3(inputs_dic, expected_output):
    sn = SNode(function=my_function_2, mapper='axb', inputs=inputs_dic)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()

@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_4(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='(a.b).c', inputs=inputs_dic)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()

@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_5(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='a.(b.c)', inputs=inputs_dic)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [[1,0],[1,2]]}, np.array([[2, 1], [5, 0]])),
        ])
def test_single_node_6(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='(axb).c', inputs=inputs_dic)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0]}, np.array([[2, 0], [6, 2]])),
        ])
def test_single_node_7(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='ax(b.c)', inputs=inputs_dic)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0]}, np.array([[2, 6], [0, 2]])),
        ])
def test_single_node_8(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='(b.c)xa', inputs=inputs_dic)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()

@pytest.mark.xfail
@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0], "d": [2,1]}, np.array([[1, 0], [3, 2]])),
        ])
def test_single_node_9(inputs_dic, expected_output):
    sn = SNode(function=my_function_4, mapper='(a.b)x(c.d)', inputs=inputs_dic)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()



def test_single_node_wrong_mapper():
    with pytest.raises(Exception):
        sn = SNode(function=my_function_2, mapper='a*b', inputs={"a":[3], "b":[0]})

def test_single_node_wrong_input():
    with pytest.raises(Exception):
        sn = SNode(function=my_function_2, mapper='a.b', inputs={"a":[3], "c":[0]})
