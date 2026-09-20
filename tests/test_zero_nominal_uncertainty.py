import pytest
from sounio.knowledge import Knowledge as Legacy
from sounio._knowledge import Knowledge as Epistemic


@pytest.mark.parametrize('value', [3.0, -3.0])
def test_zero_product_preserves_absolute_uncertainty(value):
    result = Legacy(0, 2) * Legacy(value, 0.5)
    assert result.value == 0
    assert result.epsilon == pytest.approx(6)


@pytest.mark.parametrize('type_,field', [(Legacy, 'epsilon'), (Epistemic, 'uncertainty')])
@pytest.mark.parametrize('denominator', [4.0, -4.0])
def test_zero_numerator_preserves_absolute_uncertainty(type_, field, denominator):
    result = type_(0, 2) / type_(denominator, 0.5)
    assert result.value == 0
    assert getattr(result, field) == pytest.approx(0.5)


def test_uncertain_zero_is_not_reported_as_perfect_precision():
    assert Legacy(0, 2).relative_uncertainty == float('inf')
    assert Legacy(0, 2).confidence == 0
    assert Legacy(0, 0).relative_uncertainty == 0


def test_negative_standard_uncertainty_is_rejected():
    with pytest.raises(ValueError):
        Legacy(1, -1)


def test_scale_preserves_provenance_chain():
    value = Legacy.tracked(2, 0.1, 'source')
    result = value.scale(3)
    assert result.chain is not None
    assert result.ancestry()


@pytest.mark.parametrize('operation', [lambda x: x + 2, lambda x: x - 2, lambda x: 2 - x, lambda x: 2 / x])
def test_scalar_operations_preserve_ancestry(operation):
    value = Legacy.tracked(4, 0.1, 'measurement')
    result = operation(value)
    assert result.chain is not None
    assert any(node.label == 'measurement' for node in result.ancestry())


def test_provenance_refuses_unknown_parent():
    from sounio.provenance import ProvenanceChain
    with pytest.raises(ValueError, match='Unknown provenance parent'):
        ProvenanceChain().add_node('broken', 'add', 1, 0.1, ['missing'])
