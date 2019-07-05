Sync

Changes from the original repo:

```sh
# Rename pytorch_pretrained_bert to transformers.
git grep -l 'pytorch_pretrained_bert' -- ':!sync.md' | xargs sed -i '' -e 's/pytorch_pretrained_bert/transformers/g'
isort **/*.py
autopep8 **/*.py
# Update modelling.py to return dicts
```
