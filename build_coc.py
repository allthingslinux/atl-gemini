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

# width of the table in columns
table_width: int = 80

pipeline_config: dict = { 
    "strip_inline_formatting": True,
    "convert_bullet_point_links": True,
    "format_unicode_tables": True,
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

#TODO: re-write the table parser/formatter to make use of the pipeline approach rather than doing *this*
def format_table(table: list, coc: list) -> None:
    clean_table = []
    column_width = max(len(column.strip()) for column in current_table[0])
    for x, y in enumerate(current_table):               # strips the seperating line 
        if not all( char == '-' for char in y[0]):      # Check if first column of row is all dashes. if it is, it's a seperator row and should be discarded.
            clean0 = y[0].strip() # Generate cleaned version of columns 0 and 1
            clean1 = y[1].strip()
            wrapped_text = textwrap.wrap(clean1, width = (table_width - column_width) - 5)
            clean_table.append([clean0, wrapped_text[0]])
            for segment in wrapped_text[1:]:
                clean_table.append([" "*column_width, segment])
            clean_table.append(["",""]) # add a blank line between each row for readability
    current_table.clear() # we don't need the original table buffer anymore now that we've generated clean_table.
    print(f"first column width: {str(column_width)}")
    print(f"table get!\n {str(clean_table)}")
    # Push our work into the final generated document. this looks ugly, and admittedly it really is.
    # we're hardcoding the box characters and widths. we pulled the width of the first column earlier, so we use that
    # to do math to decide where to place the table lines. string multiplation is used to place the lines down.
    # Because of the direction the entry we inserted gets pushed when we insert another one, we have to put the table together from botton to top.
    coc.insert(table_start_index, "```\n")
    coc.insert(table_start_index, f"└{("─"*(column_width+2))}┴{("─"*((table_width - 3 )-column_width))}┘\n")
    clean_table.reverse() # The list is ordered for drawing top-to-bottom. we need to change that.
    for idx, row in enumerate(clean_table): # draw in the actual table data.
        if idx == len(clean_table)-1:
            coc.insert(table_start_index, f"├{("─"*(column_width+2))}┼{("─"*((table_width - 3) - column_width))}┤\n")
        coc.insert(table_start_index, f"│ {row[0]+(" "*(column_width-len(row[0])))} │ {row[1]+(" "*((table_width - 4) - (len(row[1])+column_width)))}│\n")
    coc.insert(table_start_index, f"┌{("─"*(column_width+2))}┬{("─"*((table_width - 3) - column_width))}┐\n")
    coc.insert(table_start_index, "```\n")

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
in_table = False        # switches iteration logic between normal and table modes
current_table = []      # 2D list that's used to buffer the table data as it comes in
table_start_index = 0   # point to delete from and then insert the new formatted table

# Main Iterator
# this is the beating heart of this conversion script. it runs through each line and:
# - runs the line through a line-formatting pipeline
# - Pushes multi-line formatting types into a buffer to run through multi-line formatters

for index, line in enumerate(coc):
    line = strip_inline_markdown(line) if pipeline_config["strip_inline_formatting"] else line
    line = convert_links(line) if pipeline_config["convert_bullet_point_links"] else line
    if in_table:
        if line.startswith("|"): #if we're still in the table, move this line into the table buffer and iterate to the next.
            #strip inline markdown and the beginning of the table ("| ") from the line
            current_table.append(line[2:len(line)-2].split(" | "))
        else:
            # We have the whole table! all done iterating!
            in_table = False
            # Remove the unformatted section from the document. the formatter will reinsert it at the end.
            del coc[table_start_index:(table_start_index+len(current_table))]   
            format_table(current_table, coc)
    else:
        if line.startswith("|"):
            #activate the table parser, push first line into the table buffer
            in_table =           True
            table_start_index =  index
            current_table.append(line[2:len(line)-2].split(" | "))
        coc[index] = line
                
# Stripped markdown should now be a valid gemtext document. 
# Combine the processed document with the preformated heading and footings,
# then save it to the coc page!
gemtext = f"{heading}{''.join(coc)}{footing}"
#print(gemtext) 
page = open("./allthingslinux.org/code-of-conduct.gmi", "w")
page.write(gemtext)
print("Page generated successfully!")
