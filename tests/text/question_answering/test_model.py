# Copyright The PyTorch Lightning team.
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
import collections
import os
from typing import Any

import pytest
import torch

from flash import Trainer
from flash.core.utilities.imports import _TEXT_AVAILABLE, _TEXT_TESTING
from flash.text import QuestionAnsweringTask
from tests.helpers.task_tester import TaskTester

# ======== Mock functions ========

SEQUENCE_LENGTH = 384


class DummyDataset(torch.utils.data.Dataset):
    def __getitem__(self, index):
        return {
            "input_ids": torch.randint(1000, size=(SEQUENCE_LENGTH,)),
            "attention_mask": torch.randint(1, size=(SEQUENCE_LENGTH,)),
            "start_positions": torch.randint(1000, size=(1,)),
            "end_positions": torch.randint(1000, size=(1,)),
        }

    def __len__(self) -> int:
        return 100


# ==============================

TEST_BACKBONE = "distilbert-base-uncased"


class TestQuestionAnsweringTask(TaskTester):

    task = QuestionAnsweringTask
    task_kwargs = {"backbone": TEST_BACKBONE}
    cli_command = "question_answering"
    is_testing = _TEXT_TESTING
    is_available = _TEXT_AVAILABLE

    scriptable = False
    traceable = False

    @property
    def example_forward_input(self):
        return {
            "input_ids": torch.randint(1000, size=(1, 32)),
            "attention_mask": torch.randint(1, size=(1, 32)),
            "start_positions": torch.randint(1000, size=(1, 1)),
            "end_positions": torch.randint(1000, size=(1, 1)),
        }

    def check_forward_output(self, output: Any):
        assert isinstance(output[0], torch.Tensor)
        assert isinstance(output[1], collections.OrderedDict)


@pytest.mark.skipif(not _TEXT_TESTING, reason="text libraries aren't installed.")
def test_modules_to_freeze():
    model = QuestionAnsweringTask(backbone=TEST_BACKBONE)
    assert model.modules_to_freeze() is model.model.distilbert


@pytest.mark.skipif(os.name == "nt", reason="Huggingface timing out on Windows")
@pytest.mark.skipif(not _TEXT_TESTING, reason="text libraries aren't installed.")
def test_init_train(tmpdir):
    model = QuestionAnsweringTask(TEST_BACKBONE)
    train_dl = torch.utils.data.DataLoader(DummyDataset())
    trainer = Trainer(default_root_dir=tmpdir, fast_dev_run=True)
    trainer.fit(model, train_dl)
