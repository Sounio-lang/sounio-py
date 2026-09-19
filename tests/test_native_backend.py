"""Optional native tests; CI native stage must install the extension first."""
import pytest

native = pytest.importorskip('sounio.native')


def test_native_install_does_not_change_legacy_constructor():
    import sounio
    assert sounio.Knowledge is sounio.PureKnowledge
    assert sounio.Knowledge(2, 0.1, 'source').provenance == 'source'
    assert native.Knowledge(2, 0.1, 0.8).confidence == 0.8


@pytest.mark.parametrize('nominal', [3.0, -3.0])
def test_native_zero_multiplication(nominal):
    result = native.Knowledge(0, 2) * native.Knowledge(nominal, 0.5)
    assert result.uncertainty == pytest.approx(6)


@pytest.mark.parametrize('nominal', [4.0, -4.0])
def test_native_zero_division(nominal):
    result = native.Knowledge(0, 2) / native.Knowledge(nominal, 0.5)
    assert result.uncertainty == pytest.approx(0.5)


def test_mutable_native_value_cannot_be_hashed():
    with pytest.raises(TypeError):
        hash(native.Knowledge(1, 0.1))


def test_uncertain_zero_is_not_reliable():
    value = native.Knowledge(0, 1)
    assert value.relative_uncertainty == float('inf')
    assert not value.is_reliable()
