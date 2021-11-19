# this is conic

We want to represent the circle

$$
C = \lbrace (x,y) \mid x^2 + y^2 \leq 1 \rbrace.
$$

We can do an approximation whose accuracy increases with each $K > 0$ in the form of:

$$
\begin{align*}
\alpha_0 \geq |x| \\
\beta_0  \geq |y| \\
\alpha_K \leq 1 \\
\beta_K \leq \tan\left(\frac{\pi}{2^{2K+1}}\right) \alpha_K \\
\end{align*}
$$

(interesting! you would have assumed the things above would link to the things below, but they don't! what's the plot look like if you just do the things above?
oh duh, there's no relation because they're different variables.)


and for $k = 1,\ldots,K$:

$$
\theta_k = \frac{\pi}{2^{k+1}}
$$

$$
\begin{align*}
\alpha_k    =   \cos(\theta_k) \alpha_{k-1} + \sin(\theta_k) \beta_{k-1}  \\
 \beta_k \geq |-\sin(\theta_k) \alpha_{k-1} + \cos(\theta_k) \beta_{k-1}| \\
\end{align*}
$$



