# Dataset cards

A dataset card records where a dataset comes from, its terms of use, how RadAssist uses it,
and its known problems. Read the card before training on or evaluating with a dataset.

| Dataset | Task in RadAssist | Card |
|---|---|---|
| NIH ChestX-ray14 | Pleural effusion vs. not (chest) | [nih-chestxray14.md](nih-chestxray14.md) |
| MURA v1.1 | Abnormal vs. normal study (upper extremity) | [mura.md](mura.md) |

Raw data, labels and manifests are **never committed** to this repository.
Recreate them with the commands in [`ml/README.md`](../../ml/README.md).
