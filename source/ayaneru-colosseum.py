# あやねるコロシアム
# マルチあやねるサーバーを用いてエンジンの1対1対局を行うスクリプト

# === 本スクリプトの引数の意味 ===

# --engine1 , --engine2
# エンジンの実行ファイル名

# --home
# エンジンなどが存在するホームディレクトリ

# --hash1 , --hash2
# player1のHashのサイズ , player2のHashのサイズ

# --time
# 持ち時間設定(AyaneruServer.set_time_setting()の引数と同じ)
# time = 先後の持ち時間[ms]
# time1p = 1p側 持ち時間[ms](1p側だけ個別に設定したいとき)
# time2p = 2p側 持ち時間[ms](2p側だけ個別に設定したいとき)
# byoyomi = 秒読み[ms]
# byoyomi1p = 1p側秒読み[ms]
# byoyomi2p = 2p側秒読み[ms]
# inc = 1手ごとの加算[ms]
# inc1p = 1p側のinc[ms]
# inc2p = 2p側のinc[ms]
#
# 例 : --time "byoyomi 100" : 1手0.1秒
# 例 : --time "time 900000" : 15分
# 例 : --time "time1p 900000 time2p 900000 byoyomi 5000" : 15分 + 秒読み5秒
# 例 : --time "time1p 10000 time2p 10000 inc 5000" : 10秒 + 1手ごとに5秒加算
# 例 : --time "time1p 10000 time2p 10000 inc1p 5000 inc2p 1000" : 10秒 + 先手1手ごとに5秒、後手1手ごとに1秒加算

# --loop
# 対局回数

# --cores
# CPUのコア数

# --thread1 , thread2
# エンジン1P側のスレッド数、エンジン2P側のスレッド数

# --eval1 , eval2
# エンジン1P側のevalフォルダ、エンジン2P側のevalフォルダ

# --flip_turn
# 1局ごとに先後入れ替えるのか(デフォルト:True)

# --book_file
# 定跡ファイル("startpos moves ..."や"sfen ... moves ..."のような書式で書かれているものとする)

# --start_gameply
# 定跡ファイルの開始手数。0を指定すると末尾の局面から開始。1を指定すると初期局面。

import os
import time
import argparse
import shogi.Ayane as ayane
import sys


