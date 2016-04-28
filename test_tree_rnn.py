import tree_rnn

import theano
from theano import tensor as T
import numpy as np
from numpy.testing import assert_array_almost_equal


class DummyTreeRNN(tree_rnn.TreeRNN):

    def create_recursive_unit(self):
        def unit(child_emb):
            return 1.0 + T.prod(child_emb, axis=0)
        return unit


def test_tree_rnn():
    model = DummyTreeRNN(8, 2, 1, degree=2)
    leaf_emb = model.embeddings.get_value()

    root = tree_rnn.Node()
    c1 = tree_rnn.Node(1)
    c2 = tree_rnn.Node(2)
    root.add_children([c1, c2])

    x, tree = tree_rnn.gen_nn_inputs(root)
    root_emb = model.evaluate(x, tree[:, :-1])
    expected = 1 + leaf_emb[1] * leaf_emb[2]
    assert_array_almost_equal(expected, root_emb)

    cc1 = tree_rnn.Node(5)
    cc2 = tree_rnn.Node(2)
    c2.val = None
    c2.add_children([cc1, cc2])

    x, tree = tree_rnn.gen_nn_inputs(root)
    root_emb = model.evaluate(x, tree[:, :-1])
    expected = 1 + (1 + leaf_emb[5] * leaf_emb[2]) * leaf_emb[1]
    assert_array_almost_equal(expected, root_emb)

    ccc1 = tree_rnn.Node(5)
    ccc2 = tree_rnn.Node(4)
    cc1.val = None
    cc1.add_children([ccc1, ccc2])

    x, tree = tree_rnn.gen_nn_inputs(root)
    root_emb = model.evaluate(x, tree[:, :-1])
    expected = 1 + (1 + (1 + leaf_emb[5] * leaf_emb[4]) * leaf_emb[2]) * leaf_emb[1]
    assert_array_almost_equal(expected, root_emb)

    # check step works without error
    model.train_step(root, np.array([0]).astype(theano.config.floatX))

    # degree > 2
    model = DummyTreeRNN(10, 2, 1, degree=3)
    leaf_emb = model.embeddings.get_value()

    root = tree_rnn.Node()
    c1 = tree_rnn.Node(1)
    c2 = tree_rnn.Node(2)
    c3 = tree_rnn.Node(3)
    root.add_children([c1, c2, c3])

    cc1 = tree_rnn.Node(1)
    cc2 = tree_rnn.Node(2)
    cc3 = tree_rnn.Node(3)
    cc4 = tree_rnn.Node(4)
    cc5 = tree_rnn.Node(5)
    cc6 = tree_rnn.Node(6)
    cc7 = tree_rnn.Node(7)
    cc8 = tree_rnn.Node(8)
    cc9 = tree_rnn.Node(9)

    c1.add_children([cc1, cc2, cc3])
    c2.add_children([cc4, cc5, cc6])
    c3.add_children([cc7, cc8, cc9])

    x, tree = tree_rnn.gen_nn_inputs(root)
    root_emb = model.evaluate(x, tree[:, :-1])
    expected = \
        1 + ((1 + leaf_emb[1] * leaf_emb[2] * leaf_emb[3]) *
             (1 + leaf_emb[4] * leaf_emb[5] * leaf_emb[6]) *
             (1 + leaf_emb[7] * leaf_emb[8] * leaf_emb[9]))
    assert_array_almost_equal(expected, root_emb)

    # check step works without error
    model.train_step(root, np.array([0]).astype(theano.config.floatX))
