"""Offline tests of the SAE maths on small random tensors."""

import pytest

torch = pytest.importorskip("torch")

from mosaic.sae import ce_recovered, decode, encode, fvu_parts  # noqa: E402


def tiny(d=8, s=32):
    g = torch.Generator().manual_seed(0)
    return {"W_enc": torch.randn(s, d, generator=g), "W_dec": torch.randn(d, s, generator=g),
            "b_enc": torch.zeros(s), "b_dec": torch.zeros(d)}


def test_topk_keeps_exactly_k_and_shapes():
    sae = tiny()
    a = encode(sae, torch.randn(5, 8), k=4)
    assert a.shape == (5, 32) and ((a != 0).sum(-1) == 4).all()
    assert decode(sae, a).shape == (5, 8)


def test_perfect_reconstruction_has_zero_fvu_and_mean_has_one():
    x = torch.randn(50, 8)
    assert fvu_parts(x, x)[0] == 0.0
    rss, tss = fvu_parts(x, x.mean(0, keepdim=True).expand_as(x))
    assert rss == pytest.approx(tss, rel=1e-5)


def test_ce_recovered_endpoints():
    assert ce_recovered(2.0, 2.0, 8.0) == 1.0
    assert ce_recovered(2.0, 8.0, 8.0) == 0.0
