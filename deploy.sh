#!/bin/sh
for dir in ~/projects/graphs/auto-graphs/generated_graphs/*;
  do 
     [ -d "$dir" ] && cd "$dir" && echo "Entering into $dir and installing packages" && npm install && graph auth --product hosted-service 3de36d739e2a4660b486d3f0eda7ed7e && npm run codegen  && npm run deploy
  done;