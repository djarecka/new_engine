import re
import numpy as np
import pdb


class SNode(object):
    def __init__(self, function, mapper, inputs, outp_name=None, run_node=True):
        r = re.compile("^[a-zA-Z.\(\)]*$")
        if r.match(mapper):
            pass
            #self.mapper = mapper
        else: 
            raise Exception("wrong mapper")
        # property? TODO
        self.inputs_usr = inputs
        
        self.outp_name = outp_name
        self.run_node = run_node
        
        self.inputs = None
        if self.run_node:
            #pdb.set_trace()
            self.inputs = {}
            for key in inputs:
                self.inputs[key] = np.array(inputs[key])

            self._mapper_to_inputs(mapper)

        if type(function) is list:
            self.functions = function #TODO: extra checks?
        else:
            self.functions = [(function, self.inputs, mapper, outp_name)]



    def _mapper_to_inputs(self, mapper):
        _mapper_rpn = self._rpn(mapper)
        #pdb.set_trace()
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
                if len(signs) > 1:
                    _mapper_rpn.append(signs.pop())
                if signs[-1] == "(":
                    signs.pop()
                else:
                    raise Exceptionn("WRONG INP: parenthesis")
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
                        self.inputs[inp] = np.broadcast_to(self.inputs[inp], out_shape)

                inp_arr.append(left+right)

            else:
                inp_arr.append(smb)


    def __add__(self, second_node):
        for (key, val) in second_node.inputs_usr.items():
            if key in self.inputs:
                raise Exception("a key from second input already exists in self.inputs") #warnings?
            else:
                self.inputs[key] = np.array(val)
        
        self.functions += second_node.functions


    def run(self):
        if self.run_node:
            for (fun, inp, map, out_nm) in self.functions:
                if not inp:
                    # have to create mapping before running function
                    self._mapper_to_inputs(map)
                
                self.output = fun(**self.inputs)
                #pdb.set_trace()
                if type(out_nm) is list:
                    for i,nm in enumerate(out_nm):
                        self.inputs[nm] = self.output[i]
                elif type(out_nm) is str:
                    self.inputs[out_nm] = self.output
                    
                #pdb.set_trace()
        else:
            # TODO check if the node has all fields and try to run?
            raise Exception("The node is not design to be run")



# sprawdzanie argumentow f-cji i dopasowywanie (na poczatku jako kwrgs)
# tworzenie tablic a/b w zaleznosci od ./x i podawanie tego do f-cji
# zrezygnowac z warunku, ze a i b trza w init podawac?
# nazwy nie moga miec "x", czy to ok?
# napisac jakis dekorator aby do arg f-cji dodawal  **dict (albo tworzyc jakis kolejny sub-slownik) 
