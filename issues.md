\# Open Issues — anyone can pick these up



| # | Bug | File | Fix |

|---|-----|------|-----|

| 1 | `assume\_role()` has no test | `utils/session\_manager.py` | Add a moto-mocked test, same pattern as `test\_session.py` |

| 2 | Test runs itself twice | `tests/test\_session.py` | Delete the `test\_session()` call at the very bottom of the file |

| 3 | Files saved with BOM encoding, causes garbled text | `.gitignore`, possibly others | Re-save in UTF-8 (not "UTF-8 with BOM") |

| 4 | Throwaway test file is in the real repo | `scratch\_baseline.py` | Delete it, or move to a `scratch/` folder and gitignore it |



\## Closed

\- \~\~`scan` command not using the concurrency engine\~\~ — fixed, wired into `main.py`

