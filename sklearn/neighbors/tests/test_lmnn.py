import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_true
from sklearn import datasets
from sklearn.neighbors import LargeMarginNearestNeighbor as LMNN

rng = np.random.RandomState(0)
# load and shuffle iris dataset
iris = datasets.load_iris()
perm = rng.permutation(iris.target.size)
iris.data = iris.data[perm]
iris.target = iris.target[perm]

# load and shuffle digits
digits = datasets.load_digits()
perm = rng.permutation(digits.target.size)
digits.data = digits.data[perm]
digits.target = digits.target[perm]


def test_neighbors_iris():
    # Sanity checks on the iris dataset
    # Puts three points of each label in the plane and performs a
    # nearest neighbor query on points near the decision boundary.

    clf = LMNN(n_neighbors=1)
    clf.fit(iris.data, iris.target)
    assert_array_equal(clf.predict(iris.data), iris.target)

    clf.set_params(n_neighbors=9)
    clf.fit(iris.data, iris.target)

    assert_true(clf.score(iris.data, iris.target) > 0.95)


def test_neighbors_digits():
    # Sanity check on the digits dataset
    # the 'brute' algorithm has been observed to fail if the input
    # dtype is uint8 due to overflow in distance calculations.

    X = digits.data.astype('uint8')
    y = digits.target
    n_samples, n_features = X.shape
    train_test_boundary = int(n_samples * 0.8)
    train = np.arange(0, train_test_boundary)
    test = np.arange(train_test_boundary, n_samples)
    X_train, y_train, X_test, y_test = X[train], y[train], X[test], y[test]

    clf = LMNN(n_neighbors=1, max_iter=50)
    score_uint8 = clf.fit(X_train, y_train).score(X_test, y_test)
    score_float = clf.fit(X_train.astype(float), y_train).score(
        X_test.astype(float), y_test)
    assert_equal(score_uint8, score_float)


def test_params_errors():
    # Test that invalid parameters raise value error
    X = np.arange(12).reshape(4, 3)
    y = [1, 1, 2, 2]
    clf = LMNN

    # TypeError
    assert_raises(TypeError, clf(n_neighbors=1.3).fit, X, y)
    assert_raises(TypeError, clf(max_iter='21').fit, X, y)
    assert_raises(TypeError, clf(verbose='true').fit, X, y)
    assert_raises(TypeError, clf(max_constraints=23.1).fit, X, y)
    assert_raises(TypeError, clf(max_corrections=1e3).fit, X, y)
    assert_raises(TypeError, clf(tol=1).fit, X, y)
    assert_raises(TypeError, clf(n_features_out='invalid').fit, X, y)
    assert_raises(TypeError, clf(use_pca=1).fit, X, y)
    assert_raises(TypeError, clf(n_jobs='yes').fit, X, y)
    assert_raises(TypeError, clf(warm_start=1).fit, X, y)
    assert_raises(TypeError, clf(use_sparse=0.5).fit, X, y)

    # ValueError
    assert_raises(ValueError, clf(n_neighbors=-1).fit, X, y)
    assert_raises(ValueError, clf(n_neighbors=len(X)).fit, X, y)
    assert_raises(ValueError, clf(max_iter=-1).fit, X, y)
    assert_raises(ValueError, clf(max_constraints=-1).fit, X, y)
    assert_raises(ValueError, clf(max_corrections=-1).fit, X, y)
    assert_raises(ValueError, clf(L=np.random.rand(5, 3)).fit, X, y)
    assert_raises(ValueError, clf(n_features_out=10).fit, X, y)
    assert_raises(ValueError, clf(n_jobs=-2).fit, X, y)

    # test min_class_size < 2
    y = [1, 1, 1, 2]
    assert_raises(ValueError, clf(n_neighbors=1).fit, X, y)


