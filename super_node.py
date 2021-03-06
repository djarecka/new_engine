import re
import numpy as np
import itertools
import pdb


class SNode(object):
    def __init__(self, function, mapper, inputs={}, arg_map=None, outp_name=None, 
                 run_node=True, redu=False):
        r = re.compile("^[a-zA-Z0-9.\(\)]*$")
        if not r.match(mapper):
            raise Exception("wrong mapper")

        self.inputs_usr = {}
        for key, val in inputs.items():
            self.inputs_usr[key] = np.array(val)
        
        self.outp_name = outp_name
        self.run_node = run_node
        self.redu = redu
        
        if self.redu: # TODO: this should be true only if run_node is True
            self.redu_mapping = {}
            for key, arr in self.inputs_usr.items():
                if arr.size == 1:
                    self.redu_mapping[key] = [] #if array has only one element
                else:
                    self.redu_mapping[key] = [i for i in range(arr.ndim)]

        if self.outp_name and self.redu:
            self.var_hist = {}
            if type(self.outp_name) is list:
              for var in self.outp_name:  #I'm assuming that all var from inputs is used in mapper TODO
                  self.var_hist[var] = inputs.keys()
        

        self.inputs = None
        if self.run_node:
            self.inputs = {}
            for key in inputs:
                self.inputs[key] = np.array(inputs[key])
            
            self._mapper_to_inputs(mapper)

        if type(function) is list:
            self.functions = function #TODO: extra checks?
        else:
            self.functions = [(function, self.inputs, mapper, outp_name, arg_map)]



    def _mapper_to_inputs(self, mapper):
        _mapper_rpn = self._rpn(mapper)
        if len(_mapper_rpn) > 1:
            self._input_broadcasting(_mapper_rpn)
            

    def _rpn(self, mapper):
        _mapper_rpn = []
        signs = []
        i=0
        while i < len(mapper):    
            l = mapper[i]
            inc=1
            if l in ["(", ".", "x"]:
                signs.append(l)
            elif l == ")":
                if signs[-1] == "(": #for (a).(b)
                    signs.pop()
                else:
                    _mapper_rpn.append(signs.pop())
                    if signs[-1] == "(":
                        signs.pop()
                    else:
                        raise Exception("WRONG INP: parenthesis")
            elif re.match("[a-vy-zA0-9]+", mapper[i:]):
                kk = re.match("[a-vy-zA0-9]+", mapper[i:])
                _mapper_rpn.append([mapper[i+kk.start():i+kk.end()]])
                inc = (kk.end() - kk.start()) 
            else:
                print "WRONG INP"
            i += inc

        if "(" in signs:
            raise Exception("WRONG INP: left parenthesis")
        while signs:
            _mapper_rpn.append(signs.pop())
        
        return _mapper_rpn


    def _input_broadcasting(self, _mapper_rpn):
        inp_arr = []
        for smb in _mapper_rpn:
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
                            
                        #for reducer, so I know which axis are related to the input var
                        if self.redu:
                            self.redu_mapping[inp] = [x+left_ndim for x in self.redu_mapping[inp]]
                            if self.outp_name and (inp in self.var_hist):
                                for ih in self.var_hist[inp]:
                                    self.redu_mapping[ih] = [x+left_ndim for x in self.redu_mapping[ih]]

                        self.inputs[inp] = np.broadcast_to(self.inputs[inp], out_shape)

                inp_arr.append(left+right)

            else:
                inp_arr.append(smb)


    def __add__(self, second_node):
        if isinstance(second_node, SNode):
            for (key, val) in second_node.inputs_usr.items():
                if key in self.inputs:
                    raise Exception("a key from second input already exists in self.inputs") #warnings?
                else:
                    self.inputs[key] = val
                    self.inputs_usr[key] = val
                    if second_node.redu:
                        self.redu_mapping[key] = second_node.redu_mapping[key]
                    
            if second_node.redu and second_node.outp_name:
                for (key, val) in second_node.var_hist.items():
                    if key in self.var_hist:
                        raise Exception("a key from second redu_mapper already exists in self.inputs") #warnings?
                    else:
                        self.var_hist[key] = val
       
            self.functions += second_node.functions
            
        elif isinstance(second_node, ReduNode): # checking self.redu ?? TODO
            # TODO we should probably allow for multiple reducers
            self.reducer_and_fun = (second_node.reducer, second_node.reducer_function) 

    def run(self):
        if self.run_node:
            for (fun, inp, map, out_nm, arg) in self.functions:
                if not inp:
                    # have to create mapping before running function
                    self._mapper_to_inputs(map)
                
                if arg: #TODO better
                    fun_inputs = self.inputs.copy()
                    for (key, arg_nm) in arg.items():
                        fun_inputs[arg_nm] = fun_inputs.pop(key)
                    self.output = fun(**fun_inputs)
                else:
                    self.output = fun(**self.inputs)
               
                if type(out_nm) is list:
                    for i,nm in enumerate(out_nm):
                        self.inputs[nm] = self.output[i]
                elif type(out_nm) is str:
                    self.inputs[out_nm] = self.output
                    
                #pdb.set_trace()
        else:
            # TODO check if the node has all fields and try to run?
            raise Exception("The node is not design to be run")

        # for now it works only at the end, so no self.function needed, but TODO 
        if self.redu and self.reducer_and_fun:
            self.run_reducer()


    def run_reducer(self):
        # assuming that we reduce self.output, i.e. the result of the last function
        # assuming that there is one reducer node TODO
        reducer_key_list = self.reducer_and_fun[0]
        reducer_fun = self.reducer_and_fun[1]

        axis_all = []
        axis_redu_list = []
        newaxis_redu_list = []
        index_redu_list = []
        inputs_redu_list = []
        i = 0
        for key in reducer_key_list:
            axis_redu = self.redu_mapping[key]
            if list(set(axis_all) & set(axis_redu)):
                raise Exception("cant reduce anymore, chose the subset of keys")
            else:
                axis_all += axis_redu
                axis_redu_list.append(axis_redu)
                newaxis_redu_list.append(range(i, i+ len(axis_redu)))
                inputs_redu_list.append(self.inputs_usr[key])
                index_redu_list.append([x for x in np.ndindex(self.inputs_usr[key].shape)])
                i+=len(axis_redu)

        #changing output               
        self._output_moveaxis = self.output.copy() #it's a copy...   
        self._output_moveaxis = np.moveaxis(self._output_moveaxis,
                                           sum(axis_redu_list, []), sum(newaxis_redu_list, []))

        self._index_redu_product = list(itertools.product(*index_redu_list))

        if reducer_fun:
            # should I really use list
            self.output_reduced = [([inputs_redu_list[i][x[i]] for i in range(len(inputs_redu_list))],
                                    getattr(self._output_moveaxis[sum(x,())],reducer_fun)()) for x in self._index_redu_product]
        else:
            self.output_reduced = [([inputs_redu_list[i][x[i]] for i in range(len(inputs_redu_list))], 
                                    self._output_moveaxis[sum(x,())]) for x in self._index_redu_product]
        

# TODO: now the code doesn't work for var that are just a number


class ReduNode(object):
    #TODO should inherit from SNode??
    def __init__(self, reducer, reducer_function=None):
        self.reducer = reducer
        self.reducer_function = reducer_function 


# zrezygnowac z warunku, ze a i b trza w init podawac?
# nazwy nie moga miec "x", czy to ok?
# napisac jakis dekorator aby do arg f-cji dodawal  **dict (albo tworzyc jakis kolejny sub-slownik) 
