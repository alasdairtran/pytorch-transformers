# Sync

Changes from the original repo:

```sh
# Rename pytorch_pretrained_bert to transformers.
git grep -l 'pytorch_pretrained_bert' -- ':!sync.md' | xargs sed -i '' -e 's/pytorch_pretrained_bert/transformers/g'
isort **/*.py
autopep8 -i **/*.py
# Update modelling_bert.py to return dicts
```
