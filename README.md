Run on golem network:
1. `docker build -t gollm .`
2. `pip install gvmkit-build`
3. `gvmkit-build gollm --push --nologin`
4. `export GOLLM_IMAGE_HASH=`
5. `dapp-runner start --config golem_config.yaml build.yaml`
