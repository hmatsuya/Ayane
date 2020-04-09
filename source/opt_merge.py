#!/home/hmatsuya/anaconda/envs/py3/bin/python3
import sys
import optuna
import shlex, subprocess
from datetime import datetime
import os
import argparse
import math
import pickle

exec(open('/home/hmatsuya/workspace/Shogi/Ayane/source/ayaneru-colosseum.py').read())

study = optuna.create_study()
#study = pickle.load(open("optuna_study.pkl", "rb"))

def run(command_line):
    args = shlex.split(command_line)
    print(f"{datetime.now()}: {command_line}", flush=True)
    #subprocess.run(args, cwd="/home/hmatsuya/workspace/Shogi/cobra2019b/exe")
    subprocess.run(args, shell=False, cwd="/home/hmatsuya/workspace/Shogi/cobra2019b/exe")
    print(f"{datetime.now()}: Done.", flush=True)

def objective(trial):
    percentage1 = trial.suggest_int('percentage1', 0, 100)
    percentage2 = trial.suggest_int('percentage2', 0, 100)
    percentage3 = trial.suggest_int('percentage3', 0, 100)

    # merge
    print(f"{datetime.now()}: start training.", flush=True)
    command_line = f"./YaneuraOu-by-gcc.evalmerge.bak test nnue evalmerge eval /home/hmatsuya/workspace/Shogi/tanuki-2019/eval merged1 {percentage1} , quit"
    run(command_line)

    # Kristallweizen
    command_line = f"./YaneuraOu-by-gcc.evalmerge.bak test nnue evalmerge /home/hmatsuya/workspace/Shogi/Kristallweizen/eval /home/hmatsuya/workspace/Shogi/Kristallweizen/kai04/eval merged2 {percentage2} , quit"
    run(command_line)

    # last merge
    command_line = f"./YaneuraOu-by-gcc.evalmerge.bak test nnue evalmerge merged1 merged2 merged3 {percentage3} , quit"
    run(command_line)

    # save
    pickle.dump(study, open("optuna_study.pkl", "wb"))

    # test
    print(f"{datetime.now()}: start testing.", flush=True)
    winrate1 = AyaneruColosseum([
        "--time", "byoyomi 130",
        "--home", "/home/hmatsuya/workspace/Shogi/cobra2019b/exe",
        "--engine1", "YaneuraOu-by-gcc.default_arch",
        "--engine2", f"YaneuraOu-by-gcc.default_arch",
        "--loop", "1000",
        "--cores", "6",
        "--thread1", "1",
        "--thread2", "1",
        "--bookfile1", "no_book",
        "--bookfile2", "no_book",
        "--hash1", "512",
        "--hash2", "512",
        "--eval1", "Kristall",
        "--eval2", f"merged3",
        "--flip_turn", "True",
        "--book_file", "book/records_2017-05-19.sfen",
        "--start_gameply", "24",
        "--early_stopping",
        ])

    return winrate1

study.optimize(objective, n_trials=50)

print()
print(study.best_params)
print()
print(study.best_value)
print()
print(study.best_trial)
print()
print(study.trials)
print()

pickle.dump(study, open("optuna_study.pkl", "wb"))
