#!/bin/sh
for dir in ~/projects/graphs/auto-graphs/generated_graphs/*;
  do 
     [ -d "$dir" ] && cd "$dir" && echo "Entering into $dir and installing packages" && npm install && graph auth --product hosted-service <access-key> && npm run codegen  && npm run deploy
  done;