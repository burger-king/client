import unittest
import numpy as np
from bkpm.adapters import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from sklearn.cross_validation import train_test_split


class AdaptersTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_linear_regression(self):
        X, y = make_regression(n_samples=1000, n_features=100, n_informative=10)
        X_train, X_test, y_train, y_test = train_test_split(X, y)
        model = LinearRegression()
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)

        sklearn.save(model, '/tmp/')
        model_ = sklearn.load('/tmp/')
        score_ = model.score(X_test, y_test)
        self.assertEquals(score, score_)
        self.assertTrue(np.array_equal(model.coef_, model_.coef_))
        self.assertEquals(model.intercept_, model_.intercept_)

