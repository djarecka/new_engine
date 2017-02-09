import pytest, pdb
import numpy as np

from node import Node

def my_function_1(a, **dict):
    return a**2 - 9

def my_function_1a(a1a, **dict):
    return a1a**2 - 9

def my_function_2(a, b, **dict):
    return a * b - 9

def my_function_2a(a, b, **dict):
    return a+b, a-b

def my_function_3(a, b, c, **dict):
    return a * b - c

def my_function_4(a, b, c, d, **dict):
    return a * b - c * d

def my_function_3dot(a, b, c, **dict):
    return a * b * c


def test_single_node_1():
    sn = Node(Interface=my_function_1, mapper='a')
    sn.inputs = {"a" : [3, 1, 8]}
    sn.run()
    assert (sn.output["out"] == [0, -8, 55]).all()


def test_single_node_1a():
    sn = Node(Interface=my_function_1, mapper='(a)')
    sn.inputs = {"a" : [3, 1, 8]}
    sn.run()
    assert (sn.output["out"] == [0, -8, 55]).all()

def test_single_node_1b():
    sn = Node(Interface=my_function_1a, mapper='a1a')
    sn.inputs = {"a1a" : [3, 1, 8]}
    sn.run()
    assert (sn.output["out"] == [0, -8, 55]).all()


def test_single_node_1c():
    sn = Node(Interface=my_function_1, mapper='a', output_name=["out_1"])
    sn.inputs = {"a" : [3, 1, 8]}
    sn.run()
    assert (sn.output["out_1"] == [0, -8, 55]).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1, 8], "b":[0, 1, 2]}, [-9, -8, 7]),
        ({"a":[3, 1, 8], "b":[2]}, [-3, -7, 7]),
        ])
def test_single_node_2(inputs_dic, expected_output):
    sn = Node(Interface=my_function_2, mapper='a.b')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1, 8], "b":[0, 1, 2]}, ([3, 2, 10], [3, 0, 6])),
        ({"a":[3, 1, 8], "b":[2]}, ([5, 3, 10], [1, -1, 6])),
        ])
def test_single_node_2a(inputs_dic, expected_output):
    outp_name = ["out1", "out2"]
    sn = Node(Interface=my_function_2a, mapper='a.b', output_name=outp_name)
    sn.inputs = inputs_dic
    sn.run()
    for i, exp in enumerate(expected_output):
        assert (sn.output[outp_name[i]] == exp).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]])),
        ({"a":[[3, 1]], "b":[1, 2, 4]}, np.array([[[-6, -3, 3], [-8, -7, -5]]])),
        ({"a":[[3, 1], [30, 10]], "b":[1, 2, 4]},
         np.array([[[-6, -3, 3], [-8, -7, -5]],[[21, 51, 111],[1, 11, 31]]])),
        ({"a":[3, 1], "b":[2]}, np.array([[-3], [-7]])),
        ])
def test_single_node_3(inputs_dic, expected_output):
    sn = Node(Interface=my_function_2, mapper='axb')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]])),
        ({"a":[[3, 1]], "b":[1, 2, 4]}, np.array([[[-6, -3, 3], [-8, -7, -5]]])),
        ])
def test_single_node_3a(inputs_dic, expected_output):
    sn = Node(Interface=my_function_2, mapper='(a)x(b)')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_4(inputs_dic, expected_output):
    sn = Node(Interface=my_function_3, mapper='(a.b).c')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()

@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_5(inputs_dic, expected_output):
    sn = Node(Interface=my_function_3, mapper='a.(b.c)')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c":[0, 1]}, [3, 1]),
        ])
def test_single_node_5a(inputs_dic, expected_output):
    sn = Node(Interface=my_function_3, mapper='(a.(b.c))')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [[1,0],[1,2]]}, np.array([[2, 6], [0, 0]])),
        ])
def test_single_node_6(inputs_dic, expected_output):
    sn = Node(Interface=my_function_3, mapper='(axb).c')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0]}, np.array([[2, 6], [0, 2]])),
        ])
def test_single_node_7(inputs_dic, expected_output):
    sn = Node(Interface=my_function_3, mapper='ax(b.c)')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0]}, np.array([[2, 0], [6, 2]])),
        ])
def test_single_node_8(inputs_dic, expected_output):
    sn = Node(Interface=my_function_3, mapper='(b.c)xa')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0], "d": [2,1]}, np.array([[1, 3], [0, 2]])),
        ])
def test_single_node_9(inputs_dic, expected_output):
    sn = Node(Interface=my_function_4, mapper='(a.b)x(c.d)')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1], "b":[1, 2], "c": [1,0]}, np.array([[[3, 0], [6, 0]], [[1, 0], [2, 0]]])),
        ])
def test_single_node_10(inputs_dic, expected_output):
    sn = Node(Interface=my_function_3dot, mapper='(axb)xc')
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()


@pytest.mark.parametrize("mapper_str", ['a*b', '(a.b', 'axb)', 'a,b'])
def test_single_node_wrong_mapper(mapper_str):
    with pytest.raises(Exception):
        sn = Node(Interface=my_function_2, mapper=mapper_str) 
        sn.inputs = {"a":[3], "b":[0]}
        sn.run()


@pytest.mark.parametrize("inputs_dic", [
        {"a":[[3, 1], [0,0]], "b":[1, 2, 0]},
        {"a":[[3, 1], [0,0], [1, 1]], "b":[1, 2, 0]}, # think if this should work
        {"a":[[3, 1, 1], [0,0, 0]], "b":[1, 2, 0]},  # think if this should work
        ])
def test_single_node_wrong_input(inputs_dic):
    with pytest.raises(Exception):
        sn = Node(Interface=my_function_2, mapper='a.b') 
        sn.inputs = inputs_dic
        sn.run()

@pytest.mark.xfail # pomyslec czy to powinno fail
def test_single_node_wrong_key():
    with pytest.raises(Exception):
        sn = Node(Interface=my_function_2, mapper='a.b') 
        sn.inputs = {"a":[3], "c":[0]}


# TODO: czy nie powinnam jednak moc wykorzystac a1a w fun_1?? czyli uzyc arg_map
# TODO: co powinno byc sprawdzane przy inpucie, kiedy powinien dawac blad?
