import numpy as np
from numpy.testing import assert_allclose
import pytest

from this_tutorial.knn_ray import create_grid, create_query_points, calculate_distances, knn_search, compute_prices, split_into_batches


def test_create_grid():
    x, y = create_grid(n_points=5)
    assert x.shape == (25,)
    assert y.shape == (25,)
    assert x[0] == -10.0
    assert x[-1] == 10.0
    assert y[0] == -10.0
    assert y[-1] == 10.0


def test_create_query_points():
    query_points = create_query_points(n_points=5, floor=2)
    assert query_points.shape == (25, 3)
    assert np.all(query_points[:,2] == 2)  # Floor should be constant at 2
    assert np.all(query_points[:,0] >= -10) and np.all(query_points[:,0] <= 10)
    assert np.all(query_points[:,1] >= -10) and np.all(query_points[:,1] <= 10)
    assert_allclose(query_points[17], np.asarray([0., 5., 2.]))


def test_calculate_distances():
    query_points = np.array([[0, 0, 1], [1, 1, 1]])
    reference_points = np.array([[0, 0, 0], [1, 1, 0], [2, 2, 0], [1, 1, 1]])
    
    distances = calculate_distances(query_points, reference_points)
    assert distances.shape == (2, 4)

    
    expected_distances = np.array([
        [1.0, np.sqrt(3), 3.0, np.sqrt(2)],
        [np.sqrt(3), 1.0, np.sqrt(3), 0.0]
    ])
    
    assert_allclose(distances, expected_distances)


def test_knn_search():
    query_points = np.array([[0, 0, 1], [3, 3, 3]])
    reference_points = np.array([[0, 0, 0, 7], [1, 1, 0, 2], [2, 2, 0, 5], [1, 1, 1, 6]])
    
    k = 2
    indices = knn_search(query_points, reference_points, k)
    
    assert indices.shape == (2, k)
    expected_indices = np.array([[0, 3], [2, 3]])

    assert np.array_equal(indices, expected_indices) 


def test_compute_prices():
    query_points = np.array([[0, 0, 1], [3, 3, 3]])
    reference_points = np.array([[0, 0, 0, 7], [1, 1, 0, 2], [2, 2, 0, 5], [1, 1, 1, 6]])
    
    prices = compute_prices(query_points, reference_points, k=2)
    
    assert prices.shape == (2,)
    expected_prices = np.array([6.5, 5.5])
    
    assert_allclose(prices, expected_prices)


@pytest.mark.parametrize(
    ("points", "batch_size", "n_batches", "last_batch_size"),
    [
        (99, 10, 10, 9),
        (100, 10, 10, 10),
        (101, 10, 11, 1),
        (1, 1, 1, 1),
    ]
)
def test_split_into_batches(points, batch_size, n_batches, last_batch_size):
    query_points = np.random.rand(points, 3)
    batches = split_into_batches(query_points, batch_size)
    
    assert len(batches) == n_batches
    for batch in batches:
        assert batch.shape[0] <= batch_size
        assert batch.shape[1] == 3

    batches[-1].shape[0] == last_batch_size