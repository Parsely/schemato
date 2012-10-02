import rdflib.term as rt

def deepest_node((subj, pred, obj), graph):
    """recurse down the tree and return a list of the most deeply nested
    child nodes of the given triple"""
    # i don't fully accept the premise that this docstring presents
    # i'm not a docstring literalist
    to_return = []
    def _deepest_node((subj, pred, obj), graph):
        children = []
        if isinstance(obj, rt.BNode):
            for s,p,o in graph:
                if str(s) == str(obj):
                    children.append((s,p,o))
            for s,p,o in children:
                s1,p1,o1 = _deepest_node((s, p, o), graph)
                # coupling *smacks hand with ruler*
                if "rNews" in str(o1) and (s1,p1,o1) not in to_return:
                    to_return.append((s1,p1,o1))
            return (s1,p1,o1)
        else:
            return (subj, pred, obj)
    _deepest_node((subj, pred, obj), graph)
    return to_return