def AyaneruColosseum(arglist):
    # --- コマンドラインのparseここから ---

    parser = argparse.ArgumentParser("ayaneru-colosseum.py")

    # 持ち時間設定。デフォルト1秒
    parser.add_argument(
        "--time",
        type=str,
        default="byoyomi 100",
        help="持ち時間設定 AyaneruServer.set_time_setting()の引数と同じ。",
    )

    # home folder
    parser.add_argument("--home", type=str, default="", help="hole folder")

    # engine path
    parser.add_argument(
        "--engine1", type=str, default="exe/YaneuraOu.exe", help="engine1 path"
    )
    parser.add_argument(
        "--engine2", type=str, default="exe/YaneuraOu.exe", help="engine2 path"
    )

    # Hashサイズ。デフォルト64MB
    parser.add_argument("--hash1", type=int, default=128, help="engine1 hashsize[MB]")
    parser.add_argument("--hash2", type=int, default=128, help="engine2 hashsize[MB]")

    # 対局回数
    parser.add_argument("--loop", type=int, default=100, help="number of games")

    # CPUコア数
    parser.add_argument(
        "--cores", type=int, default=8, help="cpu cores(number of logical thread)"
    )

    # エンジンに割り当てるスレッド数
    parser.add_argument(
        "--thread1", type=int, default=2, help="number of engine1 thread"
    )
    parser.add_argument(
        "--thread2", type=int, default=2, help="number of engine2 thread"
    )

    # engine folder
    parser.add_argument("--eval1", type=str, default="eval", help="engine1 eval")
    parser.add_argument("--eval2", type=str, default="eval", help="engine2 eval2")

    # flip_turn
    parser.add_argument(
        "--flip_turn", type=bool, default=True, help="flip turn every game"
    )

    # book_file
    parser.add_argument("--book_file", type=str, default=None, help="book filepath")

    # start_gameply
    parser.add_argument(
        "--start_gameply", type=int, default=24, help="start game ply in the book"
    )

    # BookDir
    parser.add_argument("--bookdir1", type=str, default="book", help="book directory for engine1")
    parser.add_argument("--bookdir2", type=str, default="book", help="book directory for engine2")

    # BookFile
    parser.add_argument("--bookfile1", type=str, default="no_book",
            help="book file name for engine1")
    parser.add_argument("--bookfile2", type=str, default="no_book",
            help="book file name for engine2")

    # Arbitrary options
    parser.add_argument("--options", "-o", type=str, default=None,
            help="set arbitrary options as name:value for both engines")
    parser.add_argument("--options1", "-o1", type=str, default=None,
            help="set arbitrary options as name:value for the 1st engine")
    parser.add_argument("--options2", "-o2", type=str, default=None,
            help="set arbitrary options as name:value for the 2nd engine")

    # Early stopping
    parser.add_argument("--early_stopping", action="store_true")

    args = parser.parse_args(arglist)

    # --- コマンドラインのparseここまで ---

    print("home           : {0}".format(args.home), flush=True)
    print("engine1        : {0}".format(args.engine1), flush=True)
    print("engine2        : {0}".format(args.engine2), flush=True)
    print("eval1          : {0}".format(args.eval1), flush=True)
    print("eval2          : {0}".format(args.eval2), flush=True)
    print("hash1          : {0}".format(args.hash1), flush=True)
    print("hash2          : {0}".format(args.hash2), flush=True)
    print("loop           : {0}".format(args.loop), flush=True)
    print("cores          : {0}".format(args.cores), flush=True)
    print("time           : {0}".format(args.time), flush=True)
    print("flip_turn      : {0}".format(args.flip_turn), flush=True)
    print("book file      : {0}".format(args.book_file), flush=True)
    print("start_gameply  : {0}".format(args.start_gameply), flush=True)
    print("bookdir1       : {0}".format(args.bookdir1), flush=True)
    print("bookdir2       : {0}".format(args.bookdir2), flush=True)
    print("bookfile1      : {0}".format(args.bookfile1), flush=True)
    print("bookfile2      : {0}".format(args.bookfile2), flush=True)
    print("options        : {0}".format(args.options), flush=True)
    print("options1       : {0}".format(args.options1), flush=True)
    print("options2       : {0}".format(args.options2), flush=True)
    print("early_stopping : {0}".format(args.early_stopping), flush=True)

    # directory

    home = args.home
    engine1 = os.path.join(home, args.engine1)
    engine2 = os.path.join(home, args.engine2)
    eval1 = os.path.join(home, args.eval1)
    eval2 = os.path.join(home, args.eval2)
    bookdir1 = os.path.join(home, args.bookdir1)
    bookdir2 = os.path.join(home, args.bookdir2)

    # マルチあやねるサーバーをそのまま用いる
    server = ayane.MultiAyaneruServer()

    # 1対局に要するスレッド数
    # (先後、同時に思考しないので大きいほう)
    thread_total = max(args.thread1, args.thread2)
    # 何並列で対局するのか？ 2スレほど余らせておかないとtimeupになるかもしれん。
    # メモリが足りるかは知らん。メモリ足りないとこれまたメモリスワップでtimeupになる。
    cores = max(args.cores - 2, 1)
    game_server_num = int(cores / thread_total)

    # エンジンとのやりとりを標準出力に出力する
    # server.debug_print = True

    # あやねるサーバーを起動
    server.init_server(game_server_num)

    # エンジンオプション
    options_common = {
        "NetworkDelay": "0",
        "NetworkDelay2": "0",
        "MaxMovesToDraw": "320",
        "MinimumThinkingTime": "0",
        #"BookFile": "no_book"
    }

    # command line options
    def split_opt(arg):
        argopt = {}
        if arg:
            for item in args.options.split(" "):
                name, value = item.split(":")
                argopt.update({name:value})
        return argopt
    #argopt = {}
    #if args.options:
    #    for item in args.options.split(" "):
    #        name, value = item.split(":")
    #        argopt.update({name: value})

    argopt = split_opt(args.options)
    argopt1 = split_opt(args.options1)
    argopt2 = split_opt(args.options2)
    print(f"argopt: {argopt}")
    print(f"argopt1: {argopt1}")
    print(f"argopt2: {argopt2}")

    options1p = {"Hash": str(args.hash1), "Threads": str(args.thread1), "EvalDir": eval1,
            "BookDir": bookdir1, "BookFile": args.bookfile1}
    options2p = {"Hash": str(args.hash2), "Threads": str(args.thread2), "EvalDir": eval2,
            "BookDir": bookdir2, "BookFile": args.bookfile2}

    # 1P,2P側のエンジンそれぞれを設定して初期化する。
    server.init_engine(0, engine1, {**options_common, **options1p, **argopt, **argopt1})
    server.init_engine(1, engine2, {**options_common, **options2p, **argopt, **argopt2})

    # 持ち時間設定。
    server.set_time_setting(args.time)

    # flip_turnを反映させる
    server.flip_turn_every_game = args.flip_turn

    # 定跡

    # テスト用の定跡ファイル
    # args.book_file = "book/records2016_10818.sfen"
    if args.book_file is None:
        start_sfens = ["startpos"]
    else:
        book_filepath = os.path.join(home, args.book_file)
        with open(book_filepath) as f:
            start_sfens = f.readlines()
    server.start_sfens = start_sfens
    server.start_gameply = args.start_gameply

    # 対局スレッド数、秒読み設定などを短縮文字列化する。
    if args.thread1 == args.thread2:
        game_setting_str = "t{0}".format(args.thread1)
    else:
        game_setting_str = "t{0},{1}".format(args.thread1, args.thread2)
    game_setting_str += (
        args.time.replace("byoyomi", "b")
        .replace("time", "t")
        .replace("inc", "i")
        .replace(" ", "")
    )

    # これで対局が開始する
    server.game_start()

    # loop回数試合終了するのを待つ
    last_total_games = 0
    loop = args.loop

    # ゲーム数が増えていたら、途中結果を出力する。
    def output_info():
        nonlocal last_total_games, server
        if last_total_games != server.total_games:
            last_total_games = server.total_games
            print(game_setting_str + "." + server.game_info(), flush=True)

    def early_stopping():
        nonlocal last_total_games, server, args, loop
        if args.early_stopping and (server.total_games > (loop/10)) and (server.game_rating().rating_lowerbound > 0):
            return True
        return False

    while server.total_games < loop and not early_stopping():
        output_info()
        time.sleep(1)
    output_info()

    server.game_stop()

    # 対局棋譜の出力
    # for kifu in server.game_kifus:
    #     print("game sfen = {0} , flip_turn = {1} , game_result = {2}".format(kifu.sfen , kifu.flip_turn , str(kifu.game_result)))

    server.terminate()

    return server.game_rating().win_rate


if __name__ == "__main__":
    print(__name__, flush=True)
    AyaneruColosseum(sys.argv[1:])
