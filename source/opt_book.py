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
#study = pickle.load(open("optuna_book_study.pkl", "rb"))

def run(command_line):
    args = shlex.split(command_line)
    print(f"{datetime.now()}: {command_line}", flush=True)
    #subprocess.run(args, cwd="/home/hmatsuya/workspace/Shogi/cobra2019b/exe")
    subprocess.run(args, shell=False, cwd="/home/hmatsuya/workspace/Shogi/cobra2019b/exe")
    print(f"{datetime.now()}: Done.", flush=True)

def objective(trial):
    min_num = math.floor(trial.suggest_loguniform('min_num', 2, 100000))
    book_eval_diff = math.floor(trial.suggest_loguniform('book_eval_diff', 0.1, 300))
    book_eval_black_limit = math.floor(trial.suggest_int('book_eval_black_limit', -150, 150))
    book_eval_white_limit = math.floor(trial.suggest_int('book_eval_white_limit', -150, 150))
    consider_book_move_count = trial.suggest_categorical('consider_book_move_count', ['true', 'false'])
    ignore_book_ply = trial.suggest_categorical('ignore_book_ply', ['true', 'false'])

    # save Optuna study
    pickle.dump(study, open("optuna_book_study.pkl", "wb"))

    # Prune book
    print(f"{datetime.now()}: start pruning book.", flush=True)
    temp_book_path = "/home/hmatsuya/workspace/Shogi/cobra2019b/exe/book/user_book3.db"
    #book_path = "/home/hmatsuya/workspace/Shogi/cobra2019b/exe/uct_book_startpos.bin.pruned2"
    book_path = "uct_book_startpos.bin.pruned2"
    if os.path.exists(temp_book_path):
        os.remove(temp_book_path)
    command_line = f"python3 prune_book.py --num {min_num} -o book/user_book3.db {book_path}"
    run(command_line)

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
        "--bookfile2", "user_book3.db",
        "--hash1", "512",
        "--hash2", "512",
        "--eval1", "Kristall",
        "--eval2", f"merged5",
        "--flip_turn", "True",
        "--options", f"BookDepthLimit:0 BookNumLimit:{min_num} BookMoves:256 ResignValue:1200 NarrowBook:false BookEvalDiff:{book_eval_diff} BookEvalBlackLimit:{book_eval_black_limit} BookEvalWhiteLimit:{book_eval_white_limit} ConsiderBookMoveCount:{consider_book_move_count} IgnoreBookPly:{ignore_book_ply}",
        "--early_stopping",
        ])

    return winrate1

# Optimize!
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
