import unittest

import torch

from tfm_brats.monai_pipeline import build_model


def _gating(model_config):
    model = build_model({"architecture": "residual_unet_3d", "fusion": "adaptive_gating", **model_config})
    return model, model.fusion


class AdaptiveGatingTests(unittest.TestCase):
    def test_mean_only_gate_input_dim(self):
        _, gate = _gating({})
        self.assertEqual(gate.gate[0].in_features, 4)  # 4 channels x 1 stat

    def test_mean_std_gate_input_dim(self):
        _, gate = _gating({"fusion_stats": ["mean", "std"]})
        self.assertEqual(gate.gate[0].in_features, 8)  # 4 channels x 2 stats

    def test_forward_shape_and_entropy(self):
        model, gate = _gating({"fusion_stats": ["mean", "std"]})
        x = torch.randn(2, 4, 32, 32, 32)
        y = model(x)
        self.assertEqual(tuple(y.shape), (2, 3, 32, 32, 32))
        self.assertIsNotNone(gate.last_entropy)
        self.assertGreater(float(gate.last_entropy), 0.0)

    def test_warmup_alpha_zero_is_identity(self):
        _, gate = _gating({})
        x = torch.randn(2, 4, 16, 16, 16)
        gate.warmup_alpha.fill_(0.0)
        with torch.no_grad():
            self.assertTrue(torch.allclose(gate(x), x, atol=1e-6))
        gate.warmup_alpha.fill_(1.0)
        with torch.no_grad():
            self.assertFalse(torch.allclose(gate(x), x, atol=1e-4))

    def test_temperature_stored(self):
        _, gate = _gating({"fusion_temperature": 2.0})
        self.assertAlmostEqual(gate.temperature, 2.0)

    def test_warmup_alpha_not_in_state_dict(self):
        model, _ = _gating({})
        self.assertFalse(any("warmup_alpha" in k for k in model.state_dict()))


if __name__ == "__main__":
    unittest.main()
