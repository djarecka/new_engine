import re
import numpy as np
import pdb


class SNode(object):
    def __init__(self, function, mapper, inputs):
        self.function = function
        r = re.compile("^[a-zA-Z.\(\)]*$")
        if r.match(mapper):
            self.mapper = mapper
        else: 
            raise Exception("wrong mapper")
        self.inputs_usr = inputs
        self.inputs = {}
        #pdb.set_trace()
        self._mapper_to_inputs(inputs, mapper)


    def _mapper_to_inputs(self, inputs_dic, mapper):
        inner_brackets = True
        while inner_brackets:
            bracket_search = re.search('\([^\(\)]+\)', mapper)
            if bracket_search:
                expr_bracket = mapper[bracket_search.start() : bracket_search.end()]
                broadcasted_list = self._broadcasting_input(expr_bracket[1:-1])
                mapper = mapper.replace(expr_bracket, str(broadcasted_list))
            else:
                inner_brackets = False
                broadcasted_list = self._broadcasting_input(mapper)
        #pdb.set_trace()
        if not all(key in self.inputs for key in broadcasted_list):
            raise Exception("incomplite input")

    def _broadcasting_input(self, expr):
        if "." in expr:
            input_list = expr.split(".")
            # checking if list has exactly 2 elements and no special signs
            if len(input_list) != 2 or "x" in input_list:
                raise Exception("wrong mapper, too many .x")
            else:
                #pdb.set_trace()
                if input_list[0][0] == "[" and type(eval(input_list[0])) is list: # the first broadcasting was already done
                    input_list =  self._broadcasting_list_of_input_dot(input_list, 0)

                elif input_list[1][0] == "[" and type(eval(input_list[1])) is list:
                    input_list =  self._broadcasting_list_of_input_dot(input_list, 1)

                else:
                    self.inputs[input_list[0]], self.inputs[input_list[1]] = \
                        np.broadcast_arrays(self.inputs_usr[input_list[0]], 
                                            self.inputs_usr[input_list[1]])
                #pdb.set_trace()
                return input_list  # pomyslec czy potrzebne

        elif "x" in expr:
            input_list = expr.split("x")
            # checking if list has exactly 2 elements and no special signs  
            if len(input_list) != 2 or "." in input_list:
                raise Exception("wrong mapper, too many .x")
            else:
                if input_list[0][0] == "[" and type(eval(input_list[0])) is list:
                    input_list = self._broadcasting_list_of_input_cross(input_list, 0)
                elif input_list[1][0] == "[" and type(eval(input_list[1])) is list:
                    input_list = self._broadcasting_list_of_input_cross(input_list, 1)
                else: #dac spr czy 1d
                    self.inputs[input_list[0]], self.inputs[input_list[1]] = \
                        np.broadcast_arrays(self.inputs_usr[input_list[0]], \
                        np.array(self.inputs_usr[input_list[1]])[np.newaxis].transpose())
                return input_list  # pomyslec czy potrzebne 
        else:
            self.inputs[expr] = np.array(self.inputs_usr[expr])
            return [expr]  # pomyslec czy potrzebne 


    def _broadcasting_list_of_input_dot(self, input_list, ind_list):
        ind_no_list = [i for i in [0,1] if i != ind_list][0]
        broadcasted_array = self.inputs[eval(input_list[ind_list])[0]]
        new_array = np.array(self.inputs_usr[input_list[ind_no_list]])
        if broadcasted_array.shape == new_array.shape:
            self.inputs[input_list[ind_no_list]] = new_array
        elif new_array.shape == (1,):
            self.inputs[input_list[ind_no_list]] = np.brodcast_to(new_array, broadcasted_array.shape)
        elif broadcasted_array.shape == (1,):
            self.inputs[input_list[ind_no_list]] = new_array
            for key in eval(input_list[ind_list]):
                self.inputs[key] = np.brodcast_to(self.inputs[key], new_array.shape)
        else:
            raise Exception("wrong mapper: can't broadcast")

        return [inp for inp in eval(input_list[ind_list])] + [input_list[ind_no_list]]


    def _broadcasting_list_of_input_cross(self, input_list, ind_list):
        ind_no_list = [i for i in [0,1] if i != ind_list][0]

        broadcasted_array = self.inputs[eval(input_list[ind_list])[0]]
        new_array = np.array(self.inputs_usr[input_list[ind_no_list]])
        if broadcasted_array.ndim > 1 or new_array.ndim > 1:
            raise Exception("cross product requires ndim=1")
        
        if ind_list == 0:
            for key in eval(input_list[ind_list]):
                self.inputs[key], self.inputs[input_list[ind_no_list]] = \
                    np.broadcast_arrays(self.inputs[key], \
                                            new_array[np.newaxis].transpose())
        elif ind_list == 1:
            for key in eval(input_list[ind_list]):
                self.inputs[input_list[ind_no_list]], self.inputs[key] = \
                    np.broadcast_arrays(new_array, \
                                            self.inputs[key][np.newaxis].transpose())

        #pdb.set_trace()
        return [inp for inp in eval(input_list[ind_list])] + [input_list[ind_no_list]]




    def run(self):
        self.output = self.function(**self.inputs)


    


# nie dziala z dwoma nawiasami po lewej i prawej
# czy outer produck tylko dla 1d?? tak zakladam
# sprawdzanie argumentow f-cji i dopasowywanie (na poczatku jako kwrgs)
# tworzenie tablic a/b w zaleznosci od ./x i podawanie tego do f-cji
# zrezygnowac z warunku, ze a i b trza w init podawac?
# czytanie jak w kalkulatrorze, najpierw nawiasy
