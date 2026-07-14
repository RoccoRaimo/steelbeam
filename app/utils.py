def clean_handcalcs_latex(raw_result):
    """
    Function to clean the latex output of handcalcs render
    """
    if not raw_result:
        return ""
    if isinstance(raw_result, tuple):
        latex_str = raw_result[0] if raw_result[0] else ""
    elif isinstance(raw_result, dict):
        latex_str = raw_result.get('latex_code', '')
    else:
        latex_str = str(raw_result)
    if not latex_str.strip():
        return ""

    # Remove only the $$ delimiters
    latex_str = latex_str.replace('$$', '').strip()

    # Fix &= duplicates: keep only the first one per line
    fixed_lines = []
    for line in latex_str.split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = line.split('&=')
        if len(parts) > 1:
            line = parts[0] + '&=' + '='.join(parts[1:])
        fixed_lines.append(line)

    return '\n'.join(fixed_lines)