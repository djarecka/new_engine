import pytest, pdb

from super_node import SNode

def my_function_1(a):
    return a**2 - 9

def my_function_2(a, b):
    return a * b - 9


def test_single_node_1():
    sn = SNode(function=my_function_1, mapper='a', inputs={"a" : [3, 1, 8]})
    #pdb.set_trace()
    sn.run()
    assert (sn.output == [0, -8, 55]).all()

@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1, 8], "b":[0, 1, 2]}, [-9, -8, 7]),
        ({"a":[3, 1, 8], "b":[2]}, [-3, -7, 7]),
        ])
def test_single_node_2(inputs_dic, expected_output):
    sn = SNode(function=my_function_2, mapper='a.b', inputs=inputs_dic)
    sn.run()
    assert (sn.output == expected_output).all()


def test_single_node_wrong_mapper():
    with pytest.raises(Exception):
        sn = SNode(function=my_function_2, mapper='a*b', inputs={"a":[3], "b":[0]})

def test_single_node_wrong_input():
    with pytest.raises(Exception):
        sn = SNode(function=my_function_2, mapper='a.b', inputs={"a":[3], "c":[0]})
