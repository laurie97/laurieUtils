#!/usr/bin/env python

####################################
#
# doPlotUtils.py
#
# generic Plotting script, with importable doPlot function
#
# Laurie McClymont - UCL
# Written ~ August 2016
#
###################################

import os, sys, time, argparse, copy, glob
from array import array
from math import sqrt, log, isnan, isinf
from os import path

import ROOT

from ROOT import gROOT, gStyle
gROOT.ProcessLine("gErrorIgnoreLevel > 2000;")
gStyle.SetOptTitle( 0 )

import AtlasStyle
AtlasStyle.SetAtlasStyle()

verbose=False
quiet=False

def root_colours(input):

  if input=='Red':           output=ROOT.kRed
  elif input=='Green':       output=ROOT.kGreen
  elif input=='Yellow':      output=ROOT.kYellow
  elif input=='Blue':        output=ROOT.kBlue
  elif input=='Magenta':     output=ROOT.kMagenta
  elif input=='Cyan':        output=ROOT.kCyan
  elif input=='DarkCyan':    output=ROOT.kCyan+1
  elif input=='DarkGreen':   output=ROOT.kGreen+2
  elif input=='Orange':      output=ROOT.kOrange
  elif input=='Black':       output=ROOT.kBlack
  elif input=='Gray':        output=ROOT.kGray
  elif input=='Grey':        output=ROOT.kGray
  elif input=='White':       output=ROOT.kWhite
  elif input=='DarkGrey':    output=ROOT.kGray+2
  elif input=='Violet':      output=ROOT.kViolet+1
  else:    output=int(input)

  return output

def root_markerStyles(input):

  if input=='Circle':
    output=20
  elif input=='Square':
    output=21
  elif input=='Triangle':
    output=22
  elif input=='circle':
    output=24
  elif input=='square':
    output=25
  elif input=='triangle':
    output=26
  else:
    output=int(input)

  return output

def root_fillStyles(inputRaw):
  
  try:
    input=inputRaw.lower()
  except:
    input=inputRaw
  
  if input=="solid":
    output=1001
  elif input=="heavydots":
    output=3001  
  elif (input=="mediumdots" or input=="dots"):
    output=3002  
  elif input=="lightdots":
    output=3002  
    
  else:
    output=int(inputRaw)

  return output


def getListsFromString(string):

  # Make 2 comma safe
  string.replace(',,',',')
  #print "Doing make string safe"

  Lists = []
  for List in string.split(","):
    Lists.append(List.split(":"))
  return Lists

def getOptionMapFromString(optionString, verbose=False): 

    optionMap={}

    optionLists=getListsFromString(optionString)
    for optionList in optionLists:
      try:
        optionMap[optionList[0]]=optionList[1].replace("\comma",",")
      except:
        raise SystemError("doPlot: optionMap problem, optionList:", optionList)
      if(verbose): print "  ", optionList[0], ":", optionList[1]

    return optionMap


defaultOptionString="Type:Hist,nPads:2,Logx:0,Logy:0,colour:Black,pad1DrawOption:,pad2DrawOption:,atlasLabel:Internal,atlasLabelPos:0.2-0.85,plotStringPos:0.2-0.7-0.9,plotName:test"
defaultOptionString+=",yTitle:Frequency,yTitleSize:0.06,yTitleOffset:1,xTitleSize:0.05,xTitleOffset:0.02"
defaultOptionString+=",ratio_yTitle:Ratio,ratio_yTitleSize:0.13,ratio_yTitleOffset:0.5,ratio_xTitleSize:0.15,ratio_xTitleOffset:0.9"
defaultOptionString+=",ratio_xLabelSize:0.1,ratio_yLabelSize:0.1,ratio_yLabelDivisions:5-0-5"
defaultOptionString+=",pad:1,legendPos:0.6-0.7-0.9-0.9,plotSuffix:pdf-C-png,verbose:0,newRightMargin:1"

if(verbose): print
if(verbose): print "Default Settings for map"
defaultOptionMap=getOptionMapFromString(defaultOptionString)

def getOption(option, optionMap):

    try:
        ret = optionMap[option]
    except:
        try:     ret=defaultOptionMap[option]
        except:  ret = 0

    if ret=="0":  return 0
    return ret

def openHistsAndStrings(histsAndStrings, verbose=False):

  histsAndMaps=[]
  
  for histAndString in histsAndStrings:
    histAndMap=[]
    histAndMap.append(histAndString[0])
    histAndMap.append(getOptionMapFromString(histAndString[1]))
    histsAndMaps.append(histAndMap)

  return histsAndMaps


