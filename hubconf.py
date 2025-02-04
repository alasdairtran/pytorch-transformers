from hubconfs.bert_hubconf import (bertForMaskedLM, bertForMultipleChoice,
                                   bertForNextSentencePrediction,
                                   bertForPreTraining,
                                   bertForQuestionAnswering,
                                   bertForSequenceClassification,
                                   bertForTokenClassification, bertModel,
                                   bertTokenizer)
from hubconfs.gpt2_hubconf import (gpt2DoubleHeadsModel, gpt2LMHeadModel,
                                   gpt2Model, gpt2Tokenizer)
from hubconfs.gpt_hubconf import (openAIGPTDoubleHeadsModel,
                                  openAIGPTLMHeadModel, openAIGPTModel,
                                  openAIGPTTokenizer)
from hubconfs.transformer_xl_hubconf import (transformerXLLMHeadModel,
                                             transformerXLModel,
                                             transformerXLTokenizer)

dependencies = ['torch', 'tqdm', 'boto3', 'requests', 'regex']
