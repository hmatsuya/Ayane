#!/bin/bash -e

HOME=/home/hmatsuya/workspace/Shogi/test/yane1/exe
#HOME=/home/hmatsuya/workspace/Shogi/cobra2019b/exe
echo HOME: $HOME

if [ $# -eq 0 ] ; then
    EVAL1=$HOME/eval
    EVAL2=$HOME/eval2
elif [ $# -eq 1 ] ; then
    EVAL1=$HOME/eval
    EVAL2=$1
elif [ $# -eq 2 ] ; then
    EVAL1=$1
    EVAL2=$2
else
    echo "ERROR: too many arguments."
    exit 1
fi

echo EVAL1: $EVAL1
echo EVAL2: $EVAL2

#rm $HOME/evallink1
#rm $HOME/evallink2

#ln -s $EVAL1 $HOME/evallink1
#ln -s $EVAL2 $HOME/evallink2

python3 ayaneru-colosseum.py \
	--time "byoyomi 2000" \
    --home $HOME \
	--engine1 YaneuraOu-by-gcc \
	--engine2 YaneuraOu-by-gcc \
    --bookdir1 book \
    --bookdir2 book \
    --bookfile1 no_book \
    --bookfile2 no_book \
	--hash1 512 \
	--hash2 512 \
	--loop 3000 \
	--cores 6 \
	--thread1 1 \
	--thread2 1 \
    --flip_turn True \
    --book_file book/records_2017-05-19.sfen \
    --start_gameply 24 \
    --eval1 $EVAL1 \
    --eval2 $EVAL2
	# --eval1 ../../Kristallweizen/eval \
	# --eval2 merged5 \
    #--start_gameply 0 \
    #--option BookMoves:128 ConsiderBookMoveCount:false