def setupCanvas(opts):

  ## Setup Canvas ##
  canvName="c"
  canv = ROOT.TCanvas(canvName,canvName,60,50,800,600)
  #canv = ROOT.TCanvas()
  canv.Clear()
  canv.cd()
  
  pad1 = ROOT.TPad("pad1","pad1",0,0.3,1,1)
  pad2 = ROOT.TPad("pad2","pad2",0,0.01,1,0.37)
  if(int(getOption('newRightMargin',opts)) > 0 ):
    pad1.SetRightMargin(0.1)
    pad2.SetRightMargin(0.1)
  pad1.Draw()
  pad2.Draw()
    
  if(getOption('verbose',opts)): print "nPads:", getOption("nPads",opts)

  if int( getOption("nPads",opts) ) > 1:
    pad2.SetTopMargin(0.03)
    pad2.SetBottomMargin(0.35) 
    pad1.Draw()
    pad2.Draw()
    pad2.SetGridx()
    pad2.SetGridy()

  else:
    pad1.SetPad(0,0,1,1)
    pad1.Draw()
  pad1.cd()

  if int(getOption("Logx",opts)) > 0:
    pad1.SetLogx()
    pad2.SetLogx()
    if(getOption('verbose',opts)): print "  Setting Logx"

  if int(getOption("Logy",opts)) > 0:
    pad1.SetLogy()
    if(getOption('verbose',opts)): print "  Setting Logy"

  if int(getOption("Logz",opts)) > 0:
    pad1.SetLogz()
    if(getOption('verbose',opts)): print "  Setting Logz"

  if int(getOption("Gridx",opts)) > 0:
    pad1.SetGridx()
    if(getOption('verbose',opts)): print "  Setting Gridx"

  if int(getOption("Gridy",opts)) > 0:
    pad1.SetGridy()
    if(getOption('verbose',opts)): print "  Setting Gridy"

  if getOption("legend",opts):
    legendPos=getOption("legendPos",opts).split("-")
    legend=ROOT.TLegend( float(legendPos[0]), float(legendPos[1]), float(legendPos[2]), float(legendPos[3]) )
    if getOption("legendFillColour",opts)!=0:
      legend.SetFillColor(int(getOption("legendFillColour",opts)))
    else:
      legend.SetFillStyle(0)
    
    if getOption("legendTextSize",opts)!=0:
      legend.SetTextSize(float(getOption("legendTextSize",opts)))
    else:
      legend.SetTextSize(0.04)

    if getOption("legendColumns",opts):
      legend.SetNColumns(int(getOption("legendColumns",opts)))
    
    opts["legend"]=legend
    if(getOption('verbose',opts)): print " Added a legend"

  return canv, pad1, pad2

