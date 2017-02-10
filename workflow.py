import re
import numpy as np
import itertools
import pdb

from node import Node

# TODO: Node should be used?
class Workflow():
    # TODO: inputs should be in the init?
    def __init__(self, nodes_list=None, inputs_map={}, output_map={}, name=None):
        if nodes_list:
            self.nodes_list = nodes_list
        else:
            self.nodes_list = []
        # TODO when nodes_list is not none
        self.nodes_dict = {}
        self.name = name
        self.inputs_map = inputs_map
        self.output_map = output_map
        self.output_map_reduced = {} 
        self.connect_inp = {}
        self.connect_inp_redu = {}

    def add_node(self, new_node):
        self.nodes_list.append(new_node)
        if new_node.inputs:
            self.inputs_map.update(new_node.inputs)
        if not new_node.name:
            new_node.name = "node"+str(len(self.nodes_list))
        self.nodes_dict[new_node.name] = new_node


    def connect(self, from_node, from_socket, to_node, to_socket):
        # TODO spr order in the list?
       if from_node not in self.nodes_list:
            self.add_node(from_node)
       if to_node not in self.nodes_list:
            self.add_node(to_node)

       # TODO should think how to do multiple connection (can have the same input in mapper?)
       if not to_node.name in self.connect_inp.keys():
           self.connect_inp[to_node.name] = (from_node, from_socket, to_socket)
       #    self.connect_inp[to_node.name] = []
       ##inp = View(from_node.output)
       #inp.rename(from_socket,to_socket)
       #self.connect_inp[to_node.name].append(inp)

       #if to_node.reducer:
       #    if not to_node.name in self.connect_inp_redu.keys():
       #        self.connect_inp_redu[to_node.name] = []
       #    self.connect_inp_redu[to_node.name].append(from_node._inputs)


    # TODO think about order/graph
    def run(self):
        for nn in self.nodes_list:
            if nn.name in self.connect_inp.keys():
                self._update_connection(nn)
            #pdb.set_trace()
            nn.run()
            #pdb.set_trace()
            self.output_map[nn.name] = nn.output
            
            if nn.reducer:
                self.output_map_reduced[nn.name] = nn.output_reduced
        # TODO  output be already reduced?


    def _update_connection(self, node):
        (from_node, from_socket, to_socket) = self.connect_inp[node.name]
        inp = node.inputs # TODO how to update node.iputs?
        if type(to_socket) is list:
            for (i,sc) in enumerate(to_socket):
                inp[sc] = from_node.output[from_socket[i]]
                node.var_hist[sc] = []
        else:
            inp[to_socket] = from_node.output[from_socket]
            node.var_hist[to_socket] = []

#        if node.reducer:
        for (key, val) in from_node.inputs.items():
            if key in self.inputs_map.keys():
                inp[key] = val
                node.redu_mapping[key] = from_node.redu_mapping[key]
                if type(to_socket) is list:
                    for sc in to_socket:
                        node.var_hist[sc].append(key)
                else:
                    node.var_hist[to_socket].append(key)
        node.inputs = inp

            

    def _update_inputs(self, node):
        inp = node.inputs
        for dict in self.connect_inp[node.name]:
            for (key, val) in dict.items():
                inp[key] = val
        node.inputs = inp


# TODO test it
class View(object):
    def __init__(self, d):
        self._d = d
        self._renaming = {}

    def rename(self, a, b):
        self._renaming[b] = a

    def __getitem__(self, key):
        return self._d[self._renaming[key]]

    def items(self):
        for (key, it) in self._renaming.items():
            yield (key,self._d[self._renaming[key]])



# przy connect tworzyc sn1.output["a"] = none
# i sn2.input["aa"] = sn1.output["a"]
