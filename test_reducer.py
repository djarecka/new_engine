import numpy as np
import pytest, pdb

from super_node import SNode, ReduNode

from test_node import my_function_1, my_function_2, my_function_4 
from test_multi_nodes import my_function_dot, my_function_4a


def test_reducer_1():
    sn = SNode(function=my_function_1, mapper='a', inputs={"a" : [3, 1, 8]}, redu=True)
    rn = ReduNode(reducer=["a"])
    sn.__add__(rn)
    sn.run()
    assert (sn.output == [0, -8, 55]).all()
    assert sn.output_reduced == [(3, [0]), (1, [-8]), (8, [55])]


@pytest.mark.parametrize("inputs_dic, expected_output", [
        #({"a":[3, 1, 8], "b":[0, 1, 2]}, ([-9, -8, 7], [(0, [-9]), (1, [-8]), (2, [7])])),
        ({"a":[3, 1, 8], "b":[2]}, ([-3, -7, 7], [(2, [-3, -7, 7])])),
        ])
def test_reducer_2(inputs_dic, expected_output):
    sn = SNode(function=my_function_2, mapper='a.b', inputs=inputs_dic, outp_name="ff", redu=True)
    rn = ReduNode(reducer=["b"])
    sn.__add__(rn)
    sn.run()
    assert (sn.output == expected_output[0]).all()
    assert (sn.inputs["ff"] == expected_output[0]).all()
    for (i,out) in enumerate(sn.output_reduced):
        assert out[0] == expected_output[1][i][0]
        assert (out[1] == expected_output[1][i][1]).all()


@pytest.mark.parametrize("inputs_dic, expected_output, expected_redu", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]]), 
         [(3, [-6, -3, 3]), (1, [-8, -7, -5])]),
#        ({"a":[[3, 1]], "b":[1, 2, 4]}, np.array([[[-6, -3, 3], [-8, -7, -5]]])),
#        ({"a":[[3, 1], [30, 10]], "b":[1, 2, 4]},
#         np.array([[[-6, -3, 3], [-8, -7, -5]],[[21, 51, 111],[1, 11, 31]]])),
#        ({"a":[3, 1], "b":[2]}, np.array([[-3], [-7]])),
        ])
def test_reducer_3(inputs_dic, expected_output, expected_redu):
    sn = SNode(function=my_function_2, mapper='axb', inputs=inputs_dic, redu=True)
    rn = ReduNode(reducer=["a"])
    sn.__add__(rn)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()
    for (i,out) in enumerate(sn.output_reduced):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


@pytest.mark.parametrize("inputs_dic, expected_output, expected_redu", [
        ({"a":[3, 1], "b":[1, 2, 4]}, np.array([[-6, -3, 3], [-8, -7, -5]]),
         [(1, [-6, -8]), (2, [-3, -7]), (4, [3, -5])]),
        ])
def test_reducer_3a(inputs_dic, expected_output, expected_redu):
    sn = SNode(function=my_function_2, mapper='axb', inputs=inputs_dic, redu=True)
    rn = ReduNode(reducer=["b"])
    sn.__add__(rn)
    sn.run()
    pdb.set_trace()
    assert (sn.output == expected_output).all()
    for (i,out) in enumerate(sn.output_reduced):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


@pytest.mark.parametrize("reducer_var, expected_redu", [
        ("a", [(3, [1, 3]) , (1, [0, 2])]),
        ("b", [(1, [1, 3]) , (2, [0, 2])]),
        ("c", [(1, [1, 0]) , (0, [3, 2])]),
        ("d", [(2, [1, 0]) , (1, [3, 2])]),
        ])
def test_reducer_4(reducer_var, expected_redu):
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
    pdb.set_trace()
    assert (sn1.output == expected_output).all()
    assert (sn1.inputs["out"] == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()
    for (i,out) in enumerate(sn1.output_reduced):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()


@pytest.mark.parametrize("reducer_var, expected_redu", [
        ("a", [(3, [1, 3]) , (1, [0, 2])]),
        ("b", [(1, [1, 3]) , (2, [0, 2])]),
        pytest.mark.xfail(("ab", [(3, [1, 3]) , (2, [0, 2])])), #should be implemented??
        ("c", [(1, [1, 0]) , (0, [3, 2])]),
        ("d", [(2, [1, 0]) , (1, [3, 2])]),
        ])
def test_reducer_4a(reducer_var, expected_redu):
    inputs_1 = {"a":[3, 1], "b":[1, 2]}
    inputs_2 = {"c": [1,0], "d": [2,1]}
    sn1 = SNode(function=my_function_dot, mapper='a.b', inputs=inputs_1, outp_name="ab", redu=True)
    sn2 = SNode(function=my_function_4a, mapper='(ab)x(c.d)', inputs=inputs_2, run_node=False, redu=True)
    sn1.__add__(sn2)
    rn = ReduNode(reducer=[reducer_var])
    sn1.__add__(rn)
    sn1.run()
    if reducer_var == "ab": pdb.set_trace()
    expected_output = np.array([[1, 3], [0, 2]])
    expected_inp_ab = np.array([[3, 3], [2, 2]])
    assert (sn1.output == expected_output).all()
    assert (sn1.inputs["ab"] == expected_inp_ab).all()
    for (i,out) in enumerate(sn1.output_reduced):
        assert out[0] == expected_redu[i][0]
        assert (out[1] == expected_redu[i][1]).all()




#pomyslec czy drugo node musi miec redu=true

#zakldamy chyba, ze postac f-cji wychodzacej z f-cji mapper jest taka sama??
# trzeba pamietac zmienne ktore ida do reduce
# skoro i tak trzeba ciagac poczatkowe zmienne, to moze osobne jednak nody dla reduce??


#jesli jest named output, to trzeba sprawdzac, czy z rzeczy mappera nie ma w reduce i ewntualnie tez jakos korelowac (nowy slownik?)
#chwilowo zrobic, ze reduzer tylko na koncu?
