# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 Opentensor Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import random
import bittensor as bt
from datasets import load_dataset
from collections.abc import Iterator

class QnADataset(Iterator):
    def __init__(self):
        super().__init__()
        seed = random.randint(0, 1000)
        self.datasets = [ 
            iter(
                load_dataset("openwebtext", split="train", streaming=True, trust_remote_code=True).shuffle(
                    seed=seed, buffer_size=10000
                )
            ),
            iter(
                load_dataset(
                    "togethercomputer/RedPajama-Data-1T",
                    "default",
                    split="train",
                    trust_remote_code=True,
                    streaming=True,
                ).shuffle(seed=seed, buffer_size=10000)
            )
        ]

    def __next__(self):
        bt.logging.debug("Retrieving data from dataset...")
        while True:
            try:
                ds = random.choice(self.datasets)
                text = next(ds)["text"]

                # Check if the text is not empty or does not consist only of newline characters
                if text.strip():
                    return {"text": text}

            except Exception as e:
                bt.logging.debug(f"HuggingFace issue ... {e}")
                time.sleep(15)


class SummaryDataset(Iterator):
    def __init__(self):
        super().__init__()
        seed = random.randint(0, 1000)
        self.keys = {"cnn_dailymail": {"text": "article", "summary": "highlights"},
                     "samsum": {"text": "dialogue", "summary":"summary"}}
        self.datasets = { 
            "samsum": iter(
                load_dataset("samsum", split="train", streaming=True, trust_remote_code=True).shuffle(
                    seed=seed, buffer_size=10000
                )
            ),
            "cnn_dailymail": iter(
                load_dataset("cnn_dailymail", "3.0.0", split="train", streaming=True, trust_remote_code=True).shuffle(
                    seed=seed, buffer_size=10000)
            )
        }

    def __next__(self):
        bt.logging.debug("Retrieving data from dataset...")
        while True:
            try:
                dname, ds = random.choice(list(self.datasets.items()))
                data = next(ds)
                text = data[self.keys[dname]["text"]]
                summary = data[self.keys[dname]["summary"]]

                # Check if the text is not empty or does not consist only of newline characters
                if text.strip():
                    return {"text": text, "summary": summary}
            except Exception as e:
                bt.logging.debug(f"HuggingFace issue ... {e}")
                time.sleep(15)