def setupHist(histAndMap,opts):

  hist=histAndMap[0]
  map=histAndMap[1]

  if(getOption('verbose',opts)): print
  if(getOption('verbose',opts)): print "Setting options for histMap", hist.GetName()
  
  if( getOption("type",map)=="Function"):
      hist=histAndMap[0].GetHistogram()
  #if( getOption("type",map)=="graph"):
  #    hist=histAndMap[0].GetHistogram()
  
  xRange=getOption("xRange",opts)
  if xRange!=0:
    if ";" in xRange:
      xLow=xRange.split(";")[0]
      xUp=xRange.split(";")[1]
    else:
      xLow=xRange.split("-")[0]
      xUp=xRange.split("-")[1]
    hist.GetXaxis().SetRangeUser( float(xLow), float(xUp) )
    if(getOption('verbose',opts)): print "Setting xRange to be", str(xLow)+"-"+str(xUp)
    
  yRange=getOption("yRange",map)
  if yRange==0:
    yRange=getOption("yRange",opts)    

  if yRange!=0:
    if ";" in yRange:
      yLow=yRange.split(";")[0]
      yUp=yRange.split(";")[1]
    else:
      yLow=yRange.split("-")[0]
      yUp=yRange.split("-")[1]

    if( getOption("type",map)!="graph"):
      hist.GetYaxis().SetRangeUser( float(yLow), float(yUp) )
    else:
      hist.GetHistogram().SetMinimum( float(yLow) )
      hist.GetHistogram().SetMaximum( float(yUp)  )
    if(getOption('verbose',opts)): print "Setting yRange to be", yRange

  elif (int(getOption("Logy",opts)) > 0) and (int( getOption("pad",map) )==1):
    yLow=max(0.5,hist.GetMinimum()/20)
    yUp=hist.GetMaximum()*100
    hist.GetYaxis().SetRangeUser( float(yLow), float(yUp) )
    if(getOption('verbose',opts)): print "Setting yRange to be", str(yLow)+"-"+str(yUp)

  hist.SetLineColor( root_colours(getOption("colour",map) ) )
  hist.SetMarkerColor( root_colours(getOption("colour",map) ) )
  hist.SetMarkerStyle(root_markerStyles(getOption("markerStyle",map) ) )
  if getOption("fillColour",map): fillColour=root_colours(getOption("fillColour",map) )                                                    
  else:                           fillColour=root_colours(getOption("colour",map) )
  hist.SetFillColor(fillColour)
  hist.SetFillStyle( root_fillStyles(getOption("fillStyle",map) ) )
  
  if(getOption('verbose',opts)): print "Setting colour to ", getOption("colour",map)
  if(getOption('verbose',opts)): print "Setting fillColour to ", fillColour
  if(getOption('verbose',opts)): print "Setting markerStyle to ", getOption("markerStyle",map)
  if(getOption('verbose',opts)): print "Setting fillStyle to ", getOption("fillStyle",map)
  ##print "=> hist.SetFillStyle("+str(root_fillStyles(getOption("fillStyle",map) ) )+"), from "+str(getOption("fillStyle",map))
  
  # Check if first histogram for pad
  if int( getOption("pad",map) )==1:
    drawOption=getOption("pad1DrawOption",opts)
    pad=""
  elif int( getOption("pad",map) )==2:
    drawOption=getOption("pad2DrawOption",opts)
    pad="ratio_"

  #If first histogram
  if "same" not in drawOption:

    hist.GetXaxis().SetMoreLogLabels() # Always
    
    #Set Titles
    if  getOption("yTitle",map) != "Frequency" and getOption("yTitle",map) != 0:
      hist.GetYaxis().SetTitle(getOption("yTitle",map))    
    elif getOption(pad+"yTitle",opts) != 0:
      hist.GetYaxis().SetTitle(getOption(pad+"yTitle",opts))
    if ( int(getOption("nPads",opts)) == int( getOption("pad",map) )): 
      if getOption("xTitle",opts)!=0:
        hist.GetXaxis().SetTitle(getOption("xTitle",opts))
        if(getOption('verbose',opts)): print "xTitle:", getOption("xTitle",opts), "in pad",getOption("pad",map)

    #if getOption(pad+"xTitle",opts)!=0:
    #  hist.GetXaxis().SetTitle(getOption(pad+"xTitle",opts))

    if getOption(pad+"yTitleSize",opts)!=0:
      hist.GetYaxis().SetTitleSize(float(getOption(pad+"yTitleSize",opts)))
    if getOption(pad+"xTitleSize",opts)!=0:
      hist.GetXaxis().SetTitleSize(float(getOption(pad+"xTitleSize",opts)))

    if getOption(pad+"yTitleOffset",opts)!=0:
      hist.GetYaxis().SetTitleOffset(float(getOption(pad+"yTitleOffset",opts)))
    if getOption(pad+"xTitleOffset",opts)!=0:
      hist.GetXaxis().SetTitleOffset(float(getOption(pad+"xTitleOffset",opts)))

    #Set for labels
    if getOption(pad+"yLabelSize",opts)!=0:
      hist.GetYaxis().SetLabelSize(float(getOption(pad+"yLabelSize",opts)))
    if getOption(pad+"xLabelSize",opts)!=0:
      hist.GetXaxis().SetLabelSize(float(getOption(pad+"xLabelSize",opts)))

    if getOption(pad+"yLabelOffset",opts)!=0:
      hist.GetYaxis().SetLabelOffset(float(getOption(pad+"yLabelOffset",opts)))
    if getOption(pad+"xLabelOffset",opts)!=0:
      hist.GetXaxis().SetLabelOffset(float(getOption(pad+"xLabelOffset",opts)))

    if getOption(pad+"yLabelDivisions",opts)!=0:
      ndivisions=getOption(pad+"yLabelDivisions",opts).split('-')
      hist.GetYaxis().SetNdivisions(int(ndivisions[0]),int(ndivisions[1]),int(ndivisions[2]))
    if getOption(pad+"xLabelDivisions",opts)!=0:
      ndivisions=getOption(pad+"xLabelDivisions",opts).split('-')
      hist.GetXaxis().SetNdivisions(int(ndivisions[0]),int(ndivisions[1]),int(ndivisions[2]))

      
        
  histAndMap[0]=hist


def drawHist(histAndMap,opts,pad1,pad2):

  hist=histAndMap[0]
  map=histAndMap[1]

  drawOption=""
        
  if int( getOption("pad",map) )==1:
    drawOption=getOption("pad1DrawOption",opts)
    opts["pad1DrawOption"]="same"
    pad1.cd()

  elif int( getOption("pad",map) )==2:
    drawOption=getOption("pad2DrawOption",opts)
    opts["pad2DrawOption"]="same"
    pad2.cd()

  else:
    if(getOption('verbose',opts)): print "Don't know which pad to put", hist.GetName()
    return

  if getOption("drawOption",map):
    drawOption+=getOption("drawOption",map)
  
  hist.Draw(drawOption)
  
  ############
  ##Add to legend
  legOption="epl"
  if getOption("fillStyle",map):
    legOption="fepl"

  if getOption("legend",opts) and getOption("legend",map):
    opts["legend"].AddEntry(hist, getOption("legend",map), legOption)
    if(getOption('verbose',opts)): print " Added to legend"
    
  histAndMap[1]=map

  if(getOption('verbose',opts)): print "  Drawn hist", hist.GetName(), "with drawOption", drawOption, "in pad", int( getOption("pad",map) )
  return

