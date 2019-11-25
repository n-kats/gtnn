"""
A hierarchical module graph is composed by followings.
* a collection of submodules
* a collection of inputs
* a collection of outputs
* a collection of bindings of intput and output
"""

from typing import List, Tuple, Optional, Dict, Callable, Any
from collections import defaultdict, OrderedDict


class HierarchicalGraph:
    """
    graph with hierarchical structure
    """
    def __init__(self):
        self.__n_nodes: int = 0
        self.__edges: List[Tuple[int, int]] = []
        self.__inclusions: List[Tuple[int, int]] = []  # [(node, parent), ...]

    def add_node(self, parent: Optional[int] = None):
        """
        Args:
            parent(Optional[int]): If None, add a top node. Otherwise, index of parent.
        """
        new_node = self.__n_nodes
        self.__n_nodes += 1
        if parent is not None:
            self.__inclusions.append((new_node, parent))

        return new_node

    def add_edge(self, node_from: int, node_to: int):
        """
        Args:
            node_from: source of the edge.
            node_to: target of the edge.
        """
        self.__edges.append((node_from, node_to))

    def add_inclusion(self, child: int, parent: int):
        """
        Args:
            child: included node
            parent: including node
        """
        self.__inclusions.append((child, parent))

    @property
    def n_nodes(self):
        return self.__n_nodes

    @property
    def edges(self):
        return self.__edges

    @property
    def inclusions(self):
        return self.__inclusions


class HierarchicalModuleGraph:
    def __init__(self, modules, inputs, outputs, bindings, name: str):
        self.__name = name
        self.__modules = modules
        self.__inputs = inputs  # [(key, (i_in, key_in)), ...]
        self.__outputs = outputs  # [((i_out, key_out), key), ...]

        # bind output to input
        self.__bindings = bindings  # [((i_out, key_out), (i_in, key_in)), ...]

        # build
        self.__modules_sorted, self.__bindings_lists, self.__output_lists = self.__build()
        (
            self.__hierarchical_graph,
            self.__node_names,
            self.__input_name_to_id,
            self.__output_name_to_id,
        ) = self.__build_hierarchical_graph()

    @property
    def name(self):
        return self.__name

    def __build_hierarchical_graph(self) -> Tuple[HierarchicalGraph, List[str], Dict[str, int], Dict[str, int]]:
        h_graph = HierarchicalGraph()
        root = h_graph.add_node()
        node_names = [self.__name]
        inputs_dict = OrderedDict()
        for key, (i_in, key_in) in self.__inputs:
            if key not in inputs_dict:
                inputs_dict[key] = []
                node_names.append(f"{self.__name}/input:{key}")
            inputs_dict[key].append((i_in, key_in))
        input_name_to_node_id = {}
        for key in inputs_dict:
            input_name_to_node_id[key] = h_graph.add_node(parent=root)

        outputs_dict = OrderedDict()
        for (i_out, key_out), key in self.__outputs:
            if key not in outputs_dict:
                outputs_dict[key] = []
                node_names.append(f"{self.__name}/output:{key}")
            outputs_dict[key].append((i_out, key_out))

        output_name_to_node_id = {}
        for key in outputs_dict:
            output_name_to_node_id[key] = h_graph.add_node(parent=root)

        input_lists: List[Dict[str, List[int]]] = [defaultdict(list) for _ in self.__modules]
        for key, (i_in, key_in) in self.__inputs:
            input_lists[i_in][key_in].append(input_name_to_node_id[key])

        output_lists: List[Dict[str, List[int]]] = [defaultdict(list) for _ in self.__modules]
        for (i_out, key_out), key in self.__outputs:
            output_lists[i_out][key_out].append(output_name_to_node_id[key])

        for i_mod, module in enumerate(self.__modules):
            sub_graph: HierarchicalGraph = module.hierarchical_graph
            start = h_graph.n_nodes

            # node in submodule
            for sub_name in module.node_names:
                h_graph.add_node()
                node_names.append(f"{self.__name}/module:{sub_name}")

            # edge in submodule
            for source, target in sub_graph.edges:
                h_graph.add_edge(source + start, target + start)

            # root in submodule -> root
            is_top_node = [True for i in range(sub_graph.n_nodes)]
            for child, parent in sub_graph.inclusions:
                is_top_node[child] = False
                h_graph.add_inclusion(child + start, parent + start)

            for node, is_top in enumerate(is_top_node):
                if is_top:
                    h_graph.add_inclusion(node + start, root)

            # input -> input in submodule
            for key_in, id_sub_in in module.input_name_to_id.items():
                for id_in in input_lists[i_mod][key_in]:
                    h_graph.add_edge(id_in, id_sub_in + start)

            # output in submodule -> output
            for key_out, id_sub_out in module.output_name_to_id.items():
                for id_out in output_lists[i_mod][key_out]:
                    h_graph.add_edge(id_sub_out + start, id_out)

        return h_graph, node_names, input_name_to_node_id, output_name_to_node_id

    @property
    def hierarchical_graph(self):
        return self.__hierarchical_graph

    @property
    def node_names(self):
        return self.__node_names

    @property
    def input_name_to_node_id(self):
        return self.__input_name_to_id

    @property
    def output_name_to_node_id(self):
        return self.__output_name_to_id

    def __call__(self, **kwargs):
        outputs: Dict[str, Any] = {}
        inputs_dicts: List[Dict[str, Callable]] = [{} for _ in self.__modules]
        for key, (i_in, key_in) in self.__inputs:
            inputs_dicts[i_in][key_in] = kwargs[key]

        for i_mod in self.__modules_sorted:
            out = self.__modules[i_mod](**inputs_dicts[i_mod])
            for key_out, i_in, key_in in self.__bindings_lists[i_mod]:
                inputs_dicts[i_in][key_in] = out[key_out]
            for key_out, key in self.__output_lists[i_mod]:
                outputs[key] = out[key_out]

        return outputs

    def __build(self):
        edges = {(i_source, i_target) for (i_source, _), (i_target, _) in self.__bindings}
        modules_sorted = []
        target_to_sources = {i: set() for i in range(len(self.__modules))}
        for i_source, i_target in edges:
            target_to_sources[i_target].add(i_source)

        # topological sort
        while True:
            to_add = [i for i, srcs in target_to_sources.items() if not srcs]
            if not to_add:
                break
            for i in to_add:
                target_to_sources.pop(i)
                modules_sorted.append(i)

            for srcs in target_to_sources.values():
                for i in to_add:
                    if i in srcs:
                        srcs.remove(i)
        if target_to_sources:
            raise Exception("There are cyclic dependencies.")

        bindings_lists: List[Tuple[str, int, str]] = [[] for _ in self.__modules]
        for (i_out, key_out), (i_in, key_in) in self.__bindings:
            bindings_lists[i_out].append((key_out, i_in, key_in))

        output_lists: List[Tuple[str, str]] = [[] for _ in self.__modules]
        for (i_out, key_out), key in self.__outputs:
            output_lists[i_out].append((key_out, key))

        return modules_sorted, bindings_lists, output_lists
