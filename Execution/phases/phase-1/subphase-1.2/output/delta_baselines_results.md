# Delta baselines smoke-test results

- Subsample: 100000 cells × 2000 genes
- Train/test split: sample-stratified, test_fraction=0.2
- train=72810  test=27190
- Top-k DEGs: 20   alpha=0.05   n_perm=100
- Harness metric-gaming check: PASS (random baseline failed WMSE gate as expected)

## Per-baseline results

| baseline | wmse | wmse_p | wmse_z | spearman_topk | gate | ece | seconds | n_pass_topk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear | 0.135346 | 0.0 | 890.929 | 0.4603 | PASS | 0.017111 | 1.88 | 27190 |
| mean | 0.150362 | 0.0 | 809.524 | 0.3041 | PASS | 0.016658 | 0.48 | 27190 |
| pca | 0.135938 | 0.0 | 887.724 | 0.4477 | PASS | 0.017427 | 7.23 | 27190 |
| random | 0.301354 | 1.0 | -9.075 | N/A | FAIL | 0.332162 | 0.22 | 0 |
| persistence | 0.150812 | 0.0 | 807.083 | 0.296 | PASS | 0.016639 | 0.56 | 27190 |

## Stratified summary (per cell_type — wmse / gate / n)

### linear
- CVCL_0023: wmse=0.0809  gate=PASS  n=865
- CVCL_0028: wmse=0.0588  gate=PASS  n=205
- CVCL_0069: wmse=0.0750  gate=PASS  n=459
- CVCL_0099: wmse=0.0020  gate=PASS  n=251
- CVCL_0131: wmse=0.0924  gate=PASS  n=896
- CVCL_0152: wmse=0.0768  gate=PASS  n=687
- CVCL_0179: wmse=0.0892  gate=PASS  n=470
- CVCL_0218: wmse=0.0570  gate=PASS  n=366
- CVCL_0292: wmse=0.0012  gate=PASS  n=327
- CVCL_0293: wmse=0.1200  gate=PASS  n=788
- ... (38 more)

### mean
- CVCL_0023: wmse=0.0884  gate=PASS  n=865
- CVCL_0028: wmse=0.0724  gate=PASS  n=205
- CVCL_0069: wmse=0.0859  gate=PASS  n=459
- CVCL_0099: wmse=0.0089  gate=FAIL  n=251
- CVCL_0131: wmse=0.1035  gate=PASS  n=896
- CVCL_0152: wmse=0.0887  gate=PASS  n=687
- CVCL_0179: wmse=0.1031  gate=PASS  n=470
- CVCL_0218: wmse=0.0730  gate=PASS  n=366
- CVCL_0292: wmse=0.0115  gate=FAIL  n=327
- CVCL_0293: wmse=0.1349  gate=PASS  n=788
- ... (38 more)

### pca
- CVCL_0023: wmse=0.0811  gate=PASS  n=865
- CVCL_0028: wmse=0.0617  gate=PASS  n=205
- CVCL_0069: wmse=0.0758  gate=PASS  n=459
- CVCL_0099: wmse=0.0075  gate=FAIL  n=251
- CVCL_0131: wmse=0.0925  gate=PASS  n=896
- CVCL_0152: wmse=0.0770  gate=PASS  n=687
- CVCL_0179: wmse=0.0894  gate=PASS  n=470
- CVCL_0218: wmse=0.0586  gate=PASS  n=366
- CVCL_0292: wmse=0.0043  gate=FAIL  n=327
- CVCL_0293: wmse=0.1201  gate=PASS  n=788
- ... (38 more)

### random
- CVCL_0023: wmse=0.2339  gate=FAIL  n=865
- CVCL_0028: wmse=0.2252  gate=FAIL  n=205
- CVCL_0069: wmse=0.2296  gate=FAIL  n=459
- CVCL_0099: wmse=0.1068  gate=FAIL  n=251
- CVCL_0131: wmse=0.2587  gate=FAIL  n=896
- CVCL_0152: wmse=0.2461  gate=FAIL  n=687
- CVCL_0179: wmse=0.2574  gate=FAIL  n=470
- CVCL_0218: wmse=0.2253  gate=FAIL  n=366
- CVCL_0292: wmse=0.1445  gate=FAIL  n=327
- CVCL_0293: wmse=0.2866  gate=FAIL  n=788
- ... (38 more)

### persistence
- CVCL_0023: wmse=0.0887  gate=PASS  n=865
- CVCL_0028: wmse=0.0725  gate=PASS  n=205
- CVCL_0069: wmse=0.0861  gate=PASS  n=459
- CVCL_0099: wmse=0.0089  gate=FAIL  n=251
- CVCL_0131: wmse=0.1039  gate=PASS  n=896
- CVCL_0152: wmse=0.0890  gate=PASS  n=687
- CVCL_0179: wmse=0.1034  gate=PASS  n=470
- CVCL_0218: wmse=0.0732  gate=PASS  n=366
- CVCL_0292: wmse=0.0116  gate=FAIL  n=327
- CVCL_0293: wmse=0.1355  gate=PASS  n=788
- ... (38 more)

## Notes

- Baselines are implemented in `delta/baselines/{linear,mean,pca,random,persistence}.py`.
- Evaluation harness: `delta/eval/{wmse,fdr,calibration,stratified}.py`.
- Features for linear/pca: one-hot (drug, cell_line) concatenated.
- log1p transform applied at load time.
- Random baseline is the IP §12.4 metric-gaming check.