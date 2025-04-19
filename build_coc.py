import re
import textwrap

# Hardcoded header and footer to replace the html ones
heading = r"""
```
  _____        __      ____  ___  _____             __         __
 / ___/__  ___/ /__   / __ \/ _/ / ___/__  ___  ___/ /_ ______/ /_
/ /__/ _ \/ _  / -_) / /_/ / _/ / /__/ _ \/ _ \/ _  / // / __/ __/
\___/\___/\_,_/\__/  \____/_/   \___/\___/_//_/\_,_/\_,_/\__/\__/
```
"""

footing = r"""
## Contributors
=> https://contrib.rocks Made with contrib.rocks
=> https://contrib.rocks/image?repo=allthingslinux/code-of-conduct Contributors
    """

config: dict = { 
    "strip_inline_formatting": True,
    "convert_bullet_point_links": True,
    "format_unicode_tables": True,
    "preformatted_unicode_columns": 80,
}





# Grab the file, then split it into a 2D list for ease of manipulation
coc = open("./code-of-conduct/README.md").read().splitlines(True)

# Find the end of the table of contents and delete everything up to that point
toc_end = coc.index("<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n") + 2
print(f"end of TOC found at line {str(toc_end)}, stripping toc and header")
del coc[0:toc_end]

# Find the beginning of the contributors section and chop it off
contrib_start = coc.index("## Contributors\n")
print(f"Contributor block found at line {str(contrib_start)}, stripping out footing")
del coc[contrib_start:]

# multiline formatters
def format_table(multiline_buffer: list) -> list:
    table = [i[2:-2].split(" | ") for i in multiline_buffer]   # take the buffer and convert the table lines into a 2d list
    table_width: int = config["preformatted_unicode_columns"]
    clean_table = []
    column_width = max(len(column.strip()) for column in table[0])
    for x, y in enumerate(table):               # strips the seperating line 
        if not all( char == '-' for char in y[0]):      # Check if first column of row is all dashes. if it is, it's a seperator row and should be discarded.
            clean0 = y[0].strip() # Generate cleaned version of columns 0 and 1
            clean1 = y[1].strip()
            wrapped_text = textwrap.wrap(clean1, width = (table_width - column_width) - 5)
            clean_table.append([clean0, wrapped_text[0]])
            for segment in wrapped_text[1:]:
                clean_table.append([" "*column_width, segment])
            clean_table.append(["",""]) # add a blank line between each row for readability
    
    final_table = [
        "```\n",
        f"┌{'─'*(column_width+2)}┬{'─'*((table_width - 3) - column_width)}┐\n",
        *[
            f"├{'─'*(column_width+2)}┼{'─'*((table_width - 3) - column_width)}┤\n" if idx == 1 else "" +
            f"│ {row[0] + ' '*(column_width - len(row[0]))} │ {row[1] + ' '*((table_width - 4) - (len(row[1]) + column_width))}│\n"
            for idx, row in enumerate(clean_table)
        ],
        f"└{'─'*(column_width+2)}┴{'─'*((table_width - 3) - column_width)}┘\n```\n"
    ]
    return final_table
        
# Line formatters

def convert_links(line: str) -> str:
    #Convert "- [label](url)" markdown link lines to "=> url label" gemtext links
    if line.startswith("- ["):
        # strip the first 3 characters "- [" off the line, then break it in half at the ](
        link = line[3:].split("](")
        # Since we have to flip the fields around, we also need to strip the newline and add one at the end.
        return f"=> {link[1].replace(")\n","")} {link[0]}\n"
    return line

def strip_inline_markdown(line: str) -> str:
    #set up a regex method to remove inline markdown
    inline_md_replacements = {"*":"","**":"","***":"","_":"","__":"","___":"",}
    inline_md_pattern = re.compile("|".join(re.escape(old) for old in inline_md_replacements))
    # regex it all out
    return f"{line[0:2]}{inline_md_pattern.sub(lambda match: inline_md_replacements[match.group(0)], line[2:])}"

#Global registers for the iteration logic to use
format_multiline: bool  = False  # switches iteration logic between single and multiple line formatter modes
multiline_buffer: list  = []     # 2D list that's used to buffer multiline formatting
output_doc:       list  = []     # The buffer for the final document

# Main Iterator
# this is the beating heart of this conversion script. it runs through each line and:
# - runs the line through a line-formatting pipeline
# - Pushes multi-line formatting types into a buffer to run through multi-line formatters
for index, line in enumerate(coc):
    line = strip_inline_markdown(line) if config["strip_inline_formatting"] else line
    line = convert_links(line) if config["convert_bullet_point_links"] else line
    if format_multiline:
        if line.startswith("|"): 
            multiline_buffer.append(line)
        else:
            # We're done building the multi-line buffer, format it and push it to the final doc!
            format_multiline = False
            multiline_buffer = format_table(multiline_buffer) if config["format_unicode_tables"] else multiline_buffer
            output_doc += multiline_buffer # append the formatted buffer to the document
            multiline_buffer.clear()
    else:
        if line.startswith("|"):
            format_multiline = True
            multiline_buffer.append(line)
        else:
            output_doc.append(line)
                
# Stripped markdown should now be a valid gemtext document. 
# Combine the processed document with the preformated heading and footings,
# then save it to the coc page!
gemtext = f"{heading}{''.join(output_doc)}{footing}"
#print(gemtext) 
page = open("./allthingslinux.org/code-of-conduct.gmi", "w")
page.write(gemtext)
print("Page generated successfully!")
