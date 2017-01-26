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
        # property? TODO
        self.inputs_usr = inputs
        self.inputs = {}
        for key in inputs:
            self.inputs[key] = np.array(inputs[key])
        
        #pdb.set_trace()
        self._mapper_to_inputs()


    def _mapper_to_inputs(self):
        self._rpn()
        if len(self._mapper_rpn) > 1:
            self._input_broadcasting()


    def _rpn(self):
        self._mapper_rpn = []
        signs = []
        i=0
        while i < len(self.mapper):    
            l = self.mapper[i]
            inc=1
            if l in ["(", ".", "x"]:
                signs.append(l)
            elif l == ")":
                self._mapper_rpn.append(signs.pop())
                if signs[-1] == "(":
                    signs.pop()
                else:
                    raise Exceptionn("WRONG INP: parenthesis")
            elif re.match("[a-vy-zA0-9]+", self.mapper[i:]):
                kk = re.match("[a-vy-zA0-9]+", self.mapper[i:])
                self._mapper_rpn.append([self.mapper[i+kk.start():i+kk.end()]])
                inc = (kk.end() - kk.start()) 
            else:
                print "WRONG INP"
            i += inc

        if "(" in signs:
            raise Exception("WRONG INP: left parenthesis")
        while signs:
            self._mapper_rpn.append(signs.pop())


    def _input_broadcasting(self):
        inp_arr = []
        for smb in self._mapper_rpn:
            #pdb.set_trace()
            if smb in [".", "x"]:
                right = inp_arr.pop()
                left = inp_arr.pop()
                if smb == ".":
                    #pdb.set_trace()
                    # for now I'm assuming that either they have the same shape or shape=(1,)
                    if self.inputs[right[0]].shape == self.inputs[left[0]].shape:
                        #don't have to do anything, have already the proper shape
                        pass
                    elif self.inputs[right[0]].shape == (1,):
                        for inp in right:
                            self.inputs[inp] = \
                                np.broadcast_to(self.inputs[inp], self.inputs[left[0]].shape)

                    elif self.inputs[left[0]].shape == (1,):
                        for inp in left:
                            self.inputs[inp] = \
                                np.broadcast_to(self.inputs[inp], self.inputs[right[0]].shape)

                    else:
                        raise Exception("cannot broadcast")
        

                elif smb == "x":
                    # should I check if shape doesn't contain ones??
                    left_ndim = self.inputs[left[0]].ndim
                    right_ndim = self.inputs[right[0]].ndim
                    out_shape = self.inputs[left[0]].shape + self.inputs[right[0]].shape
                    for inp in left:
                        #pdb.set_trace()
                        # how to do it without a loop??
                        for d in range(right_ndim):
                            self.inputs[inp] = self.inputs[inp][...,np.newaxis]
                        #pdb.set_trace()
                        self.inputs[inp] = np.broadcast_to(self.inputs[inp], out_shape)

                    for inp in right:
                        for d in range(left_ndim):
                            self.inputs[inp] = self.inputs[inp][np.newaxis, :]
                        self.inputs[inp] = np.broadcast_to(self.inputs[inp], out_shape)

                inp_arr.append(left+right)

            else:
                inp_arr.append(smb)




    def run(self):
        #pdb.set_trace()
        self.output = self.function(**self.inputs)


    


# nie dziala z dwoma nawiasami po lewej i prawej
# czy outer produck tylko dla 1d?? tak zakladam
# sprawdzanie argumentow f-cji i dopasowywanie (na poczatku jako kwrgs)
# tworzenie tablic a/b w zaleznosci od ./x i podawanie tego do f-cji
# zrezygnowac z warunku, ze a i b trza w init podawac?
# czytanie jak w kalkulatrorze, najpierw nawiasy
