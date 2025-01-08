---
title: "Hello world"
format: docx
editor: visual
bibliography: prj_biblio.bib common_biblio.bib
---

## Funzionalità

- codice inline in R funziona out of the box: `{r} 1 + 1` 

- codice inline python non funziona?
  ```{python}
  res = 1 + 1
  ```
  res è `{python} res`.

- mixing di linguaggi differenti
  ```{python}

  def sum(a, b):
      return a + b
    
  sum(1,2)
  ```

  ```{r}
  su <- function(a, b) a + b
  su(1,2)
  ```

- Citazione: inline [@moher2010consort], in footnote[^fn1], per altro
  vedi
  [qui](https://medium.com/@chriskrycho/academic-markdown-and-citations-fe562ff443df).

- LaTeX full formula: $$ \sum_{i=1}^n x_i $$

- Figura: 
  
  ```{python}
  import numpy as np
  import matplotlib.pyplot as plt
  import pandas as pd
  
  x = np.linspace(0, 6, 600)
  plt.figure(figsize=(4,2.5))
  plt.grid(linestyle='dashed')
  plt.plot(x, np.sin(x))
  plt.xlabel('$x$')
  plt.ylabel('$y=\\sin(x)$')
  plt.savefig('img/plot.png', transparent=True, bbox_inches='tight')
  ```
	
- Tabella (pandas `DataFrame` con pacchetto tabulate installato)
  ```{python}
  df = pd.DataFrame({"x": list("abc"), "y" : [1,2,3]})
  df
  ```


## Todo

- latex formula inline:?




## References


<!-- footnotes -->

[^fn1]: [@walker2011equivnoninf]