def test_same_lmnn_parallel():
    X, y = datasets.make_classification(n_samples=30, n_features=5,
                                        n_redundant=0, random_state=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    clf = LMNN(n_neighbors=3)
    clf.fit(X_train, y_train)
    y = clf.predict(X_test)

    clf.set_params(n_jobs=3)
    clf.fit(X_train, y_train)
    y_parallel = clf.predict(X_test)

    assert_array_equal(y, y_parallel)


# def test_dtype_convert():
#     classifier = LMNN(n_neighbors=1)
#     CLASSES = 15
#     X = np.eye(CLASSES)
#     y = [ch for ch in 'ABCDEFGHIJKLMNOPQRSTU'[:CLASSES]]
#
#     result = classifier.fit(X, y).predict(X)
#     assert_array_equal(result, y)


# TODO: TESTS
def test_L():

    X = np.arange(12).reshape(4, 3)
    y = [1, 1, 2, 2]

    L = [[1, 2], [3, 4]]  # len(L[0]) != len(X[0])
    assert_raises(ValueError, LMNN(L=L, n_neighbors=1).fit, X, y)

    L = [[1, 2], [3, 4], [5, 6]]  # len(L) > len(L[0])
    assert_raises(ValueError, LMNN(L=L, n_neighbors=1).fit, X, y)

    L = np.arange(9).reshape(3, 3)
    LMNN(L=L, n_neighbors=1).fit(X, y)


def test_n_neighbors():
    pass


def test_n_features_out():

    X = np.arange(12).reshape(4, 3)
    y = [1, 1, 2, 2]

    L = [[1, 2, 3], [4, 5, 6]]  # len(L) != n_features_out
    clf = LMNN(L=L, n_neighbors=1, n_features_out=5)
    assert_raises(ValueError, clf.fit, X, y)

    # n_features_out > len(X[0])
    clf = LMNN(L=L, n_neighbors=1, n_features_out=5)
    assert_raises(ValueError, clf.fit, X, y)

    # n_features_out < len(L) = np.eye(len(X[0])).shape[0]
    clf = LMNN(n_neighbors=1, n_features_out=2, use_pca=False)
    clf.fit(X, y)


def test_L__n_features_out_combinations():
    pass


def test_use_pca():
    X, y = datasets.make_classification(n_samples=30, n_features=5,
                                        n_redundant=0, random_state=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    clf = LMNN(n_neighbors=3, use_pca=False)
    clf.fit(X_train, y_train)
    n_iter_no_pca = clf.details_['nit']

    clf = LMNN(n_neighbors=3, use_pca=True)
    clf.fit(X_train, y_train)
    n_iter_pca = clf.details_['nit']

    assert_true(n_iter_pca <= n_iter_no_pca)


def test_L__n_features_out__use_pca_combinations():
    pass


def test_max_constraints():
    clf = LMNN(n_neighbors=3, max_constraints=1, use_sparse=True)
    clf.fit(iris.data, iris.target)

    clf = LMNN(n_neighbors=3, max_constraints=1, use_sparse=False)
    clf.fit(iris.data, iris.target)


def test_use_sparse():
    X = iris.data
    y = iris.target
    n_samples, n_features = X.shape
    train_test_boundary = int(n_samples * 0.8)
    train = np.arange(0, train_test_boundary)
    test = np.arange(train_test_boundary, n_samples)
    X_train, y_train, X_test, y_test = X[train], y[train], X[test], y[test]

    clf = LMNN(n_neighbors=3, use_sparse=False)
    clf.fit(X_train, y_train)
    acc_sparse = clf.score(X_test, y_test)

    clf = LMNN(n_neighbors=3, use_sparse=True)
    clf.fit(X_train, y_train)
    acc_dense = clf.score(X_test, y_test)

    err_msg = 'Toggling use_sparse results in different accuracy.'
    assert_equal(acc_dense, acc_sparse, msg=err_msg)


def test_warm_start():
    # A 1-iteration second fit on same data should give almost same result
    # with warm starting, and quite different result without warm starting.

    X, y = datasets.make_classification(n_samples=30, n_features=5,
                                        n_redundant=0, random_state=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    n_iter = 10

    clf_warm = LMNN(n_neighbors=3, warm_start=True, max_iter=n_iter,
                    random_state=0).fit(X_train, y_train)
    L_warm = clf_warm.L_
    clf_warm.max_iter = 1
    clf_warm.fit(X_train, y_train)
    L_warm_plus_one = clf_warm.L_

    clf_cold = LMNN(n_neighbors=3, warm_start=False, max_iter=n_iter,
                    random_state=0).fit(X_train, y_train)
    L_cold = clf_cold.L_
    clf_cold.max_iter = 1
    clf_cold.fit(X_train, y_train)
    L_cold_plus_one = clf_cold.L_

    diff_warm = np.sum(np.abs(L_warm_plus_one - L_warm))
    diff_cold = np.sum(np.abs(L_cold_plus_one - L_cold))

    err_msg = "Transformer changed significantly after one iteration even " \
              "though it was warm-started."

    assert_true(diff_warm < 2.0, err_msg)

    err_msg = "Cold-started transformer changed less significantly than " \
              "warm-started transformer after one iteration."
    assert_true(diff_cold > diff_warm, err_msg)


def test_verbose():
    clf = LMNN(n_neighbors=3, verbose=1)
    clf.fit(iris.data, iris.target)


def test_random_state():
    """Assert that when having more than max_constraints (forcing sampling),
    the same constraints will be sampled given the same random_state and
    different constraints will be sampled given a different random_state"""

    X = iris.data
    y = iris.target
    n_constr = 5

    clf = LMNN(n_neighbors=3, max_constraints=n_constr, random_state=1)
    clf.fit(X, y)
    L_1 = clf.L_

    clf = LMNN(n_neighbors=3, max_constraints=n_constr, random_state=1)
    clf.fit(X, y)
    L_2 = clf.L_

    assert_array_equal(L_1, L_2)

    clf = LMNN(n_neighbors=3, max_constraints=n_constr, random_state=2)
    clf.fit(X, y)
    L_3 = clf.L_

    diff = np.sum(np.abs(L_2, L_3))
    assert_true(diff > 0.2)
