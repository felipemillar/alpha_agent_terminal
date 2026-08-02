import os
import re

target_file = "/Users/fmillar/Proyectos_Desarrollo/alpha_agent_terminal/src/generate_analysis.py"
with open(target_file, "r") as f:
    content = f.read()

# Replace scipy imports and kurt/skew
content = content.replace("from scipy.stats import kurtosis, skew", "")

content = content.replace("    kurt = kurtosis(clean_returns) if len(clean_returns) > 10 else 0", "    kurt = clean_returns.kurt() if len(clean_returns) > 10 else 0")
content = content.replace("    skw = skew(clean_returns) if len(clean_returns) > 10 else 0", "    skw = clean_returns.skew() if len(clean_returns) > 10 else 0")

with open(target_file, "w") as f:
    f.write(content)
