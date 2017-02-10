import re
import numpy as np
import itertools
import pdb


class Node:
    # TODO name should be optional?
    def __init__(self, Interface, output_name=["out"], name=None, mapper=None, reducer=None, reduce_function=None): 
        r = re.compile("^[a-zA-Z0-9.\(\)]*$")
        if not r.match(mapper):
            raise Exception("wrong mapper")

        self.mapper = mapper
        if self.mapper:
            self._mapper2rpn()
        
        self.reducer = reducer
        self.Interface = Interface
        self.name = name

        # TODO, not sure what shoul be the way to create output names 
        self.output_name = output_name
        self.output = {}
        for nm in output_name:
            self.output[nm] = None
        
        self._inputs = {}

    # czyli to nie ma byc w init?? wtedy duzo rzeczy w run
    def _get_inputs(self):
        #if "_inputs" in self.__dict__:
        return self._inputs
        
    
    # should I remove dictionary??
    def _set_inputs(self, inp_dict):
        #pdb.set_trace()
        self._inputs = {}
        self._inputs_bcast = {}
        for key, val in inp_dict.items():
            self._inputs[key] = np.array(val)
            self._inputs_bcast[key] = np.array(val)

    inputs = property(_get_inputs, _set_inputs)


    def run(self):
        # have to start from broadcasting
        if self.reducer:
            self._setting_redu_mapping()
        self._input_broadcasting()


        # TODO, trzeba pomyslec i IF(arg) i IF(out_nm)
        #pdb.set_trace()
        fun_output = self.Interface(**self._inputs_bcast)
        if type(fun_output) is not tuple:
            fun_output = tuple([fun_output])

        for (i,nm) in enumerate(self.output_name): 
            self.output[nm] = fun_output[i]


        if self.reducer:
            self._run_reducer()


    def _run_reducer(self):
        axis_all = []
        axis_redu_list = []
        newaxis_redu_list = []
        index_redu_list = []
        inputs_redu_list = []
        i = 0
        for key in self.reducer:
            axis_redu = self.redu_mapping[key]
            if list(set(axis_all) & set(axis_redu)):
                raise Exception("cant reduce anymore, chose the subset of keys")
            else:
                axis_all += axis_redu
                axis_redu_list.append(axis_redu)
                newaxis_redu_list.append(list(range(i, i+ len(axis_redu))))
                inputs_redu_list.append(self._inputs[key])
                index_redu_list.append([x for x in np.ndindex(self._inputs[key].shape)])
                i+=len(axis_redu)

        #changing output
        self.output_reduced = {}   
        for (key, out) in self.output.items():
            output_moveaxis = out.copy() # TODO:it's a copy...
        
            output_moveaxis = np.moveaxis(output_moveaxis,
                                          sum(axis_redu_list, []), sum(newaxis_redu_list, []))

            index_redu_product = list(itertools.product(*index_redu_list))
            self.output_reduced[key] = [([inputs_redu_list[i][x[i]] for i in range(len(inputs_redu_list))],
                                         output_moveaxis[sum(x,())]) for x in index_redu_product]




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
                    if self._inputs_bcast[right[0]].shape == self._inputs_bcast[left[0]].shape:
                        #don't have to do anything, have already the proper shape                   
                        pass
                    elif self._inputs_bcast[right[0]].shape == (1,):
                        for inp in right:
                            self._inputs_bcast[inp] = \
                                np.broadcast_to(self._inputs_bcast[inp], self._inputs_bcast[left[0]].shape)

                    elif self._inputs_bcast[left[0]].shape == (1,):
                        for inp in left:
                            self._inputs_bcast[inp] = \
                                np.broadcast_to(self._inputs_bcast[inp], self._inputs_bcast[right[0]].shape)

                    else:
                        raise Exception("cannot broadcast")


                elif smb == "x":
                    # should I check if shape doesn't contain ones??                                
                    left_ndim = self._inputs_bcast[left[0]].ndim
                    right_ndim = self._inputs_bcast[right[0]].ndim
                    out_shape = self._inputs_bcast[left[0]].shape + self._inputs_bcast[right[0]].shape
                    for inp in left:
                        #pdb.set_trace()                                                            
                        # how to do it without a loop??                                             
                        for d in range(right_ndim):
                            self._inputs_bcast[inp] = self._inputs_bcast[inp][...,np.newaxis]
                        #pdb.set_trace()                                                            
                        self._inputs_bcast[inp] = np.broadcast_to(self._inputs_bcast[inp], out_shape)

                    for inp in right:
                        for d in range(left_ndim):
                            self._inputs_bcast[inp] = self._inputs_bcast[inp][np.newaxis, :]

                        #for reducer, so I know which axis are related to the input var             
                        if self.reducer:
                            self.redu_mapping[inp] = [x+left_ndim for x in self.redu_mapping[inp]]
                            # to chyba mi sie nie przyda ??
                            #if self.outp_name and (inp in self.var_hist):
                            #    for ih in self.var_hist[inp]:
                            #        self.redu_mapping[ih] = [x+left_ndim for x in self.redu_mapping[ih]]

                        self._inputs_bcast[inp] = np.broadcast_to(self._inputs_bcast[inp], out_shape)

                inp_arr.append(left+right)

            else:
                inp_arr.append(smb)


    def _setting_redu_mapping(self):
        self.redu_mapping = {}
        for key, arr in self._inputs.items():
            if arr.size == 1:
                self.redu_mapping[key] = [] #if array has only one element                      
            else:
                self.redu_mapping[key] = [i for i in range(arr.ndim)]
