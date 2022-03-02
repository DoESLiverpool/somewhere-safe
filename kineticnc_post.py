# ***************************************************************************
# *   (c) Julian Todd (julian@goatchurch.org.uk) 2018                       *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************/
from __future__ import print_function
import FreeCAD
import Path
from PathScripts import PostUtils
from PathScripts import PathUtils

TOOLTIP = '''
Structured post-processor for development for KinetiC-NC CNC machine 
https://github.com/DoESLiverpool/somebody-should/wiki/CNC-Router
'''


#
# Functions to preprocess the incoming FreeCAD object into a new list:
# of form: [ ({tooldef}, [motion cmds]) ]
#     where:   tooldef = { Diameter, S, T, firstpos:{X, Y, Z, F}, lastpos:{X, Y, Z, F} }
#

import re

# iterates down the groupd and concatenates the path objects to create a list of cmd objects
def flattenobjectlisttocommands(objectslist):
    cmds = [ ]
    robjectstack = list(reversed(objectslist))
    while robjectstack:
        pathobj = robjectstack.pop()
        if hasattr(pathobj, "Group"):
            robjectstack.extend(reversed(pathobj.Group))
        elif hasattr(pathobj, "Path"):
            cmds.extend(pathobj.Path.Commands)
    return cmds

# regroup sequences of pure motion or drill cycle in between tool change definition commands
motionsequencename = set(["G0", "G1", "G2", "G3", "G90", "G98", "G83", "G80"])
def findmotionsequenceindexes(cmds):
    imotionsequences = [ ]
    for i, cmd in enumerate(cmds):
        if cmd.Name in motionsequencename:
            if not imotionsequences or imotionsequences[-1][1] != i-1:
                imotionsequences.append([i, i])
            else:
                imotionsequences[-1][1] = i
    return imotionsequences

# merge a series of tool definition commands into a single object
def extracttooldef(cmds, motioncmds):
    tooldef = { }
    for cmd in cmds:
        if cmd.Name in ["M6", "M3"]:
            tooldef.update(cmd.Parameters)
        else:
            commentparams = re.findall("(Diameter): ([\d\.]+)", cmd.Name)
            tooldef.update(dict(commentparams))
            
    smotioncmds = set(cmd.Name  for cmd in motioncmds)
    if "G83" in smotioncmds:
        tooldef["cycletype"] = "drill" if "G1" not in smotioncmds else "mixed"
    else:
        tooldef["cycletype"] = "normal"
        
    return tooldef

def extractfirstpos(cmds):
    pos = { }
    for cmd in cmds:
        for w in "XYZF":  # includes feedrate
            if w not in pos and w in cmd.Parameters:
                if not (w == "F" and cmd.Parameters[w] == 0):
                    pos[w] = cmd.Parameters[w]
        if len(pos) == 4:
            break
    return pos

# returns [ ({tooldef}, [motion cmds]) ]
#     where tooldef = { i, T, S, Diameter, prevpos:{XYZ}, firstpos:{XYZ}, firstpos:{XYZ}, cycletype:{normal,drill} }
def flattenandgroup(postlist):
    cmds = flattenobjectlisttocommands(postlist)
    imotionsequences = findmotionsequenceindexes(cmds)
    tooldefmotions = [ ]
    prevb = -1
    for a, b in imotionsequences:
        motioncmds = cmds[a:b+1]
        tooldef = extracttooldef(cmds[prevb+1:a], motioncmds)
        tooldef["firstpos"] = extractfirstpos(motioncmds)
        tooldef["lastpos"] = extractfirstpos(reversed(motioncmds))
        if tooldefmotions:
            tooldef["prevpos"] = tooldefmotions[-1][0]["lastpos"]
            
        if tooldef["cycletype"] == "drill":
            tooldefmotions.append((tooldef, [cmd  for cmd in motioncmds  if cmd.Name == "G83"]))
        elif len(tooldef["firstpos"]) == 4: # includes F as well as XYZ
            tooldefmotions.append((tooldef, motioncmds))
        else:
            print(" fail to add toolmotions between", a, b, "for tooldef", tooldef)
            if "F" not in tooldef["firstpos"]:
                print("is it missing feedrate F?")
        prevb = b  

    return tooldefmotions
    

