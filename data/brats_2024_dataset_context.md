# BraTS 2024 Dataset Context

Source page: https://www.synapse.org/Synapse:syn53708249/wiki/627759

Extracted at: 2026-05-13T08:29:37Z

## Dataset

- Name: BraTS 2024 Challenge
- Synapse project ID: syn53708249
- Synapse alias: brats2024
- Data folder ID: syn64952546
- Data folder URL: https://www.synapse.org/Synapse:syn64952546
- Wiki page: Data Access/Download, wiki ID 627759
- Wiki last modified: 2026-04-28T18:57:15.940Z

## Access And Use

The data is available to registered Synapse users after they accept the post-challenge terms and conditions. Downloads are accessed from the Synapse Data folder with the Request Access flow.

The dataset is under CC-BY-NC 4.0, so use is limited to non-commercial purposes. Publications must cite the flagship BraTS challenge manuscript and the relevant challenge-specific manuscripts. The required attribution identifies the Brain Tumor Segmentation (BraTS) Challenge project and Synapse ID syn53708249.

Accepting the terms and downloading data can allow Sage Bionetworks to share download activity and Synapse profile information with the challenge organizers for dataset-related purposes.

## Collections

| Collection | Synapse ID | Files | Size |
| --- | --- | ---: | ---: |
| BraTS-GLI | syn59059776 | 5 | 44.80 GiB |
| BraTS-GoAT | syn68156890 | 2 | 16.46 KiB |
| BraTS-MEN-RT | syn59059779 | 5 | 12.08 GiB |
| BraTS-MET | syn68156869 | 2 | 2.11 KiB |
| BraTS-PED | syn68156871 | 2 | 1.85 KiB |
| BraTS-Path | syn59761935 | 2 | 867 B |
| BraTS-SSA | syn59059780 | 2 | 867 B |
| MLCube Resources | syn61956466 | 4 | 117.08 MiB |

Total listed files: 24

Total listed size: 56.99 GiB

## Local Dataset Match

Local root: `/Volumes/External M2/Datos/TFM-datasets`

Matched at: 2026-05-13T10:03:30Z

Ignored local folder: `_comprimidos`

| Synapse file | Local match | Cases | NIfTI files | Status |
| --- | --- | ---: | ---: | --- |
| BraTS2024-BraTS-GLI-TrainingData.zip | training_data1_v2 | 1350 | 6750 | extracted |
| BraTS2024-BraTS-GLI-AdditionalTrainingData.zip | training_data_additional | 271 | 1355 | extracted |
| BraTS2024-BraTS-GLI-ValidationData.zip | validation_data | 188 | 752 | extracted |
| BraTS2024-MEN-RT-TrainingData.zip | BraTS-MEN-RT-Train-v2 | 500 | 1000 | extracted |
| BraTS2024-MEN-RT-ValidationData.zip | BraTS-MEN-RT-Val-v1 | 70 | 70 | extracted |
| Small Synapse files and MLCube resources | TMF-dataset-small-files | n/a | n/a | MD5 matched |

The five extracted imaging datasets have complete per-case file counts for their expected modalities:

- BraTS-GLI train/additional: seg, t1c, t1n, t2f, t2w.
- BraTS-GLI validation: t1c, t1n, t2f, t2w.
- BraTS-MEN-RT train: gtv, t1c.
- BraTS-MEN-RT validation: t1c.

Detailed row-level matches are stored in `data/brats_2024_local_dataset_match.csv`.

## Citation Scopes

- Any dataset and/or MedPerf client: MedPerf paper in Nature Machine Intelligence, DOI https://doi.org/10.1038/s42256-023-00652-2
- BraTS-GLI (2024): arXiv https://arxiv.org/abs/2405.18368, DOI https://doi.org/10.48550/arXiv.2405.18368
- BraTS-Local-Inpainting: arXiv https://arxiv.org/abs/2305.08992, DOI https://doi.org/10.48550/arXiv.2305.08992, plus BraTS-GLI 2023 manuscripts
- BraTS-MEN-RT: arXiv https://arxiv.org/abs/2405.18383
- BraTS-MET: 2023 arXiv https://arxiv.org/abs/2306.00838 and DOI https://doi.org/10.48550/arXiv.2306.00838; 2024 citation marked as coming soon in the source wiki
- BraTS-MRI-Synthesis: arXiv https://arxiv.org/abs/2305.09011, DOI https://doi.org/10.48550/arXiv.2305.09011, plus BraTS-GLI 2023 manuscripts
- BraTS-Path: arXiv https://arxiv.org/abs/2405.10871
- BraTS-PED: 2023 arXiv https://arxiv.org/abs/2305.17033 and DOI https://doi.org/10.48550/arXiv.2305.17033; 2024 arXiv https://arxiv.org/abs/2404.15009 and DOI https://doi.org/10.48550/arXiv.2404.15009
- BraTS-SSA: arXiv https://arxiv.org/abs/2305.19369, DOI https://doi.org/10.48550/arXiv.2305.19369

## Notes

Per-file sizes were not exposed through unauthenticated file-handle endpoints. The collection sizes above come from Synapse entity children metadata.

Local download matching did not inspect `_comprimidos`. The local `TMF-dataset-small-files/manifest.csv` was used only to verify IDs, file sizes, and MD5 hashes for the small Synapse files already present outside `_comprimidos`.
