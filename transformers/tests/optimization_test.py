# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function

import unittest

import numpy as np
import torch

from transformers import (AdamW, ConstantLRSchedule, WarmupConstantSchedule,
                          WarmupCosineSchedule,
                          WarmupCosineWithHardRestartsSchedule,
                          WarmupLinearSchedule)


def unwrap_schedule(scheduler, num_steps=10):
    lrs = []
    for _ in range(num_steps):
        scheduler.step()
        lrs.append(scheduler.get_lr())
    return lrs


class OptimizationTest(unittest.TestCase):

    def assertListAlmostEqual(self, list1, list2, tol):
        self.assertEqual(len(list1), len(list2))
        for a, b in zip(list1, list2):
            self.assertAlmostEqual(a, b, delta=tol)

    def test_adam_w(self):
        w = torch.tensor([0.1, -0.2, -0.1], requires_grad=True)
        target = torch.tensor([0.4, 0.2, -0.5])
        criterion = torch.nn.MSELoss()
        # No warmup, constant schedule, no gradient clipping
        optimizer = AdamW(params=[w], lr=2e-1, weight_decay=0.0)
        for _ in range(100):
            loss = criterion(w, target)
            loss.backward()
            optimizer.step()
            # No zero_grad() function on simple tensors. we do it ourselves.
            w.grad.detach_()
            w.grad.zero_()
        self.assertListAlmostEqual(w.tolist(), [0.4, 0.2, -0.5], tol=1e-2)


class ScheduleInitTest(unittest.TestCase):
    m = torch.nn.Linear(50, 50)
    optimizer = AdamW(m.parameters(), lr=10.)
    num_steps = 10

    def assertListAlmostEqual(self, list1, list2, tol):
        self.assertEqual(len(list1), len(list2))
        for a, b in zip(list1, list2):
            self.assertAlmostEqual(a, b, delta=tol)

    def test_constant_scheduler(self):
        scheduler = ConstantLRSchedule(self.optimizer)
        lrs = unwrap_schedule(scheduler, self.num_steps)
        expected_learning_rates = [10.] * self.num_steps
        self.assertEqual(len(lrs[0]), 1)
        self.assertListEqual([l[0] for l in lrs], expected_learning_rates)

    def test_warmup_constant_scheduler(self):
        scheduler = WarmupConstantSchedule(self.optimizer, warmup_steps=4)
        lrs = unwrap_schedule(scheduler, self.num_steps)
        expected_learning_rates = [2.5, 5.0, 7.5,
                                   10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0]
        self.assertEqual(len(lrs[0]), 1)
        self.assertListEqual([l[0] for l in lrs], expected_learning_rates)

    def test_warmup_linear_scheduler(self):
        scheduler = WarmupLinearSchedule(
            self.optimizer, warmup_steps=2, t_total=10)
        lrs = unwrap_schedule(scheduler, self.num_steps)
        expected_learning_rates = [5.0, 10.0, 8.75,
                                   7.5, 6.25, 5.0, 3.75, 2.5, 1.25, 0.0]
        self.assertEqual(len(lrs[0]), 1)
        self.assertListEqual([l[0] for l in lrs], expected_learning_rates)

    def test_warmup_cosine_scheduler(self):
        scheduler = WarmupCosineSchedule(
            self.optimizer, warmup_steps=2, t_total=10)
        lrs = unwrap_schedule(scheduler, self.num_steps)
        expected_learning_rates = [5.0, 10.0, 9.61,
                                   8.53, 6.91, 5.0, 3.08, 1.46, 0.38, 0.0]
        self.assertEqual(len(lrs[0]), 1)
        self.assertListAlmostEqual(
            [l[0] for l in lrs], expected_learning_rates, tol=1e-2)

    def test_warmup_cosine_hard_restart_scheduler(self):
        scheduler = WarmupCosineWithHardRestartsSchedule(
            self.optimizer, warmup_steps=2, cycles=2, t_total=10)
        lrs = unwrap_schedule(scheduler, self.num_steps)
        expected_learning_rates = [5.0, 10.0, 8.53,
                                   5.0, 1.46, 10.0, 8.53, 5.0, 1.46, 0.0]
        self.assertEqual(len(lrs[0]), 1)
        self.assertListAlmostEqual(
            [l[0] for l in lrs], expected_learning_rates, tol=1e-2)


if __name__ == "__main__":
    unittest.main()
