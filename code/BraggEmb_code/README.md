# BraggEmb

run with `python main.py -ih5 /home/wzheng/EventDetection/rareEventHEDM_v1/baseline_datasets/park_ss_ff_0MPa_000315.edf.h5`

model weights will be check-pointed for each epoch.

Output is an embedding model. 

Based on Bootstrap your own latent (BYOL):
```
@misc{https://doi.org/10.48550/arxiv.2006.07733,
  doi = {10.48550/ARXIV.2006.07733},
  url = {https://arxiv.org/abs/2006.07733},
  author = {Grill, Jean-Bastien and Strub, Florian and Altché, Florent and Tallec, Corentin and Richemond, Pierre H. and Buchatskaya, Elena and Doersch, Carl and Pires, Bernardo Avila and Guo, Zhaohan Daniel and Azar, Mohammad Gheshlaghi and Piot, Bilal and Kavukcuoglu, Koray and Munos, Rémi and Valko, Michal},
  title = {Bootstrap your own latent: A new approach to self-supervised Learning},
  publisher = {arXiv},
  year = {2020},
}
```
