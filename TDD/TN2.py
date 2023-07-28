from TDD.TDD import cont, get_identity_tdd,Index
import time
import cotengra as ctg

common_tensor_table = dict()


class Tensor:
    def __init__(self, data=[], index=[], name=None, qubits=None):
        self.data = data
        self.index_set = index
        self.name = name
        self.qubits = qubits  # This is used only when it represent a quantum gate

    def tdd(self):
        from TDD.TDD import get_tdd

        return get_tdd(self.data, self.index_set)


class TensorNetwork:
    def __init__(self, tensors=dict(), tn_type="tn", qubits_num=0):
        self.tensors = tensors
        self.tn_type = tn_type
        self.index_set = set()
        self.index_2_tensor = dict()
        self.qubits_num = (
            qubits_num  # This is used only when it represent a quantum circuit
        )

    def cont(self, optimizer=None, max_node=False):
        tdd = get_identity_tdd()
        max_node_num = 0
        if optimizer == "tree_decomposition":
            decom_tree, tree_width = get_tree_decomposition(self)
            cont_index = find_contraction_index(decom_tree)
            computed_tdd_list = []
            while cont_index:
                computed_tdd_list, node_num = contract_an_index(
                    self, cont_index, computed_tdd_list, max_node
                )
                cont_index = find_contraction_index(decom_tree)
                if max_node:
                    max_node_num = max(max_node_num, node_num)
            for temp_tdd in computed_tdd_list:
                tdd = cont(tdd, temp_tdd)
            if max_node:
                max_node_num = max(max_node_num, tdd.node_number())

            return tdd, max_node_num
        if optimizer == "cir_partition1":
            if not self.tn_type == "cir":
                print("This optimizer is only used for quantum circuits!")
                return tdd
            partion_cir = circuit_partion1(self)
            for level in range(len(partion_cir)):
                temp_tn = TensorNetwork(partion_cir[level][0])
                tdd1, max_node_num = temp_tn.cont()
                if max_node:
                    max_node_num = max(max_node_num, tdd1.node_number())
                temp_tn = TensorNetwork(partion_cir[level][1])
                tdd2, max_node_num = temp_tn.cont()
                if max_node:
                    max_node_num = max(max_node_num, tdd2.node_number())
                temp_tdd = cont(tdd1, tdd2)
                tdd = cont(tdd, temp_tdd)
                if max_node:
                    max_node_num = max(max_node_num, tdd.node_number())

            return tdd, max_node_num

        if optimizer == "cir_partition2":
            if not self.tn_type == "cir":
                print("This optimizer is only used for quantum circuits!")
                return tdd
            partion_cir = circuit_partion2(self)

            for level in range(len(partion_cir)):
                temp_tn = TensorNetwork(partion_cir[level][0])
                tdd1, max_node_num = temp_tn.cont()
                if max_node:
                    max_node_num = max(max_node_num, tdd1.node_number())
                temp_tn = TensorNetwork(partion_cir[level][1])
                tdd2, max_node_num = temp_tn.cont()
                if max_node:
                    max_node_num = max(max_node_num, tdd2.node_number())
                temp_tdd = cont(tdd1, tdd2)
                if max_node:
                    max_node_num = max(max_node_num, temp_tdd.node_number())
                temp_tn = TensorNetwork(partion_cir[level][2])
                tdd3, max_node_num = temp_tn.cont()
                if max_node:
                    max_node_num = max(max_node_num, tdd3.node_number())
                temp_tdd = cont(tdd3, temp_tdd)
                if max_node:
                    max_node_num = max(max_node_num, temp_tdd.node_number())
                tdd = cont(tdd, temp_tdd)
                if max_node:
                    max_node_num = max(max_node_num, tdd.node_number())

            return tdd, max_node_num

        def index_2_str(index):
            return (
                index.key
            )  # + '_' + str(index.idx) if index.key[0] == 'x' else index.key

        if optimizer == "opt_einsum":
            import opt_einsum as oe

            indices = {
                index_2_str(index)
                for tensor in self.tensors
                for index in tensor.index_set
            }

            index_id_dict = dict(zip(indices, range(len(indices))))

            # print("index_id_dict:", index_id_dict)

            ts_index_seq = [
                (
                    tensor.data,
                    [index_id_dict[index_2_str(index)] for index in tensor.index_set],
                )
                for tensor in self.tensors
            ]
            ts_index_flat_seq = sum(ts_index_seq, ())

            output_index_ids = [
                index_id_dict[index] for index in indices if index[0] == "y"
            ]

            # print("ts index:", dict(enumerate(ts_index_flat_seq[1::2])))
            # print("output:", output_index_ids)

            path, path_info = oe.contract_path(*ts_index_flat_seq, output_index_ids)

            # print(path, path_info)

            return self.tdds_contract_by_path(path, max_node, max_node_num)

        if optimizer == "cotengra":
            # TODO: we can further switch to cotengra by given `inputs, output, size_dict`
            

            opt = ctg.HyperOptimizer()

            indices = {
                index_2_str(index)
                for tensor in self.tensors
                for index in tensor.index_set
            }

            index_id_dict = dict(zip(indices, range(len(indices))))

            inputs = [
                tuple(index_id_dict[index_2_str(index)] for index in tensor.index_set)
                for tensor in self.tensors
            ]

            output = [index_id_dict[index] for index in indices if index[0] == "y"]

            size_dict = {
                index_id_dict[index_2_str(index)]: size
                for tensor in self.tensors
                for index, size in zip(tensor.index_set, tensor.data.shape)
            }

            tree = opt.search(inputs, output, size_dict)
            path = tree.get_path()

            return self.tdds_contract_by_path(path, max_node, max_node_num)

        for ts in self.tensors:
            temp_tdd = ts.tdd()
            tdd = cont(tdd, temp_tdd)

            if max_node:
                max_node_num = max(max_node_num, tdd.node_number())

        return tdd, max_node_num

    def get_index_set(self):
        for ts in self.tensors:
            temp_index = [idx.key for idx in ts.index_set]
            for idx in temp_index:
                self.index_set.add(idx)
                if not idx in self.index_2_tensor:
                    self.index_2_tensor[idx] = set()
                self.index_2_tensor[idx].add(ts)

    def tdds_contract_by_path(self, path, max_node, max_node_num):
        t=time.time()
        _tdds = [ts.tdd() for ts in self.tensors]
