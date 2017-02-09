import numpy as np
import pytest, pdb

from node import Node

from test_node import my_function_1, my_function_2, my_function_4, my_function_3dot 
from test_multi_nodes import my_function_dot, my_function_4a


def test_reducer_1():
    sn = Node(Interface=my_function_1, mapper='a', reducer=["a"]) 
    sn.inputs = {"a" : [3, 1, 8]}
    sn.run()
    assert (sn.output["out"] == [0, -8, 55]).all()
    assert sn.output_reduced["out"] == [([3], [0]), ([1], [-8]), ([8], [55])]


@pytest.mark.parametrize("inputs_dic, expected_output", [
        ({"a":[3, 1, 8], "b":[0, 1, 2]}, ([-9, -8, 7], [([0], [-9]), ([1], [-8]), ([2], [7])])),
        pytest.mark.xfail(({"a":[3, 1, 8], "b":[2]}, ([-3, -7, 7], [([2], [-3, -7, 7])]))),
        ])
def test_reducer_2(inputs_dic, expected_output):
    sn = Node(Interface=my_function_2, mapper='a.b', reducer=["b"]) # TODO outp_name="ff"
    sn.inputs=inputs_dic
    sn.run()
    #pdb.set_trace()
    assert (sn.output["out"] == expected_output[0]).all()
    #assert (sn.inputs["ff"] == expected_output[0]).all()
    for (i,out) in enumerate(sn.output_reduced["out"]):
        assert out[0] == expected_output[1][i][0]
        assert (out[1] == expected_output[1][i][1]).all()


@pytest.mark.parametrize("inputs_dic, expected_output, expected_redu", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]]), 
         [([3], [-6, -3, 3]), ([1], [-8, -7, -5])]),
         ({"a":[[3, 1], [30, 10]], "b":[1, 2, 4]},
         np.array([[[-6, -3, 3], [-8, -7, -5]],[[21, 51, 111],[1, 11, 31]]]),
         [([3], [-6, -3, 3]), ([1], [-8, -7, -5]), ([30], [21, 51, 111]), ([10], [1, 11, 31])]),
        ({"a":[3, 1], "b":[2]}, np.array([[-3], [-7]]), [([3], [-3]), ([1], [-7])]),
        ])
def test_reducer_3(inputs_dic, expected_output, expected_redu):
    sn = Node(Interface=my_function_2, mapper='axb', reducer=["a"])
    sn.inputs = inputs_dic
    sn.run()
    #pdb.set_trace()
    assert (sn.output["out"] == expected_output).all()
    for (i,out) in enumerate(sn.output_reduced["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


@pytest.mark.parametrize("inputs_dic, expected_output, expected_redu", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]]),
         [([1], [-6, -8]), ([2], [-3, -7]), ([4], [3, -5])]),
        ])
def test_reducer_3a(inputs_dic, expected_output, expected_redu):
    sn = Node(Interface=my_function_2, mapper='axb', reducer=["b"]) 
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()
    for (i,out) in enumerate(sn.output_reduced["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


@pytest.mark.parametrize("inputs_dic, expected_output, expected_redu", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]]),
         [([1, 3], [-6]), ([1, 1], [-8]), ([2, 3], [-3]), ([2, 1], [-7]), 
          ([4, 3], [3]), ([4,1], [-5])]),
        ])
def test_reducer_3b(inputs_dic, expected_output, expected_redu):
    sn = Node(Interface=my_function_2, mapper='axb', reducer=["b", "a"])
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()
    for (i,out) in enumerate(sn.output_reduced["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()

@pytest.mark.parametrize("inputs_dic, expected_output, expected_redu", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]]),
         [([3, 1], [-6]), ([3, 2], [-3]), ([3, 4], [3]), 
          ([1, 1], [-8]), ([1, 2], [-7]), ([1, 4], [-5])]),
        ])
