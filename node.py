import re
import numpy as np
import itertools
import pdb


class Node:
    # TODO name should be optional?
    def __init__(self, Interface, name=None, mapper=None, reducer=None, reduce_function=None):
        r = re.compile("^[a-zA-Z0-9.\(\)]*$")
        if not r.match(mapper):
            raise Exception("wrong mapper")

        self.mapper = mapper
        if self.mapper:
            self._mapper2rpn()
        
        self.reducer = reducer
        self.Interface = Interface
        self.name = name
        
    # czyli to nie ma byc w init?? wtedy duzo rzeczy w run
    def _get_inputs(self):
        return self._inputs
    
    # should I remove dictionary??
    def _set_inputs(self, inp_dict):
        #pdb.set_trace()
        self._inputs = {}
        for key, val in inp_dict.items():
            self._inputs[key] = np.array(val)
    
    inputs = property(_get_inputs, _set_inputs)


    def run(self):
        # chyba musze jednak stworzyc nowy zestaw inputu, czy nie?? moze sprobuje bez
        # have to start from broadcasting
        if self.reducer:
            self._setting_redu_mapping()
        self._input_broadcasting()


        # TODO, trzeba pomyslec i IF(arg) i IF(out_nm)
        self.output = self.Interface(**self.inputs)


    def _mapper2rpn(self):
        self._mapper_rpn = []
        signs = []
        i=0
        while i < len(self.mapper):
            l = self.mapper[i]
            inc=1
            if l in ["(", ".", "x"]:
                signs.append(l)
            elif l == ")":
                if signs[-1] == "(": #for (a).(b)                                                   
                    signs.pop()
                else:
                    self._mapper_rpn.append(signs.pop())
                    if signs[-1] == "(":
                        signs.pop()
                    else:
                        raise Exception("WRONG INP: parenthesis")
            elif re.match("[a-vy-zA0-9]+", self.mapper[i:]):
                kk = re.match("[a-vy-zA0-9]+", self.mapper[i:])
                self._mapper_rpn.append([self.mapper[i+kk.start():i+kk.end()]])
                inc = (kk.end() - kk.start())
            else:
                print("WRONG INP")
            i += inc

        if "(" in signs:
            raise Exception("WRONG INP: left parenthesis")
        while signs:
            self._mapper_rpn.append(signs.pop())


    def _input_broadcasting(self):
        #pdb.set_trace()
        inp_arr = []
        for smb in self._mapper_rpn:
            #pdb.set_trace()                                                                        
            if smb in [".", "x"]:
                right = inp_arr.pop()
                left = inp_arr.pop()
                if smb == ".": # TODO ten if polaczyc z wyzszym
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

                        #for reducer, so I know which axis are related to the input var             
                        if self.reducer:
                            self.redu_mapping[inp] = [x+left_ndim for x in self.redu_mapping[inp]]
                            if self.outp_name and (inp in self.var_hist):
                                for ih in self.var_hist[inp]:
                                    self.redu_mapping[ih] = [x+left_ndim for x in self.redu_mapping\
[ih]]

                        self.inputs[inp] = np.broadcast_to(self.inputs[inp], out_shape)

                inp_arr.append(left+right)

            else:
                inp_arr.append(smb)


    def _setting_redu_mapping(self):
        self.redu_mapping = {}
        for key, arr in self.inputs.items():
            if arr.size == 1:
                self.redu_mapping[key] = [] #if array has only one element                      
            else:
                self.redu_mapping[key] = [i for i in range(arr.ndim)]
