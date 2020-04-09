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

#study = optuna.create_study()
study = pickle.load(open("optuna_study.pkl", "rb"))

def run(command_line):
    args = shlex.split(command_line)
    print(f"{datetime.now()}: {command_line}", flush=True)
    #subprocess.run(args, cwd="/home/hmatsuya/workspace/Shogi/cobra2019b/exe")
    subprocess.run(args, shell=False, cwd="/home/hmatsuya/workspace/Shogi/cobra2019b/exe")
    print(f"{datetime.now()}: Done.", flush=True)

def objective(trial):
    #arch = trial.suggest_categorical('arch', ['default_arch', 'deepest', 'shallow', 'shallower'])
    arch = trial.suggest_categorical('arch', ['shallow', 'shallower'])
    if arch == 'default_arch':
        skip_loading_network = trial.suggest_categorical('skip_loading_netowrk', ['true', 'false'])
    else:
        skip_loading_network = 'true'

    eta  = trial.suggest_loguniform('eta', 1e-1, 10.0)
    #eta  = 1.0
    eval_weight = trial.suggest_uniform('eval_weight', 0.0, 1.0)
    #loop = trial.suggest_int('loop', 1, 2)
    loop = 1
    nn_batch_size = trial.suggest_int('nn_batch_size', 100, 10000)
    init = trial.suggest_categorical('initialize network', ['true', 'false'])
    freeze_transformer = \
        trial.suggest_categorical('freeze feature transformer', ['true', 'false'])
    eval_limit = math.floor(trial.suggest_loguniform('eval_limit', 1000, 32000))
    mirror_percentage = trial.suggest_int('mirror_percentage', 0, 50)

    sfen_file = " ".join([f"/home/hmatsuya/workspace/Shogi/data/sfens/generated_sfens.bin.{i}" for i in range(20, 21)])

    # train
    print(f"{datetime.now()}: start training.", flush=True)
    command_line = f"./YaneuraOu-by-gcc.{arch} InitializeEval true , FreezeFeatureTransformer {freeze_transformer} , SkipLoadingNetworkEval {skip_loading_network} , threads 12 , hash 16 , evaldir merged5 , evalsavedir new_eval.{trial.number} , learn save_only_once batchsize 1000000 nn_batch_size {nn_batch_size} eta {eta} lambda {eval_weight} eval_limit {eval_limit} loop {loop} mirror_percentage {mirror_percentage} {sfen_file} , quit"
    run(command_line)

    # test
    print(f"{datetime.now()}: start testing.", flush=True)
    winrate1 = AyaneruColosseum([
        "--time", "inc 300",
        "--home", "/home/hmatsuya/workspace/Shogi/cobra2019b/exe",
        "--engine1", "YaneuraOu-by-gcc.default_arch",
        "--engine2", f"YaneuraOu-by-gcc.{arch}",
        "--loop", "200",
        "--cores", "6",
        "--thread1", "1",
        "--thread2", "1",
        "--bookfile1", "no_book",
        "--bookfile2", "no_book",
        "--hash1", "512",
        "--hash2", "512",
        "--eval1", "merged5",
        "--eval2", f"new_eval.{trial.number}",
        "--flip_turn", "True",
        "--book_file", "book/records_2017-05-19.sfen",
        "--start_gameply", "24",
        ])

    pickle.dump(study, open("optuna_study.pkl", "wb"))
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
