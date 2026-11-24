from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from healthtrend.models import compare_six_models

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--csv',required=True)
    args=parser.parse_args()
    results=compare_six_models(pd.read_csv(Path(args.csv)))
    print(json.dumps([{'model':r.model_name,'metrics':r.metrics,'predictions':r.predictions} for r in results],indent=2))

if __name__=='__main__': main()
