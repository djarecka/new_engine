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

# TODO: test np.outer(self.inputs_usr["a"], self.inputs_usr["b"]) = \
# self.inputs["a"] * self.inputs["b"]

def test_single_node_1():
    sn = SNode(function=my_function_1, mapper='a', inputs={"a" : [3, 1, 8]})
    #pdb.set_trace()
    sn.run()
    #pdb.set_trace()
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
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]])),
        ({"a":[[3, 1]], "b":[1, 2, 4]}, np.array([[[-6, -3, 3], [-8, -7, -5]]])),
        ({"a":[[3, 1], [30, 10]], "b":[1, 2, 4]}, 
         np.array([[[-6, -3, 3], [-8, -7, -5]],[[21, 51, 111],[1, 11, 31]]])),
        ({"a":[3, 1], "b":[2]}, np.array([[-3], [-7]])),
        ])
def test_single_node_3(inputs_dic, expected_output):
    sn = SNode(function=my_function_2, mapper='axb', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()

@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_4(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='(a.b).c', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()

@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_5(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='a.(b.c)', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_5a(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='(a.(b.c))', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [[1,0],[1,2]]}, np.array([[2, 6], [0, 0]])),
        ])
def test_single_node_6(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='(axb).c', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0]}, np.array([[2, 6], [0, 2]])),
        ])
def test_single_node_7(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='ax(b.c)', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0]}, np.array([[2, 0], [6, 2]])),
        ])
def test_single_node_8(inputs_dic, expected_output):
    sn = SNode(function=my_function_3, mapper='(b.c)xa', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0], "d": [2,1]}, np.array([[1, 3], [0, 2]])),
        ])
def test_single_node_9(inputs_dic, expected_output):
    sn = SNode(function=my_function_4, mapper='(a.b)x(c.d)', inputs=inputs_dic)
    sn.run()
    #pdb.set_trace()
    assert (sn.output == expected_output).all()


@pytest.mark.parametrize("mapper_str", ['a*b', '(a.b', 'axb)', 'a,b'])
def test_single_node_wrong_mapper(mapper_str):
    with pytest.raises(Exception):
        sn = SNode(function=my_function_2, mapper=mapper_str, inputs={"a":[3], "b":[0]})


@pytest.mark.parametrize("inputs_dic", [
        {"a":[[3, 1], [0,0]], "b":[1, 2, 0]},
        {"a":[[3, 1], [0,0], [1, 1]], "b":[1, 2, 0]}, # think if this should work
        {"a":[[3, 1, 1], [0,0, 0]], "b":[1, 2, 0]},  # think if this should work
        ])
def test_single_node_wrong_input(inputs_dic):
    with pytest.raises(Exception):
        sn = SNode(function=my_function_2, mapper='a.b', inputs=inputs_dic)


def test_single_node_wrong_key():
    with pytest.raises(Exception):
        sn = SNode(function=my_function_2, mapper='a.b', inputs={"a":[3], "c":[0]})
