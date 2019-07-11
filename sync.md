# Sync

Changes from the original repo:

```sh
# Rename pytorch_transformers to transformers.
git grep -l 'pytorch_transformers' -- ':!sync.md' | xargs sed -i '' -e 's/pytorch_transformers/transformers/g'
isort **/*.py
autopep8 -i **/*.py
# Update modelling_bert.py to return dicts
```
