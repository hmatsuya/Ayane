#!/home/hmatsuya/anaconda/envs/py3/bin/python3
import sys
import optuna
import shlex
import subprocess
from datetime import datetime
import os
import argparse
import math
import pickle
from pathlib import Path

# exec(open('/home/hmatsuya/workspace/Shogi/Ayane/source/ayaneru-colosseum.py').read())
from ayaneru_colosseum import AyaneruColosseum

#  study = optuna.create_study()
study = pickle.load(open("optuna_study.pkl", "rb"))


def run(command_line):
    args = shlex.split(command_line)
    print(f"{datetime.now()}: {command_line}", flush=True)
    # subprocess.run(args, cwd="/home/hmatsuya/workspace/Shogi/cobra2019b/exe")
    subprocess.run(args, shell=False,
                   cwd="/home/hmatsuya/workspace/Shogi/gensfen/exe")
    print(f"{datetime.now()}: Done.", flush=True)


def objective(trial):
    # arch = trial.suggest_categorical('arch', ['default_arch', 'deepest', 'shallow', 'shallower'])

    # skip_loading_network = trial.suggest_categorical(
    #     'skip_loading_netowrk', ['true', 'false'])
    skip_loading_network = "True"

    eta = trial.suggest_loguniform('eta', 1e-1, 1.0)
    # eta1 = 0.5
    # eta1_epoch = trial.suggest_int('eta1_epoch', 1, 1000, log=False)
    # eta2 = trial.suggest_loguniform('eta2', 1e-1, 0.5)
    # eta  = 1.0

    eval_weight = trial.suggest_uniform('eval_weight', 0.33, 1.0)
    # eval_weight = 0.74

    loop = trial.suggest_int('loop', 15, 100)

    # nn_batch_size = trial.suggest_int('nn_batch_size', 100, 10000)
    nn_batch_size = 1700

    # freeze_transformer = \
    #     trial.suggest_categorical(
    #         'freeze feature transformer', ['true', 'false'])
    freeze_transformer = "True"

    # initialize_eval = \
    # trial.suggest_categorical(
    # 'initialize_eval', ['true', 'false'])
    initialize_eval = "True"

    # eval_limit = math.floor(
    # trial.suggest_loguniform('eval_limit', 1000, 32000))
    eval_limit = 6000

    # mirror_percentage = trial.suggest_int('mirror_percentage', 0, 50)
    mirror_percentage = 46

    # base_eval = "/home/hmatsuya/workspace/Shogi/cobra2019b/exe/merged.20200908",
    base_evals = [
        "/home/hmatsuya/workspace/Shogi/cobra2019b/exe/merged.20200905",
        "/home/hmatsuya/workspace/Shogi/tanuki-2019/eval",
        # "/home/hmatsuya/workspace/Shogi/suisho2_200504/eval",
    ]
    base_eval = trial.suggest_categorical('base_eval', base_evals)

    reduction_gameply = trial.suggest_int('reduction_gameply', 24, 128)

    # sfen_file = " ".join(
    #     [f"/home/hmatsuya/workspace/Shogi/data/sfens/generated_sfens.bin.{i}" for i in range(20, 21)])
    # should be absolute path
    # target_dir = "/home/hmatsuya/workspace/Shogi/gensfen/exe/depth12"
    target_dir = "/home/hmatsuya/workspace/Shogi/gensfen/exe/depth18"
    sfen_file = "teacher_*"

    # Original eval dir
    # eval_dir = "/home/hmatsuya/workspace/Shogi/tanuki-2019/eval"

    # train
    print(f"{datetime.now()}: start training.", flush=True)
    command_line = f"./cobra InitializeEval {initialize_eval} , FreezeFeatureTransformer {freeze_transformer} , SkipLoadingNetworkEval {skip_loading_network} , threads 12 , USI_hash 16 , EvalDir {base_eval} , EvalSaveDir new_eval.{trial.number} , learn save_only_once batchsize 100000 nn_batch_size {nn_batch_size} eta {eta} lambda {eval_weight} reduction_gameply {reduction_gameply} eval_limit {eval_limit} loop {loop} mirror_percentage {mirror_percentage} {' '.join([target_dir + '/' + p.name for p in Path(target_dir).glob(sfen_file)])} , quit"
    run(command_line)

    # test
    print(f"{datetime.now()}: start testing.", flush=True)
    winrate1 = AyaneruColosseum([
        "--time", "inc 300",
        "--home", "/home/hmatsuya/workspace/Shogi/gensfen/exe",
        "--engine1", "YaneuraOu-by-gcc",
        "--engine2", "YaneuraOu-by-gcc",
        "--loop", "100",
        "--cores", "6",
        "--thread1", "1",
        "--thread2", "1",
        "--bookfile1", "no_book",
        "--bookfile2", "no_book",
        "--hash1", "1024",
        "--hash2", "1024",
        "--eval1", "eval",
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
