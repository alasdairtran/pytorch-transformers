# 👾 PyTorch-Transformers

[![CircleCI](https://circleci.com/gh/huggingface/pytorch-pretrained-BERT.svg?style=svg)](https://circleci.com/gh/huggingface/pytorch-pretrained-BERT)

PyTorch-Transformers is a library of state-of-the-art pre-trained models for Natural Language Processing (NLP).

The library currently contains PyTorch implementations, pre-trained model weights, usage scripts and conversion utilities for the following models:

- **[Google's BERT model](https://github.com/google-research/bert)** released with the paper [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) by Jacob Devlin, Ming-Wei Chang, Kenton Lee and Kristina Toutanova.
- **[OpenAI's GPT model](https://github.com/openai/finetune-transformer-lm)** released  with the paper [Improving Language Understanding by Generative Pre-Training](https://blog.openai.com/language-unsupervised/) by Alec Radford, Karthik Narasimhan, Tim Salimans and Ilya Sutskever.
- **[OpenAI's GPT-2 model](https://blog.openai.com/better-language-models/)** released with the paper [Language Models are Unsupervised Multitask Learners](https://blog.openai.com/better-language-models/) by Alec Radford*, Jeffrey Wu*, Rewon Child, David Luan, Dario Amodei** and Ilya Sutskever**.
- **[Google/CMU's Transformer-XL model](https://github.com/kimiyoung/transformer-xl)** released with the paper [Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context](https://arxiv.org/abs/1901.02860) by Zihang Dai*, Zhilin Yang*, Yiming Yang, Jaime Carbonell, Quoc V. Le, Ruslan Salakhutdinov.
- **[Google/CMU's XLNet model](https://github.com/zihangdai/xlnet/)** released with the paper [​XLNet: Generalized Autoregressive Pretraining for Language Understanding](https://arxiv.org/abs/1906.08237) by Zhilin Yang*, Zihang Dai*, Yiming Yang, Jaime Carbonell, Ruslan Salakhutdinov, Quoc V. Le.
- **[Facebook's XLM model](https://github.com/facebookresearch/XLM/)** released together with the paper [Cross-lingual Language Model Pretraining](https://arxiv.org/abs/1901.07291) by Guillaume Lample and Alexis Conneau.

These implementations have been tested on several datasets (see the example scripts) and should match the performances of the original implementations (e.g. ~93 F1 on SQuAD for BERT Whole-Word-Masking, ~88 F1 on RocStories for OpenAI GPT, ~18.3 perplexity on WikiText 103 for Transformer-XL, ~0.916 Peason R coefficient on STS-B for XLNet). You can find more details on the performances in the Examples section of the [documentation](#documentation).

| Section | Description |
|-|-|
| [Installation](#installation) | How to install the package |
| [Quick tour: Usage](#quick-tour-usage) | Tokenizers & models usage: Bert and GPT-2 |
| [Quick tour: Fine-tuning/usage scripts](#quick-tour-fine-tuning/usage-scripts) | Using provided scripts: GLUE, SQuAD and Text generation |
| [Documentation](#documentation) | Full API documentation and more |

## Installation

This repo is tested on Python 2.7 and 3.5+ (examples are tested only on python 3.5+) and PyTorch 0.4.1 to 1.1.0

### With pip

PyTorch-Transformers can be installed by pip as follows:

```bash
pip install pytorch-transformers
```

### From source

Clone the repository and run:

```bash
pip install [--editable] .
```

### Tests

A series of tests is included for the library and the example scripts. Library tests can be found in the [tests folder](https://github.com/huggingface/pytorch-transformers/tree/master/transformers/tests) and examples tests in the [examples folder](https://github.com/huggingface/pytorch-transformers/tree/master/examples).

These tests can be run using `pytest` (install pytest if needed with `pip install pytest`).

You can run the tests from the root of the cloned repository with the commands:

```bash
python -m pytest -sv ./transformers/tests/
python -m pytest -sv ./examples/
```

## Quick tour: Usage

Here are two quick-start examples using `Bert` and `GPT2` with pre-trained models.

See the [documentation](#documentation) for the details of all the models and classes.

### BERT example

First let's prepare a tokenized input from a text string using `BertTokenizer`

```python
import torch
from transformers import BertTokenizer, BertModel, BertForMaskedLM

# OPTIONAL: if you want to have more information on what's happening under the hood, activate the logger as follows
import logging
logging.basicConfig(level=logging.INFO)

# Load pre-trained model tokenizer (vocabulary)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Tokenize input
text = "[CLS] Who was Jim Henson ? [SEP] Jim Henson was a puppeteer [SEP]"
tokenized_text = tokenizer.tokenize(text)

# Mask a token that we will try to predict back with `BertForMaskedLM`
masked_index = 8
tokenized_text[masked_index] = '[MASK]'
assert tokenized_text == ['[CLS]', 'who', 'was', 'jim', 'henson', '?', '[SEP]', 'jim', '[MASK]', 'was', 'a', 'puppet', '##eer', '[SEP]']

# Convert token to vocabulary indices
indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
# Define sentence A and B indices associated to 1st and 2nd sentences (see paper)
segments_ids = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

# Convert inputs to PyTorch tensors
tokens_tensor = torch.tensor([indexed_tokens])
segments_tensors = torch.tensor([segments_ids])
```

Let's see how we can use `BertModel` to encode our inputs in hidden-states:

```python
# Load pre-trained model (weights)
model = BertModel.from_pretrained('bert-base-uncased')

# Set the model in evaluation mode to desactivate the DropOut modules
# This is IMPORTANT to have reproductible results during evaluation!
model.eval()

# If you have a GPU, put everything on cuda
tokens_tensor = tokens_tensor.to('cuda')
segments_tensors = segments_tensors.to('cuda')
model.to('cuda')

# Predict hidden states features for each layer
with torch.no_grad():
    # See the models docstrings for the detail of the inputs
    outputs = model(tokens_tensor, token_type_ids=segments_tensors)
    # PyTorch-Transformers models always output tuples.
    # See the models docstrings for the detail of all the outputs
    # In our case, the first element is the hidden state of the last layer of the Bert model
    encoded_layers = outputs[0]
# We have encoded our input sequence in a FloatTensor of shape (batch size, sequence length, model hidden dimension)
assert tuple(encoded_layers.shape) == (1, len(indexed_tokens), model.config.hidden_size)
```

And how to use `BertForMaskedLM` to predict a masked token:

```python
# Load pre-trained model (weights)
model = BertForMaskedLM.from_pretrained('bert-base-uncased')
model.eval()

# If you have a GPU, put everything on cuda
tokens_tensor = tokens_tensor.to('cuda')
segments_tensors = segments_tensors.to('cuda')
model.to('cuda')

# Predict all tokens
with torch.no_grad():
    outputs = model(tokens_tensor, token_type_ids=segments_tensors)
    predictions = outputs[0]

# confirm we were able to predict 'henson'
predicted_index = torch.argmax(predictions[0, masked_index]).item()
predicted_token = tokenizer.convert_ids_to_tokens([predicted_index])[0]
assert predicted_token == 'henson'
```

### OpenAI GPT-2

Here is a quick-start example using `GPT2Tokenizer` and `GPT2LMHeadModel` class with OpenAI's pre-trained model to predict the next token from a text prompt.

First let's prepare a tokenized input from our text string using `GPT2Tokenizer`

```python
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# OPTIONAL: if you want to have more information on what's happening, activate the logger as follows
import logging
logging.basicConfig(level=logging.INFO)

# Load pre-trained model tokenizer (vocabulary)
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Encode a text inputs
text = "Who was Jim Henson ? Jim Henson was a"
indexed_tokens = tokenizer.encode(text)

# Convert indexed tokens in a PyTorch tensor
tokens_tensor = torch.tensor([indexed_tokens])
```

Let's see how to use `GPT2LMHeadModel` to generate the next token following our text:

```python
# Load pre-trained model (weights)
model = GPT2LMHeadModel.from_pretrained('gpt2')

# Set the model in evaluation mode to desactivate the DropOut modules
# This is IMPORTANT to have reproductible results during evaluation!
model.eval()

# If you have a GPU, put everything on cuda
tokens_tensor = tokens_tensor.to('cuda')
model.to('cuda')

# Predict all tokens
with torch.no_grad():
    outputs = model(tokens_tensor)
    predictions = outputs[0]

# get the predicted next sub-word (in our case, the word 'man')
predicted_index = torch.argmax(predictions[0, -1, :]).item()
predicted_text = tokenizer.decode(indexed_tokens + [predicted_index])
assert predicted_text == 'Who was Jim Henson? Jim Henson was a man'
```

Examples for each model class of each model architecture (Bert, GPT, GPT-2, Transformer-XL, XLNet and XLM) can be found in the [documentation](#documentation).

## Quick tour: Fine-tuning/usage scripts

The library comprises several example scripts with SOTA performances for NLU and NLG tasks:

- fine-tuning Bert/XLNet/XLM with a *sequence-level classifier* on nine different GLUE tasks,
- fine-tuning Bert/XLNet/XLM with a *token-level classifier* on the question answering dataset SQuAD 2.0, and
- using GPT/GPT-2/Transformer-XL and XLNet for conditional language generation.

Here are three quick usage examples for these scripts:

### Fine-tuning for sequence classification: GLUE tasks examples

The [General Language Understanding Evaluation (GLUE) benchmark](https://gluebenchmark.com/) is a collection of nine sentence- or sentence-pair language understanding tasks for evaluating and analyzing natural language understanding systems.

Before running anyone of these GLUE tasks you should download the
[GLUE data](https://gluebenchmark.com/tasks) by running
[this script](https://gist.github.com/W4ngatang/60c2bdb54d156a41194446737ce03e2e)
and unpack it to some directory `$GLUE_DIR`.

```shell
export GLUE_DIR=/path/to/glue
export TASK_NAME=MRPC

python run_bert_classifier.py \
  --task_name $TASK_NAME \
  --do_train \
  --do_eval \
  --do_lower_case \
  --data_dir $GLUE_DIR/$TASK_NAME \
  --bert_model bert-base-uncased \
  --max_seq_length 128 \
  --train_batch_size 32 \
  --learning_rate 2e-5 \
  --num_train_epochs 3.0 \
  --output_dir /tmp/$TASK_NAME/
```

where task name can be one of CoLA, SST-2, MRPC, STS-B, QQP, MNLI, QNLI, RTE, WNLI.

The dev set results will be present within the text file 'eval_results.txt' in the specified output_dir. In case of MNLI, since there are two separate dev sets, matched and mismatched, there will be a separate output folder called '/tmp/MNLI-MM/' in addition to '/tmp/MNLI/'.

#### Fine-tuning XLNet model on the STS-B regression task

This example code fine-tunes XLNet on the STS-B corpus using parallel training on a server with 4 V100 GPUs.
Parallel training is a simple way to use several GPU (but it is slower and less flexible than distributed training, see below).

```shell
export GLUE_DIR=/path/to/glue

python ./examples/run_glue.py \
    --model_type xlnet \
    --model_name_or_path xlnet-large-cased \
    --do_train  \
    --task_name=sts-b     \
    --data_dir=${GLUE_DIR}/STS-B  \
    --output_dir=./proc_data/sts-b-110   \
    --max_seq_length=128   \
    --per_gpu_eval_batch_size=8   \
    --per_gpu_train_batch_size=8   \
    --gradient_accumulation_steps=1 \
    --max_steps=1200  \
    --model_name=xlnet-large-cased   \
    --overwrite_output_dir   \
    --overwrite_cache \
    --warmup_steps=120
```

On this machine we thus have a batch size of 32, please increase `gradient_accumulation_steps` to reach the same batch size if you have a smaller machine.
These hyper-parameters give evaluation results pearsonr of `0.918`.

#### Fine-tuning Bert model on the MRPC classification task

This example code fine-tunes the Bert Whole Word Masking model on the Microsoft Research Paraphrase Corpus (MRPC) corpus using distributed training on 8 V100 GPUs to reach a F1 > 92.

```bash
python -m torch.distributed.launch --nproc_per_node 8 run_bert_classifier.py   \
    --model_type bert \
    --model_name_or_path bert-large-uncased-whole-word-masking \
    --task_name MRPC \
    --do_train   \
    --do_eval   \
    --do_lower_case   \
    --data_dir $GLUE_DIR/MRPC/   \
    --max_seq_length 128   \
    --per_gpu_eval_batch_size=8   \
    --per_gpu_train_batch_size=8   \
    --learning_rate 2e-5   \
    --num_train_epochs 3.0  \
    --output_dir /tmp/mrpc_output/ \
    --overwrite_output_dir   \
    --overwrite_cache \
```

Training with these hyper-parameters gave us the following results:

```bash
  acc = 0.8823529411764706
  acc_and_f1 = 0.901702786377709
  eval_loss = 0.3418912578906332
  f1 = 0.9210526315789473
  global_step = 174
  loss = 0.07231863956341798
```

### Fine-tuning for question-answering: SQuAD example

This example code fine-tunes BERT on the SQuAD dataset using distributed training on 8 V100 GPUs and Bert Whole Word Masking uncased model to reach a F1 > 93 on SQuAD:

```bash
python -m torch.distributed.launch --nproc_per_node=8 run_squad.py \
    --model_type bert \
    --model_name_or_path bert-large-uncased-whole-word-masking \
    --do_train \
    --do_predict \
    --do_lower_case \
    --train_file $SQUAD_DIR/train-v1.1.json \
    --predict_file $SQUAD_DIR/dev-v1.1.json \
    --learning_rate 3e-5 \
    --num_train_epochs 2 \
    --max_seq_length 384 \
    --doc_stride 128 \
    --output_dir ../models/wwm_uncased_finetuned_squad/ \
    --per_gpu_eval_batch_size=3   \
    --per_gpu_train_batch_size=3   \
```

Training with these hyper-parameters gave us the following results:

```bash
python $SQUAD_DIR/evaluate-v1.1.py $SQUAD_DIR/dev-v1.1.json ../models/wwm_uncased_finetuned_squad/predictions.json
{"exact_match": 86.91579943235573, "f1": 93.1532499015869}
```

This is the model provided as `bert-large-uncased-whole-word-masking-finetuned-squad`.

### Conditional generation: Text generation with GPT, GPT-2, Transformer-XL and XLNet

A conditional generation script is also included to generate text from a prompt.
The generation script include the [tricks](https://github.com/rusiaaman/XLNet-gen#methodology) proposed by by Aman Rusia to get high quality generation with memory models like Transformer-XL and XLNet (include a predefined text to make short inputs longer).

Here is how to run the script with the small version of OpenAI GPT-2 model:

```shell
python ./examples/run_glue.py \
    --model_type=gpt2 \
    --length=20 \
    --model_name_or_path=gpt2 \
```

## Documentation

The full documentation is available at https://huggingface.co/pytorch-transformers/.

## Citation

At the moment, there is no paper to cite for PyTorch-Transformers but we are working on preparing one.
In the meantime, please include a mention of the library and a link to the present repository if you use this work in a published or open-source project.