#         print(path)
        for ts1, ts2 in path:
            # print('contract:', ts1, ts2)
            tmp_tdd = cont(_tdds[ts1], _tdds[ts2])
            
            if max_node:
                max_node_num = max(max_node_num, tmp_tdd.node_number())

            # TODO: use heapq to do in O(logn)?
            # https://stackoverflow.com/a/10163422
            _tdds = [_tdd for i, _tdd in enumerate(_tdds) if i not in [ts1, ts2]]

            # simple remove?
            # bug: __eq__ of tdd does not unique?
            # del_vals = [_tdds[ts1], _tdds[ts2]]
            # [_tdds.remove(element) for element in del_vals]
            _tdds.append(tmp_tdd)

            # print("# of remain ts:", len(_tdds))
            # print("remain indices:", [[index_2_str(index) for index in _tdd.index_set] for _tdd in _tdds ])

        assert len(_tdds) == 1
        print('tt',time.time()-t)
        return _tdds[0], max_node_num


#     def get_index_2_node(self):
#         index_2_node=dict()
#         for k in range(len(data)):
#             temp_index=[idx.key for idx in self.data[k].index]
#             for idx in temp_index:
#                 if not idx in index_2_node:
#                     index_2_node[idx]=set()
#                 index_2_node[idx].add(k)
#         return index_2_node


def get_tree_decomposition(tn):
    import networkx as nx
    from networkx.algorithms.approximation.treewidth import treewidth_min_fill_in    
    lin_graph = nx.Graph()
    if not tn.index_set:
        tn.get_index_set()

    lin_graph.add_nodes_from(tn.index_set)

    for ts in tn.tensors:
        for k1 in range(len(ts.index_set)):
            for k2 in range(k1 + 1, len(ts.index_set)):
                if ts.index_set[k1].key != ts.index_set[k2].key:
                    lin_graph.add_edge(ts.index_set[k1].key, ts.index_set[k2].key)

    tree_width, de_graph = treewidth_min_fill_in(lin_graph)
    #     print('The treewidth is',tree_width)
    return de_graph, tree_width


def find_contraction_index(tree_decomposition):
    import networkx as nx
    idx = None
    if len(tree_decomposition.nodes) == 1:
        nod = [k for k in tree_decomposition.nodes][0]
        if len(nod) != 0:
            idx = [idx for idx in nod][0]
            nod_temp = set(nod)
            nod_temp.remove(idx)
            tree_decomposition.add_node(frozenset(nod_temp))
            tree_decomposition.remove_node(nod)
        return idx
    nod = 0
    for k in tree_decomposition.nodes:
        if nx.degree(tree_decomposition)[k] == 1:
            nod = k
            break

    neib = [k for k in tree_decomposition.neighbors(nod)][0]
    for k in nod:
        if not k in neib:
            idx = k
            break
    if idx:
        nod_temp = set(nod)
        nod_temp.remove(idx)
        tree_decomposition.remove_node(nod)
        if frozenset(nod_temp) != neib:
            tree_decomposition.add_node(frozenset(nod_temp))
            tree_decomposition.add_edge(frozenset(nod_temp), neib)
        return idx
    else:
        tree_decomposition.remove_node(nod)
        return find_contraction_index(tree_decomposition)


