from sklearn.utils.validation import check_X_y
import scipy.sparse as sp

from skpro.base import ProbabilisticEstimator
from skpro.estimators.residuals import ResidualEstimator
import skrpo.distributions.distribution as d


class ParametricEstimator(ProbabilisticEstimator):
    """
    Composite parametric prediction strategy.

    Uses classical estimators to predict the defining parameters of continuous distributions.

    Read more in the :ref:`User Guide <parametric>
    """
    
    def __init__(self, mean_estimator, residuals_estimator, 
                 distribution = d.NormalDistribution(), copy_X=True):
        
        if not isinstance(residuals_estimator, ResidualEstimator):
              raise ValueError("residual estimator is not recognized as a 'ResidualEstimator' object")
        
        self.mean_estimator = mean_estimator
        self.residuals_estimator = residuals_estimator
        self.distribution = distribution
        self.copy_X= copy_X
        
    
    def fit(self, X, y, sample_weight=None):

        X, y = check_X_y(X, y, accept_sparse=['csr', 'csc', 'coo'],
                         y_numeric=True, multi_output=True)
        
        if self.copy_X :
            if sp.issparse(X):
                X = X.copy()
            else:
                X = X.copy(order='K')

        self.mean_estimator.fit(X, y, sample_weight)
        self.residual_estimator.linkToEstimator(self.mean_estimator)
        self.residual_estimator.fit(X, y)
        
        return self
    
    
    def predict_proba(self, X):
        
        allowed_distribution = ("normal", "laplace")
        if self.distribution.name() not in allowed_distribution:
            raise ValueError("Unknown strategy type: %s, expected one of %s."
                             % (self.distribution.name(), allowed_distribution))

        if self.copy_X :
            if sp.issparse(X):
                X = X.copy()
            else:
                X = X.copy(order='K')

        return type(self.distribution)(
                self.mean_estimator.predict(X),
                self.residual_estimator.predict(X)
                )
    

    def __repr__(self):
        return self.__str__(repr)