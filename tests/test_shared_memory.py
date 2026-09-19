import pytest
np = pytest.importorskip('numpy')
from sounio.integrations.numpy_ext import UncertainArray


def test_shared_memory_round_trip_owns_data_after_unlink():
    original = UncertainArray([1, 2], [0.1, 0.2], 'sensor')
    names = original.to_shared_memory()
    try:
        restored = UncertainArray.from_shared_memory(*names)
    finally:
        UncertainArray.free_shared_memory(*names[:2])
    np.testing.assert_array_equal(restored.values, original.values)
    np.testing.assert_array_equal(restored.epsilons, original.epsilons)
    assert restored.provenance == 'sensor'
