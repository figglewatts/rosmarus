def make_path_safe(string: str) -> str:
    keepcharacters = (' ', '.', '_')
    return "".join(c for c in string
                   if c.isalnum() or c in keepcharacters).rstrip().replace(
                       " ", "_")
