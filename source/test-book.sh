#!/bin/bash

home=/home/hmatsuya/workspace/Shogi/test/yane1/exe

mkdir $home/book/test
rm $home/book/test/user_book1.db
rm $home/book/test/user_book2.db

ln -s /home/hmatsuya/workspace/Shogi/cobra2019b/exe/700T-shock-book.db $home/book/test/user_book1.db
ln -s /home/hmatsuya/workspace/Shogi/cobra2019b/exe/cobra_shock.db $home/book/test/user_book2.db

python3 ayaneru-colosseum.py \
	--time "inc 300" \
    --home $home \
	--engine1 YaneuraOu-by-gcc \
	--engine2 YaneuraOu-by-gcc \
    --bookdir1 book/test \
    --bookdir2 book/test \
    --bookfile1 user_book1.db \
    --bookfile2 user_book2.db \
	--hash1 512 \
	--hash2 512 \
	--loop 300 \
	--cores 8 \
	--thread1 1 \
	--thread2 1 \
	--eval1 eval2 \
	--eval2 eval2 \
    --flip_turn True \
    --start_gameply 1 \
    --options "BookMoves:256 BookEvalDiff:60 BookEvalBlackLimit:0 BookEvalWhiteLimit:-120 ResignValue:1800 BookDepthLimit:2 ConsiderBookMoveCount:true"
    #--options "NarrowBook:true ResignValue:3000 BookDepthLimit:0"
    #--option BookMoves:256 BookEvalBlackLimit:0 BookEvalWhiteLimit:-150 BookEvalDiff:300