def contract_an_index(tn, cont_index, computed_tdd_list, max_node=False):
    temp_tn = TensorNetwork(tn.index_2_tensor[cont_index])
    temp_tdd = temp_tn.cont()[0]
    max_node_num = 0
    if max_node:
        max_node_num = max(max_node_num, temp_tdd.node_number())
    for ts in tn.index_2_tensor[cont_index]:
        for idx in ts.index_set:
            if idx.key != cont_index:
                if ts in tn.index_2_tensor[idx.key]:
                    tn.index_2_tensor[idx.key].remove(ts)
    temp_computed_tdd_list = []
    for tdd in computed_tdd_list:
        tdd_idx_out = [k.key for k in tdd.index_set]

        if cont_index in tdd_idx_out:
            temp_tdd = cont(tdd, temp_tdd)
            if max_node:
                max_node_num = max(max_node_num, temp_tdd.node_number())
        else:
            temp_computed_tdd_list.append(tdd)
    temp_computed_tdd_list.append(temp_tdd)
    computed_tdd_list = temp_computed_tdd_list
    return computed_tdd_list, max_node_num


def circuit_partion1(tn):
    """The first partition scheme;
    cx_max is the number of CNOTs allowed to be cut
    """
    res = [[[], []]]

    num_qubit = tn.qubits_num

    cx_max = num_qubit // 2
    cx_num = 0
    level = 0

    qubits = []
    qubits.append([k for k in range(num_qubit // 2)])
    qubits.append([k for k in range(num_qubit // 2, num_qubit)])

    for ts in tn.tensors:
        q = ts.qubits
        if max(q) in qubits[0]:
            res[level][0].append(ts)
        elif min(q) in qubits[1]:
            res[level][1].append(ts)
        else:
            cx_num += 1
            if cx_num <= cx_max:
                if q[-1] in qubits[0]:
                    res[level][0].append(ts)
                else:
                    res[level][1].append(ts)
            else:
                level += 1
                res.append([])
                res[level].append([])
                res[level].append([])
                if q[-1] in qubits[0]:
                    res[level][0].append(ts)
                else:
                    res[level][1].append(ts)
                cx_num = 1

    #     print('circuit blocks:',2*(level+1))
    return res


def circuit_partion2(tn):
    """The first partition scheme;
    cx_max is the number of CNOTs allowed to be cut
    """
    res = [[[], [], []]]

    cx_num = 0
    num_qubit = tn.qubits_num
    cx_max = num_qubit // 2
    c_part_width = num_qubit // 2 + 1
    level = 0

    qubits = []
    qubits.append([k for k in range(num_qubit // 2)])
    qubits.append([k for k in range(num_qubit // 2, num_qubit)])
    qubits.append([])
    c_range = [num_qubit, 0]

    for ts in tn.tensors:
        q = ts.qubits

        if max(q) in qubits[0]:
            res[level][0].append(ts)
        elif min(q) in qubits[1]:
            res[level][1].append(ts)
        elif min(q) in qubits[2] and max(q) in qubits[2]:
            res[level][2].append(ts)
        else:
            if cx_num < cx_max:
                cx_num += 1
                if q[-1] in qubits[0]:
                    res[level][0].append(ts)
                else:
                    res[level][1].append(ts)
            else:
                c_width = max(c_range[1], max(q)) - min(c_range[0], min(q)) + 1
                if c_width < c_part_width:
                    res[level][2].append(ts)
                    c_range[0] = min(c_range[0], min(q))
                    c_range[1] = max(c_range[1], max(q))
                    qubits[0] = [k for k in range(0, c_range[0])]
                    qubits[1] = [k for k in range(c_range[1] + 1, num_qubit)]
                    qubits[2] = [k for k in range(c_range[0], c_range[1] + 1)]
                else:
                    level += 1
                    res.append([])
                    res[level].append([])
                    res[level].append([])
                    res[level].append([])
                    qubits.clear()
                    qubits.append([k for k in range(num_qubit // 2)])
                    qubits.append([k for k in range(num_qubit // 2, num_qubit)])
                    qubits.append([])
                    c_range = [num_qubit, 0]

                    if max(q) in qubits[0]:
                        res[level][0].append(ts)
                        cx_num = 0
                    elif min(q) in qubits[1]:
                        res[level][1].append(ts)
                        cx_num = 0
                    else:
                        if q[-1] in qubits[0]:
                            res[level][0].append(ts)
                        else:
                            res[level][1].append(ts)
                        cx_num = 1

    #     print('circuit blocks:',3*(level+1))
    return res