def finaliseCanvas(opts, canv, pad1, pad2):

  pad1.cd()
  if(getOption('verbose',opts)): print "Let's do finalise canvas"
  if getOption("atlasLabel",opts)!=0:
    labelPosX=float(getOption("atlasLabelPos",opts).split('-')[0])
    labelPosY=float(getOption("atlasLabelPos",opts).split('-')[1])
    if(getOption('verbose',opts)): print "labelPos ",labelPosX, labelPosY
    AtlasStyle.ATLAS_LABEL(labelPosX,labelPosY, 1, getOption("atlasLabel",opts))
    AtlasStyle.myText(labelPosX,(labelPosY-0.05),1,"#scale[0.9]{#sqrt{s} = 13 TeV}");
    if getOption("lumi",opts)!=0:
      #AtlasStyle.myText(labelPosX,(labelPosY-0.12),1,"#scale[0.9]{#int L dt = "+args.lumi+ " fb^{-1}}")
      if("24.5" in getOption("lumi",opts)): print " doPlot: Doing low mass lumi fix (24.5 -> 24.3)"
      lumi=getOption("lumi",opts).replace("24.5","24.3")
      AtlasStyle.myText(labelPosX,(labelPosY-0.1),1,"#scale[0.9]{"+lumi+" fb^{-1}}");

  gStyle.SetOptStat(0)
  legend=getOption("legend",opts)
  if legend:
    legend.Draw()

  #Add a string to the plot
  plotString=getOption("plotString",opts)
  if(getOption('verbose',opts)): print "plotString is", plotString
  if plotString!=0:
    plotStringList= plotString.split('+')
    plotStringPos=getOption("plotStringPos",opts).split('-')
    yPos = float(plotStringPos[1])  # Init position of y
    for string in plotStringList:
      #print "AtlasStyle.myText(0.65,",yPos,",1,","#scale[0.9]{"+string+"}",")"
      if(getOption('verbose',opts)): print "  -",string
      AtlasStyle.myText(float(plotStringPos[0]),yPos,1,"#scale["+plotStringPos[2]+"]{"+string+"}")
      yPos=yPos-0.05
      


def doPlot( histsAndStrings, optionString):

  verbose=False
  if("verbose:" in optionString): verbose=True
  
  #getDefault()
  if verbose: print
  if verbose: print " ******************  do Plot  **********************"

 
  if verbose: print "Getting histsAndStrings"
  histsAndMaps = openHistsAndStrings(histsAndStrings , verbose )
  
  if verbose: print "Getting general options"
  opts=getOptionMapFromString(optionString, verbose )

  (canv, pad1, pad2) = setupCanvas(opts)

  # Loop over hists
  for histAndMap in histsAndMaps:
    #Setup Hist
    setupHist(histAndMap,opts)

    #Draw Hist
    drawHist(histAndMap,opts,pad1,pad2)

  # Finalise Canvas (add text to plots, legends ect...)
  finaliseCanvas(opts, canv, pad1, pad2)

  # Create directory for plot if not already done
  plotDirName=getOption("plotName",opts).rsplit('/', 1)[0]
  if not os.path.isdir(plotDirName):
    os.makedirs(plotDirName)
  
  # Print Canvas
  suffixList=getOption("plotSuffix",opts).split("-")
  for suffix in suffixList:
    canv.Print(getOption("plotName",opts)+"."+suffix)
  print "  doPlot prints to "+getOption("plotName",opts)+"."+suffixList[0]
  if verbose: print " ****************************************************"
  
  

def main():

  print "Hello"
  
  histsAndStrings=[]

  optionString="Logx:0,nPads:2,plotString:Testing+Testing2,lumi:12,legend:YesPlease"

  file=ROOT.TFile.Open("Systematics2016/BJetTrig-00-03-05_full/BJetTriggerEfficiencies.root", "READ")
  print "****", file.GetName()
  testHist1=file.Get("eff_MC_offJets70_match_hlt70_jetPt")
  testHist2=file.Get("eff_Data_offJets70_match_hlt70_jetPt")

  print "****", testHist1.GetName()
  print "****", testHist2.GetName()

  histsAndStrings=[ [testHist1,"yRange:0-2,markerStyle:Circle,pad:1,legend:test1"], [testHist2,"colour:Red,pad:2,legend:test2"] ]

  doPlot(histsAndStrings,optionString)


if __name__ == "__main__":
  main()
  print "Done"
