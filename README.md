# graph-validator-generator
Automated python script and helper bash scripts to auto generate subgraphs for all validators on near-staking given a template subgraph

Required: 
- Python
- Template of completed subgraph for 1 validator in working directory
- Google chrome (chrome driver should automatically install.)
- Selenium

To Run: 
- Change the access-key in deploy.sh to your graph hosted service access key
- Change path-to in deploy.sh to the path from home to the path of the gnerated graphs directory
- Run make.py

Developed for Vital Point AI in aid of subgraph directory development
