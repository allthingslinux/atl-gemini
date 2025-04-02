import re

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

# Main recursive modifier. reformats single-line links and strips out inline formatting.
for index, line in enumerate(coc):
    #Convert "- [label](url)" markdown link lines to "=> url label" gemtext links
    if line.startswith("- ["):
        link = line.split("](")
        coc[index] = '=> '+link[1].replace(")\n","")+' '+link[0].replace("- [","")+'\n'
        print("Converting bullet-point-link to gemini link on line "+str(index)+":"+coc[index])
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
print(gemtext) 
page = open("./allthingslinux.org/code-of-conduct.gmi", "w")
page.write(gemtext)    