def test_reducer_3c(inputs_dic, expected_output, expected_redu):
    sn = Node(Interface=my_function_2, mapper='axb', reducer=["a", "b"])
    sn.inputs = inputs_dic
    sn.run()
    assert (sn.output["out"] == expected_output).all()
    for (i,out) in enumerate(sn.output_reduced["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()



@pytest.mark.parametrize("reducer_var, expected_redu", [
        ("a", [([3], [1, 3]) , ([1], [0, 2])]),
        ("b", [([1], [1, 3]) , ([2], [0, 2])]),
        ("c", [([1], [1, 0]) , ([0], [3, 2])]),
        ("d", [([2], [1, 0]) , ([1], [3, 2])]),
        ])
def atest_reducer_4(reducer_var, expected_redu):
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


@pytest.mark.parametrize("reducer_var, reducer_fun, expected_redu", [
        ("a", "sum", [([3], 4) , ([1], 2)]),
        ("b", "min", [([1], 1) , ([2], 0)]),
        ("c", "sum", [([1], 1) , ([0], 5)]),
        ("d", "max", [([2], 1) , ([1], 3)]),
        ])
def atest_reducer_4a(reducer_var, reducer_fun, expected_redu):
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_2, mapper='a.b', inputs=inputs_1, outp_name="ab", redu=True)
    sn2 = SNode(function=my_function_4, mapper='(a.b)x(c.d)', inputs=inputs_2, outp_name="out",
                run_node=False, redu=True)
    sn1.__add__(sn2)
    rn = ReduNode(reducer=[reducer_var], reducer_function=reducer_fun)
    sn1.__add__(rn)
    sn1.run()
    expected_output = np.array([[1, 3], [0, 2]])
    expected_inp_ab = np.array([-6, -7])
    assert (sn1.output["out"] == expected_output).all()
    assert (sn1.inputs["out"] == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()
    for (i,out) in enumerate(sn1.output_reduced["out"]):
        assert out == expected_redu[i]


@pytest.mark.parametrize("reducer_var, expected_redu", [
        ("a", [([3], [1, 3]) , ([1], [0, 2])]),
        ("b", [([1], [1, 3]) , ([2], [0, 2])]),
        pytest.mark.xfail(("ab", [([3], [1, 3]) , ([2], [0, 2])])), #should be implemented??
        ("c", [([1], [1, 0]) , ([0], [3, 2])]),
        ("d", [([2], [1, 0]) , ([1], [3, 2])]),
        ])
def atest_reducer_5(reducer_var, expected_redu):
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_dot, mapper='a.b', inputs=inputs_1, outp_name="ab", redu=True)
    sn2 = SNode(function=my_function_4a, mapper='(ab)x(c.d)', inputs=inputs_2, run_node=False, redu=True)
    sn1.__add__(sn2)
    rn = ReduNode(reducer=[reducer_var])
    sn1.__add__(rn)
    sn1.run()
    expected_output = np.array([[1, 3], [0, 2]])
    expected_inp_ab = np.array([[3, 3], [2, 2]])
    assert (sn1.output["out"] == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()
    for (i,out) in enumerate(sn1.output_reduced["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()



@pytest.mark.parametrize("reducer_var, expected_redu", [
        ("a", [([3], [[3, 0], [6, 0]]), ([1], [[1, 0], [2, 0]])]),
        ("b", [([1], [[3, 0], [1, 0]]), ([2], [[6, 0], [2, 0]])]),
        ("c", [([1], [[3, 6], [1, 2]]), ([0], [[0, 0], [0, 0]])])
        ])
def test_reducer_6(reducer_var, expected_redu):
    sn = Node(Interface=my_function_3dot, mapper='(axb)xc', reducer=[reducer_var])
    sn.inputs = {"a":[3, 1], "b":[1, 2], "c": [1,0]}
    sn.run()
    expected_output = [[[3, 0], [6, 0]], [[1, 0], [2, 0]]]
    #pdb.set_trace()
    assert (sn.output["out"] == expected_output).all()
    for (i,out) in enumerate(sn.output_reduced["out"]):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


#pomyslec czy drugo node musi miec redu=true
#zakldamy chyba, ze postac f-cji wychodzacej z f-cji mapper jest taka sama??

#jesli jest named output, to trzeba sprawdzac, czy z rzeczy mappera nie ma w reduce i ewntualnie tez jakos korelowac (nowy slownik?)
#chwilowo zrobic, ze reduzer tylko na koncu?