#
# Main three functions that make up the core of this post processor
#
#
import datetime
def writetooldefheader(fout, tooldef, i, currpos):
    if i == 0:  # first entry
        fout.write("%\n")
        fout.write("(Start %s)\n" % tooldef["filename"])
        fout.write("(Exported by FreeCAD)\n")
        fout.write("(Post Processor: %s)\n" % __name__)
        fout.write("(Output Time: %s)\n" % str(datetime.datetime.now()))
        fout.write("G90 (Absolute coordinates)\n")
        fout.write("G17 (XY Plane selection)\n")
        fout.write("G21 (Programming in mm)\n")
        fout.write("G94 (Feedrate per minute)\n")
    fout.write("\n")
    fout.write("(Diameter: %s)\n" % tooldef.get("Diameter", "unknown"))
    fout.write("M6 T%d (Change tool)\n" % tooldef.get("T", 0))
    fout.write("M3 S%d (Spindle on)\n" % tooldef.get("S", 0))
    
    # insert the retract and clearance plane motion explicitly 
    currpos.update(tooldef["firstpos"])
    fout.write("G0 Z%.3f (To clearance plane)\n" % (currpos["Z"]))
    fout.write("G0 X%.3f Y%.3f\n" % (currpos["X"], currpos["Y"]))
    Fentry = tooldef["firstpos"].get("F", 0)
    if Fentry != 0:
        currpos["F"] = Fentry
        fout.write("G1 Z%.3f F%d (Set feedrate on spot)\n" % (currpos["Z"], currpos["F"]))
        currpos["Name"] = "G1"
    else:
        currpos["Name"] = "G0"
	

def writemotioncmds(fout, motioncmds, currpos):
    for cmd in motioncmds:
        fline = [ ]
        if cmd.Name != currpos.get("Name") or cmd.Name in ["G2", "G3"]:
            fline.append("%s " % cmd.Name)
            currpos["Name"] = cmd.Name
            
        for w in "XYZcF":
            if w == "c":
                if cmd.Name in ["G2", "G3"]:
                    fline.append("I%.3f J%.3f " % (cmd.Parameters["I"], cmd.Parameters["J"]))
            elif w in cmd.Parameters and cmd.Parameters[w] != currpos.get(w):
                if not (w == "F" and cmd.Parameters[w] == 0 and cmd.Name == "G0"):  # F0 happens on G0s
                    fline.append("%s%.3f " % (w, cmd.Parameters[w]))
                    currpos[w] = cmd.Parameters[w]
                
        if fline:
            fout.write("%s\n" % "".join(fline))

def writedrillmotioncmds(fout, drillcmds, currpos):
    for cmd in drillcmds:
        fline = [ ]
        assert cmd.Name == "G83"
        fline.append("%s " % cmd.Name)
        currpos["Name"] = cmd.Name
        for w in "QRXYZ":
            fline.append("%s%.3f " % (w, cmd.Parameters[w]))
            currpos[w] = cmd.Parameters[w]
        fout.write("%s\n" % "".join(fline))
    fout.write("G80\n")

def writefilefooter(fout, currpos):
    fout.write("M5 (Spindle off)\n")
    fout.write("M30 (End of program)\n")
    fout.write("%")
    

#
# The entry point function that:
#    (1) Calls the regrouping code, 
#    (2) Calls the three core functions, and 
#    (3) saves the file after popping up an editor
#
#
from io import StringIO
def export(objectslist, filename, argstring):
    print("postprocessing...")
    
    tooldefmotions = flattenandgroup(objectslist)
    if tooldefmotions:
        tooldefmotions[0][0]["filename"] = filename

    fout = StringIO()
    currpos = {}
    for i, (tooldef, motioncmds) in enumerate(tooldefmotions):
        print("block", i, "cycletype", tooldef["cycletype"], "num_motioncommands", len(motioncmds))
        writetooldefheader(fout, tooldef, i, currpos)
        if tooldef["cycletype"] == "drill": 
            writedrillmotioncmds(fout, motioncmds, currpos)
        else:
            writemotioncmds(fout, motioncmds, currpos)
    writefilefooter(fout, currpos)

    gcode = fout.getvalue()
    if FreeCAD.GuiUp: 
        dia = PostUtils.GCodeEditorDialog()
        dia.editor.setText(fout.getvalue())
        result = dia.exec_()
        if result:
            gcode = dia.editor.toPlainText()
    print("done postprocessing.")

    if filename != '-':
        gfile = open(filename, "w")
        gfile.write(gcode)
        gfile.close()
        

print(__name__ + " gcode postprocessor V4 loaded.")





#
# Useful functions to keep safe for when running posts outside of FreeCAD
#
"""import sys
freecadpath = "/home/julian/extrepositories/FreeCAD/freecad-build/lib"
sys.path.append(freecadpath)
import FreeCAD
import PathScripts.PathJob as PathJob
import PathScripts.PathLog as PathLog
import PathScripts.PathToolController as PathToolController
import PathScripts.PathUtil as PathUtil
"""

def extractpostlistfromfile(fname):
    doc = FreeCAD.open(fname)
    #jobs = [o  for o in FreeCAD.ActiveDocument.Objects  if hasattr(o, "Proxy") and isinstance(o.Proxy, PathJob.ObjectJob)]
    job = doc.getObject("Job")
    postlist = []
    currTool = None
    for obj in job.Operations.Group:
        PathLog.debug("obj: {}".format(obj.Name))
        tc = PathUtil.toolControllerForOp(obj)
        if tc is not None:
            if tc.ToolNumber != currTool:
                postlist.append(tc)
                currTool = tc.ToolNumber
        postlist.append(obj)
    return postlist
