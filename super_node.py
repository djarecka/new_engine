import re
import numpy as np


class SNode(object):
    def __init__(self, function, mapper, inputs):
        self.function = function
        r = re.compile("^[a-zA-Z.]*$")
        if r.match(mapper):
            self.mapper = mapper
        else: 
            raise Exception("wrong mapper")
        self.set_inputs(inputs)
        


    def set_inputs(self, inputs_dic):
        self._inputs_list = self.mapper.split(".")
        if all(key in inputs_dic for key in self._inputs_list):
            self.inputs = {}
            for ii in self._inputs_list:
                
                self.inputs[ii] = np.array(inputs_dic[ii])
        else:
            raise Exception("incomplite input")


#    def _get_inputs(self):
#        return self.inputs

#    def _set_inputs(self, value_dic):
        



    def run(self):
        self.output = self.function(**self.inputs)




# sprawdzanie argumentow f-cji i dopasowywanie (na poczatku jako kwrgs)
# tworzenie tablic a/b w zaleznosci od ./x i podawanie tego do f-cji
# zrezygnowac z warunku, ze a i b trza w init podawac?
# czytanie jak w kalkulatrorze, najpierw nawiasy
