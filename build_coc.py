from copyreg import clear_extension_cache
import re
import textwrap

heading=[
r'```'+"\n"
r'  _____        __      ____  ___  _____             __         __ '+"\n"
r' / ___/__  ___/ /__   / __ \/ _/ / ___/__  ___  ___/ /_ ______/ /_'+"\n"
r'/ /__/ _ \/ _  / -_) / /_/ / _/ / /__/ _ \/ _ \/ _  / // / __/ __/'+"\n"
r'\___/\___/\_,_/\__/  \____/_/   \___/\___/_//_/\_,_/\_,_/\__/\__/ '+"\n"
r'```'+"\n"
]
footing=[
    r'## Contributors'+"\n"
    r'=> https://contrib.rocks Made with contrib.rocks'+"\n"
    r'=> https://contrib.rocks/image?repo=allthingslinux/code-of-conduct Contributors'+"\n"
]
coc = open("./code-of-conduct/README.md").read().splitlines(True)

# Find the end of the table of contents and delete everything up to that point
tocend = coc.index("<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n") + 2
print("end of TOC found at line "+str(tocend)+", stripping toc and header")
del coc[0:tocend]

# Find the beginning of the contributors section and chop it off
contribstart = coc.index("## Contributors\n")
print("Contributor block found at line "+str(contribstart)+", stripping out footing")
del coc[contribstart:]

#set up a regex method to kill inline markdown
replacements = {"*":"","**":"","***":"","_":"","__":"","___":"",}
pattern = re.compile("|".join(re.escape(old) for old in replacements))

#Global registers for the iteration logic to use
in_table = False        # switches iteration logic between normal and table modes
current_table = []      # 2D list that's used to buffer the table data as it comes in
table_start_index = 0   # point to delete from and then insert the new formatted table
# Main recursive modifier. reformats single-line links and strips out inline formatting.
for index, line in enumerate(coc):
    if in_table:
        if line.startswith("|"):
            cleanline = line[0:2]+pattern.sub(lambda match: replacements[match.group(0)], line[2:])
            current_table.append(cleanline[2:len(cleanline)-2].split(" | "))
        else:
            # We have the whole table! all done iterating!
            in_table = False
            del coc[table_start_index:(table_start_index+len(current_table))]   # Remove this section from the document
            clean_table = []
            column_width = max(len(column.strip()) for column in current_table[0])
            for x, y in enumerate(current_table):               # strips the seperating line 
                if not all( char == '-' for char in y[0]):      # Check if first column of row is all dashes. strip row if yes.
                    clean0 = y[0].strip() # Generate cleaned version of columns 0 and 1
                    clean1 = y[1].strip()
                    if len(clean1) > 75-column_width:
                        wrapped_text = textwrap.wrap(clean1, width=60)
                        clean_table.append([clean0, wrapped_text[0]])
                        for segment in wrapped_text[1:]:
                            clean_table.append([" "*column_width, segment])
                    else:
                        clean_table.append([clean0, clean1])
                    clean_table.append(["",""])
            current_table.clear()
            print("first column width: "+str(column_width))
            print("table get!\n "+str(clean_table))
            coc.insert(table_start_index, "```\n")
            coc.insert(table_start_index, "└"+("─"*(column_width+2))+"┴"+("─"*(76-column_width))+"┘\n")
            clean_table.reverse()
            for idx, row in enumerate(clean_table):
                if idx == len(clean_table)-1:        
                    coc.insert(table_start_index, "├"+("─"*(column_width+2))+"┼"+("─"*(76-column_width))+"┤\n")
                coc.insert(table_start_index, "│ "+row[0]+(" "*(column_width-len(row[0])))+" │ "+row[1]+(" "*(75-(len(row[1])+column_width)))+"│\n")    
            coc.insert(table_start_index, "┌"+("─"*(column_width+2))+"┬"+("─"*(76-column_width))+"┐\n")
            coc.insert(table_start_index, "```\n")
    else:    
        #Convert "- [label](url)" markdown link lines to "=> url label" gemtext links
        if line.startswith("- ["):
            link = line[1:].split("](")
            coc[index] = '=> '+link[1].replace(")\n","")+' '+link[0].replace("- [","")+'\n'
            print("Converting bullet-point-link to gemini link on line "+str(index)+":"+coc[index])
        elif line.startswith("|"):
            #activate the table parser, push first line into the table buffer
            in_table =           True
            table_start_index =  index
            cleanline = line[0:2]+pattern.sub(lambda match: replacements[match.group(0)], line[2:])
            current_table.append(cleanline[2:len(cleanline)-2].split(" | "))
        # If it's not a link, regex out all the inline mardown formatting
        else:
            print("stripping inline formatting from line "+str(index)+":")
            coc[index] = line[0:2]+pattern.sub(lambda match: replacements[match.group(0)], line[2:])
            print(line)

#TODO: Parse out tables, convert them to box-drawing ascii art

# Stripped markdown should now be a valid gemtext document. 
# Combine the processed document with the preformated heading and footings,
# then save it to the coc page!
gemtext = "".join(heading+coc+footing)
#print(gemtext) 
page = open("./allthingslinux.org/code-of-conduct.gmi", "w")
page.write(gemtext)    